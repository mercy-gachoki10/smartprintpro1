"""
Clear all records from the database while preserving table structure.
Also removes uploaded files from order folders.
WARNING: This will delete ALL data from all tables and uploaded files!
"""

import os
import sys
import shutil
from flask import Flask
from extension import db
from models import (
    Customer,
    Vendor,
    Admin,
    Order,
    OrderItem,
    OrderStatusHistory,
    Quote,
    QuoteItem,
    Review,
    ServicePrice,
    PrintJob,
    PasswordResetRequest
)

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def clear_uploaded_files():
    """Remove all uploaded files from order folders"""
    uploads_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    
    if not os.path.exists(uploads_dir):
        print("  ○ No uploads directory found")
        return 0
    
    deleted_folders = 0
    deleted_files = 0
    
    try:
        for item in os.listdir(uploads_dir):
            item_path = os.path.join(uploads_dir, item)
            
            # Remove order folders (order_ORD-*)
            if os.path.isdir(item_path) and item.startswith('order_'):
                try:
                    # Count files before deletion
                    file_count = sum(len(files) for _, _, files in os.walk(item_path))
                    deleted_files += file_count
                    
                    shutil.rmtree(item_path)
                    deleted_folders += 1
                    print(f"  ✓ Deleted folder: {item} ({file_count} file(s))")
                except Exception as e:
                    print(f"  ✗ Failed to delete {item}: {str(e)}")
        
        return deleted_folders, deleted_files
    
    except Exception as e:
        print(f"  ✗ Error accessing uploads directory: {str(e)}")
        return 0, 0

def clear_all_data():
    """Clear all data from all tables"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("DATABASE CLEARING SCRIPT")
        print("="*60)
        print("\n⚠️  WARNING: This will DELETE ALL DATA from the database!")
        print("This includes:")
        print("  - All customers")
        print("  - All vendors")
        print("  - All admins")
        print("  - All orders and order items")
        print("  - All quotes")
        print("  - All reviews")
        print("  - All service prices")
        print("  - All print jobs")
        print("  - All password reset requests")
        print("  - All uploaded files in order folders")
        print("\nThe table structure will be preserved.")
        print("\n" + "="*60)
        
        response = input("\nAre you sure you want to continue? Type 'YES' to confirm: ")
        
        if response != 'YES':
            print("\n❌ Operation cancelled. No data was deleted.")
            return
        
        print("\n🔄 Starting data deletion...\n")
        
        try:
            # Delete in order of dependencies (child tables first)
            tables = [
                ('Order Status History', OrderStatusHistory),
                ('Quote Items', QuoteItem),
                ('Quotes', Quote),
                ('Reviews', Review),
                ('Order Items', OrderItem),
                ('Orders', Order),
                ('Print Jobs', PrintJob),
                ('Service Prices', ServicePrice),
                ('Password Reset Requests', PasswordResetRequest),
                ('Customers', Customer),
                ('Vendors', Vendor),
                ('Admins', Admin),
            ]
            
            deleted_counts = {}
            
            for table_name, model in tables:
                count = model.query.count()
                if count > 0:
                    model.query.delete()
                    deleted_counts[table_name] = count
                    print(f"  ✓ Deleted {count} record(s) from {table_name}")
                else:
                    print(f"  ○ {table_name}: No records to delete")
            
            # Commit all deletions
            db.session.commit()
            
            # Delete uploaded files
            print("\n🗂️  Clearing uploaded files...")
            folders_deleted, files_deleted = clear_uploaded_files()
            
            print("\n" + "="*60)
            print("✅ DATABASE CLEARED SUCCESSFULLY!")
            print("="*60)
            
            if deleted_counts or folders_deleted > 0:
                print("\nSummary:")
                if deleted_counts:
                    total = sum(deleted_counts.values())
                    for table, count in deleted_counts.items():
                        print(f"  • {table}: {count} records")
                    print(f"\n  Total database records deleted: {total}")
                
                if folders_deleted > 0:
                    print(f"\n  • Upload folders deleted: {folders_deleted}")
                    print(f"  • Files deleted: {files_deleted}")
            else:
                print("\nDatabase and uploads were already empty.")
            
            print("\n" + "="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error occurred: {str(e)}")
            print("Database rollback performed. No changes were made.")
            sys.exit(1)

def clear_specific_table():
    """Clear data from a specific table"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("CLEAR SPECIFIC TABLE")
        print("="*60)
        
        tables = {
            '1': ('Customers', Customer),
            '2': ('Vendors', Vendor),
            '3': ('Admins', Admin),
            '4': ('Orders', Order),
            '5': ('Order Items', OrderItem),
            '6': ('Quotes', Quote),
            '7': ('Reviews', Review),
            '8': ('Service Prices', ServicePrice),
            '9': ('Print Jobs', PrintJob),
            '10': ('Password Reset Requests', PasswordResetRequest),
        }
        
        print("\nSelect table to clear:")
        for key, (name, _) in tables.items():
            print(f"  {key}. {name}")
        print("  0. Cancel")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '0' or choice not in tables:
            print("\n❌ Operation cancelled.")
            return
        
        table_name, model = tables[choice]
        count = model.query.count()
        
        if count == 0:
            print(f"\n✓ {table_name} table is already empty.")
            return
        
        print(f"\n⚠️  WARNING: This will delete {count} record(s) from {table_name}")
        response = input("Type 'YES' to confirm: ")
        
        if response != 'YES':
            print("\n❌ Operation cancelled.")
            return
        
        try:
            model.query.delete()
            db.session.commit()
            print(f"\n✅ Successfully deleted {count} record(s) from {table_name}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")
            sys.exit(1)

def show_database_stats():
    """Show current database statistics"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60 + "\n")
        
        tables = [
            ('Customers', Customer),
            ('Vendors', Vendor),
            ('Admins', Admin),
            ('Orders', Order),
            ('Order Items', OrderItem),
            ('Quotes', Quote),
            ('Quote Items', QuoteItem),
            ('Reviews', Review),
            ('Order Status History', OrderStatusHistory),
            ('Service Prices', ServicePrice),
            ('Print Jobs', PrintJob),
            ('Password Reset Requests', PasswordResetRequest),
        ]
        
        total = 0
        for table_name, model in tables:
            count = model.query.count()
            total += count
            status = "✓" if count > 0 else "○"
            print(f"  {status} {table_name:.<30} {count:>6} records")
        
        print("\n" + "-"*60)
        print(f"  Total records:........................ {total:>6}")
        
        # Count uploaded files
        uploads_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
        if os.path.exists(uploads_dir):
            folder_count = 0
            file_count = 0
            for item in os.listdir(uploads_dir):
                item_path = os.path.join(uploads_dir, item)
                if os.path.isdir(item_path) and item.startswith('order_'):
                    folder_count += 1
                    file_count += sum(len(files) for _, _, files in os.walk(item_path))
            
            print(f"  Upload folders:....................... {folder_count:>6}")
            print(f"  Uploaded files:....................... {file_count:>6}")
        
        print("="*60 + "\n")

def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("DATABASE MANAGEMENT SCRIPT")
        print("="*60)
        print("\nOptions:")
        print("  1. Show database statistics")
        print("  2. Clear specific table")
        print("  3. Clear ALL data (WARNING!)")
        print("  4. Clear uploaded files only")
        print("  0. Exit")
        print("\n" + "="*60)
        
        choice = input("\nEnter your choice: ")
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            show_database_stats()
        elif choice == '2':
            clear_specific_table()
        elif choice == '3':
            clear_all_data()
        elif choice == '4':
            print("\n⚠️  WARNING: This will delete all uploaded files in order folders!")
            response = input("Type 'YES' to confirm: ")
            if response == 'YES':
                print("\n🗂️  Clearing uploaded files...")
                folders_deleted, files_deleted = clear_uploaded_files()
                if folders_deleted > 0:
                    print(f"\n✅ Deleted {folders_deleted} folder(s) containing {files_deleted} file(s)")
                else:
                    print("\n✓ No upload folders found")
            else:
                print("\n❌ Operation cancelled.")
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
