import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from flask import (
    Flask,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user, confirm_login
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import DevelopmentConfig
from decorators import roles_required
from extension import db, init_extensions, login_manager
from forms import (
    AccountUpdateForm,
    AdminPasswordResetForm,
    AdminUserEditForm,
    ForgotPasswordForm,
    LoginForm,
    RegistrationForm,
)
from models import (
    Admin,
    Customer,
    Order,
    OrderItem,
    OrderStatusHistory,
    PasswordResetRequest,
    PrintJob,
    Quote,
    QuoteItem,
    Review,
    ServicePrice,
    Vendor,
    USER_MODELS,
    find_user_by_email,
    load_user_from_identity,
)
from sqlalchemy.exc import OperationalError


def create_app(config_class: type[DevelopmentConfig] | None = None):
    app = Flask(__name__)
    app.config.from_object(config_class or DevelopmentConfig)
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    init_extensions(app)
    
    # Configure Flask-Login
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"  # Prevent session hijacking
    login_manager.user_loader(load_user_from_identity)

    register_routes(app)

    with app.app_context():
        db.create_all()
        seed_admin()

    return app


def register_routes(app: Flask):
    @app.context_processor
    def inject_helpers():
        dashboard_link = url_for("dashboard") if current_user.is_authenticated else None
        account_url = (
            url_for("edit_account")
            if current_user.is_authenticated and current_user.user_type in {"customer", "vendor"}
            else None
        )
        return {
            "dashboard_url": dashboard_link,
            "account_settings_url": account_url,
        }

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/vendors")
    def vendors():
        return render_template("vendors.html")

    @app.route("/features")
    def features():
        return render_template("features.html")

    @app.route("/how-it-works")
    def how_it_works():
        return render_template("how_it_works.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = RegistrationForm()
        if not form.user_type.data:
            form.user_type.data = form.user_type.choices[0][0]
        if form.validate_on_submit():
            try:
                user = form.to_model()
                user.password_hash = generate_password_hash(form.password.data.strip())
                db.session.add(user)
                db.session.commit()

                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Signup error: {str(e)}")
                flash("An error occurred during registration. Please try again.", "error")

        return render_template("signup.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = LoginForm()
        if form.validate_on_submit():
            user = find_user_by_email(form.email.data.lower())
            if user and check_password_hash(user.password_hash, form.password.data):
                # Check if user account is active
                if not user.is_active:
                    flash("Your account has been deactivated. Please contact support.", "error")
                    return render_template("login.html", form=form)
                
                # Clear any existing session data to prevent session fixation
                session.clear()
                
                # Login user with remember me option
                login_user(user, remember=form.remember.data)
                
                # Mark session as fresh for security-sensitive operations
                session.permanent = True
                
                flash(f"Welcome back, {user.full_name.split()[0]}!", "success")
                
                # Redirect to next page if specified, otherwise dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for("dashboard"))

            flash("Invalid email or password.", "error")

        return render_template("login.html", form=form)

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            user = form.user
            pending = PasswordResetRequest.query.filter_by(user_id=user.id, status="pending").first()
            if pending:
                flash("You already have a pending reset request. Our admin team will contact you soon.", "info")
            else:
                reset_request = PasswordResetRequest(
                    user_id=user.id,
                    user_type=user.user_type,
                    email=user.email,
                )
                db.session.add(reset_request)
                db.session.commit()
                flash("Password reset request sent to the admin team. They'll update your password shortly.", "success")
                return redirect(url_for("login"))

        return render_template("forgotpassword.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        # Store user name before logging out
        user_name = current_user.full_name.split()[0] if current_user.is_authenticated else None
        
        # Logout user (clears Flask-Login session)
        logout_user()
        
        # Clear all session data to prevent any session leakage
        session.clear()
        
        # Flash message with user name if available
        if user_name:
            flash(f"Goodbye, {user_name}! You have been logged out.", "info")
        else:
            flash("You have been logged out.", "info")
        
        # Redirect to home page instead of login
        return redirect(url_for("home"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        from flask_wtf import FlaskForm
        
        template = {
            "customer": "user/userdash.html",
            "vendor": "vendor/vendordash.html",
            "admin": "admin/admindash.html",
        }.get(current_user.user_type)

        if not template:
            flash("Unknown user type.", "error")
            return redirect(url_for("login"))

        # Create a form for CSRF token
        form = FlaskForm()
        
        extra_context = {"form": form}
        if current_user.user_type == "admin":
            extra_context["user_counts"] = {
                "customers": Customer.query.count(),
                "vendors": Vendor.query.count(),
                "admins": Admin.query.count(),
            }
            extra_context["pending_reset_count"] = PasswordResetRequest.query.filter_by(status="pending").count()
        elif current_user.user_type == "customer":
            # Load customer's orders
            extra_context["orders"] = Order.query.filter_by(
                customer_id=current_user.id
            ).order_by(Order.created_at.desc()).all()
        elif current_user.user_type == "vendor":
            from sqlalchemy import func, extract, or_
            
            # Get vendor's service categories
            vendor_services = []
            if current_user.service_document_printing:
                vendor_services.append("Document Printing")
            if current_user.service_photos:
                vendor_services.append("Photo Printing")
            if current_user.service_uniforms:
                vendor_services.append("Uniforms & Apparel")
            if current_user.service_merchandise:
                vendor_services.append("Merchandise")
            if current_user.service_large_format:
                vendor_services.append("Large Format")
            
            # Get orders matching vendor's services that are open for quotes
            available_orders = Order.query.filter(
                Order.service_category.in_(vendor_services),
                Order.status.in_(["pending", "awaiting_quotes", "quoted"])
            ).order_by(Order.created_at.desc()).all()
            
            # Get orders where this vendor has submitted quotes
            my_quoted_orders = Order.query.join(Quote).filter(
                Quote.vendor_id == current_user.id,
                Order.status.in_(["awaiting_quotes", "quoted"]),
                Order.vendor_id == None  # Not yet assigned to any vendor
            ).distinct().order_by(Order.created_at.desc()).all()
            
            # Get orders assigned to this vendor
            assigned_orders = Order.query.filter_by(
                vendor_id=current_user.id
            ).filter(Order.status.in_(["accepted", "in_progress", "confirmed_received", "processing", "finished", "quality_check", "ready_dispatch", "dispatched", "awaiting_payment"])).order_by(
                Order.accepted_at.desc()
            ).all()
            
            completed_orders = Order.query.filter_by(
                vendor_id=current_user.id, status="completed"
            ).order_by(Order.completed_at.desc()).limit(20).all()
            
            # Calculate statistics
            current_month = datetime.now().month
            current_year = datetime.now().year
            completed_this_month = Order.query.filter_by(
                vendor_id=current_user.id, status="completed"
            ).filter(
                extract('month', Order.completed_at) == current_month,
                extract('year', Order.completed_at) == current_year
            ).count()
            
            # Calculate average rating
            avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
                vendor_id=current_user.id
            ).scalar()
            
            extra_context.update({
                "available_orders": available_orders,
                "my_quoted_orders": my_quoted_orders,
                "assigned_orders": assigned_orders,
                "completed_orders": completed_orders,
                "stats": {
                    "available": len(available_orders),
                    "my_quotes": len(my_quoted_orders),
                    "assigned": len(assigned_orders),
                    "completed_this_month": completed_this_month,
                    "average_rating": avg_rating or 0
                }
            })
        else:
            # Default for other types
            extra_context["orders"] = []

        return render_template(template, user=current_user, **extra_context)

    @app.route("/admin/overview")
    @roles_required("admin")
    def admin_overview():
        user_counts = {
            "customers": Customer.query.count(),
            "vendors": Vendor.query.count(),
            "admins": Admin.query.count(),
        }
        pending_reset_count = PasswordResetRequest.query.filter_by(status="pending").count()
        return render_template(
            "admin/admindash.html",
            user=current_user,
            user_counts=user_counts,
            pending_reset_count=pending_reset_count,
        )

    @app.route("/admin/users")
    @roles_required("admin")
    def admin_users():
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
        vendors = Vendor.query.order_by(Vendor.created_at.desc()).all()
        admins = Admin.query.order_by(Admin.created_at.desc()).all()

        user_counts = {
            "customers": len(customers),
            "vendors": len(vendors),
            "admins": len(admins),
        }

        return render_template(
            "admin/usermanagement.html",
            customers=customers,
            vendors=vendors,
            admins=admins,
            user_counts=user_counts,
        )

    @app.route("/admin/users/<string:user_type>/<int:user_id>/edit", methods=["GET", "POST"])
    @roles_required("admin")
    def admin_edit_user(user_type: str, user_id: int):
        from models import get_user_model

        model = get_user_model(user_type)
        if not model:
            flash("Unknown user type.", "error")
            return redirect(url_for("admin_users"))

        user = model.query.get_or_404(user_id)

        form = AdminUserEditForm(obj=user)
        if form.validate_on_submit():
            user.full_name = form.full_name.data.strip()
            user.phone = form.phone.data.strip()
            user.organization = (form.organization.data or "").strip() or None
            user.active = bool(form.active.data)
            db.session.commit()
            flash("User updated successfully.", "success")
            return redirect(url_for("admin_users"))

        return render_template("admin/edit_user.html", form=form, user=user, user_type=user_type)

    @app.route("/admin/password-requests")
    @roles_required("admin")
    def admin_password_requests():
        pending_requests = (
            PasswordResetRequest.query.filter_by(status="pending")
            .order_by(PasswordResetRequest.created_at.asc())
            .all()
        )
        recent_requests = (
            PasswordResetRequest.query.filter(PasswordResetRequest.status != "pending")
            .order_by(PasswordResetRequest.resolved_at.desc(), PasswordResetRequest.created_at.desc())
            .limit(10)
            .all()
        )

        return render_template(
            "admin/password_requests.html",
            pending_requests=pending_requests,
            recent_requests=recent_requests,
        )

    @app.route("/admin/password-requests/<int:request_id>", methods=["GET", "POST"])
    @roles_required("admin")
    def admin_password_request_detail(request_id: int):
        reset_request = PasswordResetRequest.query.get_or_404(request_id)
        form = AdminPasswordResetForm()

        if form.validate_on_submit():
            if reset_request.status == "completed":
                flash("This request has already been closed.", "info")
            else:
                model = USER_MODELS.get(reset_request.user_type)
                user = db.session.get(model, reset_request.user_id) if model else None
                if not user:
                    flash("Original user record could not be found.", "error")
                else:
                    user.password_hash = generate_password_hash(form.new_password.data.strip())
                    reset_request.mark_completed(current_user)
                    reset_request.admin_note = (form.admin_note.data or "").strip() or None
                    db.session.commit()
                    flash("Password updated and request closed.", "success")
                    return redirect(url_for("admin_password_requests"))

        return render_template(
            "admin/password_request_detail.html",
            form=form,
            reset_request=reset_request,
        )

    @app.route("/account/edit", methods=["GET", "POST"])
    @roles_required("customer", "vendor")
    def edit_account():
        form = AccountUpdateForm(obj=current_user)

        if form.validate_on_submit():
            current_user.full_name = form.full_name.data.strip()
            current_user.phone = form.phone.data.strip()
            current_user.organization = (form.organization.data or "").strip() or None
            if form.new_password.data:
                current_user.password_hash = generate_password_hash(form.new_password.data.strip())

            db.session.commit()
            flash("Account details updated.", "success")
            return redirect(url_for("dashboard"))

        if not form.is_submitted():
            form.organization.data = current_user.organization or ""

        template_map = {
            "customer": "user/edit_account.html",
            "vendor": "vendor/edit_account.html",
        }
        template_name = template_map.get(current_user.user_type)
        if not template_name:
            flash("Unable to determine the correct account page.", "error")
            return redirect(url_for("dashboard"))

        return render_template(template_name, form=form, user=current_user)

    @app.route("/upload-print-job", methods=["POST"])
    @roles_required("customer")
    def upload_print_job():
        """Handle file upload for print jobs"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            return jsonify({'error': 'Invalid file type'}), 400
        
        try:
            # Secure the filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{current_user.id}_{timestamp}_{filename}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = get_file_type(filename)
            
            # Extract file attributes
            file_attributes = extract_file_attributes(file_path, file_type)
            
            # Create print job
            print_job = PrintJob(
                customer_id=current_user.id,
                title=filename.rsplit('.', 1)[0],  # Remove extension
                file_name=filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                image_width=file_attributes.get('width'),
                image_height=file_attributes.get('height'),
                image_format=file_attributes.get('format'),
                page_count=file_attributes.get('page_count'),
                status='pending'
            )
            
            db.session.add(print_job)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'job_id': print_job.id,
                'message': 'File uploaded successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Upload error: {str(e)}")
            return jsonify({'error': 'Upload failed. Please try again.'}), 500

    @app.route("/create-order", methods=["GET"])
    @roles_required("customer")
    def create_order():
        """Display create order page"""
        # Create a form for CSRF token
        from flask_wtf import FlaskForm
        form = FlaskForm()
        
        # Get all active service prices
        services = ServicePrice.query.filter_by(active=True).all()
        services_data = [
            {
                'id': s.id,
                'category': s.category,
                'service_name': s.service_name,
                'unit_price_min': s.unit_price_min,
                'unit_price_max': s.unit_price_max,
                'average_price': s.average_price,
                'unit': s.unit,
                'description': s.description
            }
            for s in services
        ]
        return render_template("user/create_order.html", services=services_data, form=form)

    @app.route("/create-order", methods=["POST"])
    @roles_required("customer")
    def submit_order():
        """Handle order submission with single item"""
        try:
            # Generate unique order number
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{Order.query.count() + 1:04d}"
            
            # Get service details from items[1][...] fields (JavaScript creates these)
            service_id = request.form.get('items[1][service]')
            quantity = int(request.form.get('items[1][quantity]', 1))
            specifications = request.form.get('items[1][specifications]', '')
            quote_duration = int(request.form.get('quote_duration', 24))  # Default 24 hours
            
            # Get service price
            service = ServicePrice.query.get(service_id)
            if not service:
                return jsonify({'error': 'Invalid service selected'}), 400
            
            # Calculate quote deadline
            quote_deadline = datetime.now() + timedelta(hours=quote_duration)
            
            # Create order with service_category and deadline
            order = Order(
                customer_id=current_user.id,
                order_number=order_number,
                customer_notes=request.form.get('customer_notes', ''),
                service_category=service.category,  # Set the category for vendor matching
                quote_duration_hours=quote_duration,
                quote_deadline=quote_deadline,
                status='pending'
            )
            
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Calculate prices
            unit_price = service.average_price
            total_price = unit_price * quantity
            
            # Create single order item
            order_item = OrderItem(
                order_id=order.id,
                service_category=service.category,
                service_type=service.service_name,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                specifications=specifications
            )
            
            # Handle file upload if present (field name is items[1][file])
            file_field_name = 'items[1][file]'
            if file_field_name in request.files:
                file = request.files[file_field_name]
                if file and file.filename:
                    # Create folder for this order
                    order_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'order_{order.order_number}')
                    os.makedirs(order_folder, exist_ok=True)
                    
                    # Secure filename
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(order_folder, unique_filename)
                    
                    # Save file
                    file.save(file_path)
                    
                    # Get file info
                    file_size = os.path.getsize(file_path)
                    file_type = get_file_type(filename)
                    
                    # Extract attributes
                    file_attributes = extract_file_attributes(file_path, file_type)
                    
                    # Update order item with file info
                    order_item.file_name = filename
                    order_item.file_path = file_path
                    order_item.file_type = file_type
                    order_item.file_size = file_size
                    order_item.image_width = file_attributes.get('width')
                    order_item.image_height = file_attributes.get('height')
                    order_item.image_format = file_attributes.get('format')
                    order_item.page_count = file_attributes.get('page_count')
            
            db.session.add(order_item)
            
            # Calculate order totals
            order.calculate_total()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number,
                'message': 'Order created successfully! Vendors will soon submit quotes for your review.'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Order creation error: {str(e)}")
            return jsonify({'error': 'Failed to create order. Please try again.'}), 500

    # Vendor Routes
    @app.route("/vendor/order/<int:order_id>")
    @roles_required("vendor")
    def vendor_view_order(order_id):
        """View order details"""
        from flask_wtf import FlaskForm
        order = Order.query.get_or_404(order_id)
        
        # Check if vendor can view this order (has matching service or already quoted/assigned)
        vendor_can_view = False
        if order.vendor_id == current_user.id:
            vendor_can_view = True
        elif order.service_category:
            if (order.service_category == "Document Printing" and current_user.service_document_printing) or \
               (order.service_category == "Photo Printing" and current_user.service_photos) or \
               (order.service_category == "Uniforms & Apparel" and current_user.service_uniforms) or \
               (order.service_category == "Merchandise" and current_user.service_merchandise) or \
               (order.service_category == "Large Format" and current_user.service_large_format):
                vendor_can_view = True
        
        if not vendor_can_view:
            flash("You don't have access to this order.", "error")
            return redirect(url_for("dashboard"))
        
        # Get this vendor's quotes for this order
        my_quotes = Quote.query.filter_by(order_id=order.id, vendor_id=current_user.id).order_by(Quote.created_at.desc()).all()
        
        form = FlaskForm()
        return render_template("vendor/order_detail.html", order=order, form=form, my_quotes=my_quotes)

    @app.route("/order/<int:order_id>/download/<int:item_id>")
    @login_required
    def download_order_file(order_id, item_id):
        """Download file attached to order item"""
        order = Order.query.get_or_404(order_id)
        item = OrderItem.query.get_or_404(item_id)
        
        # Check permissions
        if current_user.user_type == "customer":
            if order.customer_id != current_user.id:
                flash("You don't have access to this file.", "error")
                return redirect(url_for("dashboard"))
        elif current_user.user_type == "vendor":
            # Vendor can access if they're assigned or if order is open for quotes
            if order.vendor_id != current_user.id and not order.quotes_open:
                flash("You don't have access to this file.", "error")
                return redirect(url_for("dashboard"))
        
        if item.order_id != order.id:
            flash("Invalid file request.", "error")
            return redirect(url_for("dashboard"))
        
        if not item.file_path or not os.path.exists(item.file_path):
            flash("File not found.", "error")
            return redirect(url_for("dashboard"))
        
        return send_file(item.file_path, as_attachment=True, download_name=item.file_name)

    @app.route("/vendor/order/<int:order_id>/quote", methods=["GET", "POST"])
    @roles_required("vendor")
    def vendor_submit_quote(order_id):
        """Submit or revise a quote for an order"""
        order = Order.query.get_or_404(order_id)
        
        # Check if quotes are still open
        if not order.quotes_open:
            if order.vendor_id:
                flash("This order has been assigned to another vendor.", "error")
            elif order.is_quote_deadline_passed:
                flash("The quote deadline for this order has passed.", "error")
            else:
                flash("This order is no longer accepting quotes.", "error")
            return redirect(url_for("dashboard"))
        
        # Check service match
        vendor_can_quote = False
        if (order.service_category == "Document Printing" and current_user.service_document_printing) or \
           (order.service_category == "Photo Printing" and current_user.service_photos) or \
           (order.service_category == "Uniforms & Apparel" and current_user.service_uniforms) or \
           (order.service_category == "Merchandise" and current_user.service_merchandise) or \
           (order.service_category == "Large Format" and current_user.service_large_format):
            vendor_can_quote = True
        
        if not vendor_can_quote:
            flash("You don't offer the service required for this order.", "error")
            return redirect(url_for("dashboard"))
        
        if request.method == "POST":
            # Get next quote number for this vendor
            quote_number = order.get_vendor_quote_count(current_user.id) + 1
            
            # Create new quote
            quote = Quote(
                order_id=order.id,
                vendor_id=current_user.id,
                quote_number=quote_number,
                base_fee=float(request.form.get("base_fee", 75.0)),
                vendor_message=request.form.get("vendor_message", ""),
                status="pending"
            )
            
            # Create quote items with pricing
            subtotal = 0
            for item in order.order_items:
                adjusted_price = float(request.form.get(f"item_{item.id}_price", item.unit_price))
                adjusted_total = adjusted_price * item.quantity
                
                quote_item = QuoteItem(
                    order_item_id=item.id,
                    unit_price=adjusted_price,
                    total_price=adjusted_total,
                    vendor_notes=request.form.get(f"item_{item.id}_notes", "")
                )
                quote.quote_items.append(quote_item)
                subtotal += adjusted_total
            
            quote.subtotal = subtotal
            quote.total_amount = quote.base_fee + subtotal
            
            db.session.add(quote)
            
            # Update order status if this is the first quote
            if order.status == "pending":
                order.add_status_change("awaiting_quotes", current_user.id, "vendor",
                                       f"{current_user.business_name} submitted a quote")
            elif order.quote_count == 0:
                order.add_status_change("quoted", current_user.id, "vendor",
                                       f"{current_user.business_name} submitted a quote")
            
            db.session.commit()
            
            flash(f"Quote submitted successfully! The customer will review it.", "success")
            return redirect(url_for("dashboard"))
        
        # GET request - show quote form
        from flask_wtf import FlaskForm
        form = FlaskForm()
        
        # Get vendor's previous quotes for this order
        my_quotes = Quote.query.filter_by(order_id=order.id, vendor_id=current_user.id).order_by(Quote.created_at.desc()).all()
        
        return render_template("vendor/manage_order.html", order=order, form=form, my_quotes=my_quotes)

    @app.route("/vendor/order/<int:order_id>/status", methods=["POST"])
    @roles_required("vendor")
    def vendor_update_status(order_id):
        """Update order status with progress tracking"""
        order = Order.query.get_or_404(order_id)
        
        if order.vendor_id != current_user.id:
            flash("You don't have access to this order.", "error")
            return redirect(url_for("dashboard"))
        
        new_status = request.form.get("new_status")
        notes = request.form.get("notes", "")
        
        # Validate status progression
        valid_transitions = {
            'in_progress': ['confirmed_received'],
            'confirmed_received': ['processing'],
            'processing': ['finished'],
            'finished': ['quality_check'],
            'quality_check': ['ready_dispatch'],
            'ready_dispatch': ['dispatched'],
            'dispatched': ['awaiting_payment', 'completed'],
            'awaiting_payment': ['completed']
        }
        
        if order.status not in valid_transitions or new_status not in valid_transitions.get(order.status, []):
            flash(f"Invalid status transition from {order.status} to {new_status}", "error")
            return redirect(url_for("vendor_view_order", order_id=order.id))
        
        # Add status change with notes
        order.add_status_change(new_status, current_user.id, "vendor", notes)
        
        # Update timestamps based on status
        if new_status == 'ready_dispatch':
            order.ready_at = datetime.utcnow()
        elif new_status == 'dispatched':
            order.dispatched_at = datetime.utcnow()
        elif new_status == 'completed':
            order.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f"Order status updated to {new_status.replace('_', ' ').title()}", "success")
        return redirect(url_for("vendor_view_order", order_id=order.id))

    # Customer Routes
    @app.route("/customer/order/<int:order_id>")
    @roles_required("customer")
    def customer_view_order(order_id):
        """View order details with quotes and history"""
        from flask_wtf import FlaskForm
        order = Order.query.get_or_404(order_id)
        
        # Ensure this customer owns the order
        if order.customer_id != current_user.id:
            flash("You don't have access to this order.", "error")
            return redirect(url_for("dashboard"))
        
        form = FlaskForm()
        return render_template("user/order_detail.html", order=order, form=form)

    @app.route("/customer/order/<int:order_id>/quote/<int:quote_id>/respond", methods=["POST"])
    @roles_required("customer")
    def customer_respond_to_quote(order_id, quote_id):
        """Accept or reject a quote - accepting assigns the vendor"""
        order = Order.query.get_or_404(order_id)
        
        if order.customer_id != current_user.id:
            flash("You don't have access to this order.", "error")
            return redirect(url_for("dashboard"))
        
        quote = Quote.query.get_or_404(quote_id)
        if quote.order_id != order.id:
            flash("Invalid quote.", "error")
            return redirect(url_for("customer_view_order", order_id=order.id))
        
        action = request.form.get("action")
        customer_response = request.form.get("customer_response", "")
        
        if action == "accept":
            # Mark this quote as accepted
            quote.status = "accepted"
            quote.customer_response = "Quote accepted"
            quote.responded_at = datetime.utcnow()
            
            # Assign vendor to order
            order.vendor_id = quote.vendor_id
            order.selected_quote_id = quote.id
            order.vendor_assigned_at = datetime.utcnow()
            order.accepted_at = datetime.utcnow()
            
            # Update pricing from quote
            order.base_fee = quote.base_fee
            order.subtotal = quote.subtotal
            order.total_amount = quote.total_amount
            
            # Set status to in_progress so vendor can start working
            order.status = 'in_progress'
            
            # Reject all other pending quotes for this order
            for other_quote in order.quotes:
                if other_quote.id != quote.id and other_quote.status == "pending":
                    other_quote.status = "rejected"
                    other_quote.customer_response = "Customer selected another vendor"
                    other_quote.responded_at = datetime.utcnow()
            
            order.add_status_change("accepted", current_user.id, "customer", 
                                   f"Customer accepted quote from {quote.vendor.business_name}")
            
            flash(f"Quote accepted! {quote.vendor.business_name} will begin working on your order.", "success")
        
        elif action == "reject":
            quote.status = "rejected"
            quote.customer_response = customer_response or "Quote rejected"
            quote.responded_at = datetime.utcnow()
            
            # Check if there are other pending quotes
            other_pending = [q for q in order.quotes if q.status == "pending" and q.id != quote.id]
            if other_pending:
                flash("Quote rejected. You can review other quotes or wait for more vendors to submit quotes.", "info")
            else:
                order.add_status_change("awaiting_quotes", current_user.id, "customer",
                                       f"Customer rejected quote from {quote.vendor.business_name}")
                flash("Quote rejected. Your order is still open for other vendors to quote.", "info")
        
        db.session.commit()
        return redirect(url_for("customer_view_order", order_id=order.id))

    @app.route("/customer/order/<int:order_id>/confirm-receipt", methods=["POST"])
    @roles_required("customer")
    def customer_confirm_receipt(order_id):
        """Confirm receipt of completed order"""
        order = Order.query.get_or_404(order_id)
        
        if order.customer_id != current_user.id:
            flash("You don't have access to this order.", "error")
            return redirect(url_for("dashboard"))
        
        if order.status != "dispatched":
            flash("Order is not ready for confirmation.", "error")
            return redirect(url_for("customer_view_order", order_id=order.id))
        
        order.add_status_change("completed", current_user.id, "customer", 
                               "Customer confirmed receipt")
        order.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash("Order marked as completed! Please leave a review.", "success")
        return redirect(url_for("customer_view_order", order_id=order.id))

    @app.route("/customer/order/<int:order_id>/review", methods=["POST"])
    @roles_required("customer")
    def customer_submit_review(order_id):
        """Submit a review for a completed order"""
        order = Order.query.get_or_404(order_id)
        
        if order.customer_id != current_user.id:
            flash("You don't have access to this order.", "error")
            return redirect(url_for("dashboard"))
        
        if order.status != "completed":
            flash("You can only review completed orders.", "error")
            return redirect(url_for("customer_view_order", order_id=order.id))
        
        if order.review:
            flash("You have already reviewed this order.", "error")
            return redirect(url_for("customer_view_order", order_id=order.id))
        
        rating = int(request.form.get("rating"))
        comment = request.form.get("comment", "").strip()
        
        if not (1 <= rating <= 5):
            flash("Invalid rating. Please select 1-5 stars.", "error")
            return redirect(url_for("customer_view_order", order_id=order.id))
        
        review = Review(
            order_id=order.id,
            customer_id=current_user.id,
            vendor_id=order.vendor_id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash("Thank you for your review!", "success")
        return redirect(url_for("customer_view_order", order_id=order.id))

    # Error handlers
    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden access"""
        flash("You don't have permission to access this page.", "error")
        return redirect(url_for("dashboard") if current_user.is_authenticated else url_for("login"))

    @app.errorhandler(404)
    def not_found(error):
        """Handle page not found"""
        return render_template("base.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server error"""
        db.session.rollback()
        flash("An internal error occurred. Please try again.", "error")
        return redirect(url_for("home"))


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_type(filename):
    """Determine file type from extension"""
    extension = filename.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        return 'pdf'
    elif extension == 'docx':
        return 'docx'
    elif extension in ['png', 'jpg', 'jpeg']:
        return 'image'
    return 'unknown'


def extract_file_attributes(file_path, file_type):
    """Extract attributes from uploaded file"""
    attributes = {}
    
    try:
        if file_type == 'image':
            # Extract image attributes
            from PIL import Image
            with Image.open(file_path) as img:
                attributes['width'] = img.width
                attributes['height'] = img.height
                attributes['format'] = img.format
        
        elif file_type == 'pdf':
            # Extract PDF page count
            try:
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    attributes['page_count'] = len(pdf_reader.pages)
            except:
                # If PyPDF2 fails, try alternative method
                attributes['page_count'] = 1  # Default to 1 page
        
        elif file_type == 'docx':
            # Extract DOCX page count (approximate)
            try:
                from docx import Document
                doc = Document(file_path)
                # Rough estimate: 1 page per 500 words
                word_count = sum(len(paragraph.text.split()) for paragraph in doc.paragraphs)
                attributes['page_count'] = max(1, word_count // 500)
            except:
                attributes['page_count'] = 1  # Default to 1 page
    
    except Exception as e:
        current_app.logger.error(f"Error extracting file attributes: {str(e)}")
    
    return attributes


def seed_admin():
    default_email = os.getenv("ADMIN_EMAIL", "admin@smartprintpro.com")
    default_password = os.getenv("ADMIN_PASSWORD", "Admin@123")

    try:
        existing = Admin.query.filter_by(email=default_email).first()
    except OperationalError as exc:
        db.session.rollback()
        current_app.logger.warning("Skipping default admin seed until migrations run: %s", exc)
        return

    if existing:
        return

    admin = Admin(
        full_name=os.getenv("ADMIN_NAME", "System Administrator"),
        email=default_email,
        phone=os.getenv("ADMIN_PHONE", "+254700000000"),
        organization="SmartPrint Pro",
    )
    admin.password_hash = generate_password_hash(default_password)
    db.session.add(admin)
    db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run()