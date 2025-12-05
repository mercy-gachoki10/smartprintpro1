"""
Seed script to populate database with test customers and vendors
"""
from app import app, db
from models import Customer, Vendor
from werkzeug.security import generate_password_hash

def seed_users():
    """Create test customers and vendors"""
    
    with app.app_context():
        print("🌱 Seeding users...")
        
        # Clear existing users (optional - comment out if you want to keep existing)
        # Customer.query.delete()
        # Vendor.query.delete()
        
        # Seed 10 Customers
        customers_data = [
            {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "phone": "+254712345001",
                "organization": "Tech Startup Inc"
            },
            {
                "email": "sarah.wilson@example.com",
                "full_name": "Sarah Wilson",
                "phone": "+254712345002",
                "organization": "Marketing Solutions Ltd"
            },
            {
                "email": "michael.brown@example.com",
                "full_name": "Michael Brown",
                "phone": "+254712345003",
                "organization": "Brown Consulting"
            },
            {
                "email": "emma.davis@example.com",
                "full_name": "Emma Davis",
                "phone": "+254712345004",
                "organization": "Davis & Associates"
            },
            {
                "email": "james.miller@example.com",
                "full_name": "James Miller",
                "phone": "+254712345005",
                "organization": "Miller Events Co"
            },
            {
                "email": "olivia.taylor@example.com",
                "full_name": "Olivia Taylor",
                "phone": "+254712345006",
                "organization": "Taylor Design Studio"
            },
            {
                "email": "william.anderson@example.com",
                "full_name": "William Anderson",
                "phone": "+254712345007",
                "organization": "Anderson Legal Services"
            },
            {
                "email": "sophia.thomas@example.com",
                "full_name": "Sophia Thomas",
                "phone": "+254712345008",
                "organization": "Thomas Photography"
            },
            {
                "email": "benjamin.moore@example.com",
                "full_name": "Benjamin Moore",
                "phone": "+254712345009",
                "organization": "Moore Real Estate"
            },
            {
                "email": "charlotte.jackson@example.com",
                "full_name": "Charlotte Jackson",
                "phone": "+254712345010",
                "organization": "Jackson Catering"
            }
        ]
        
        customers_created = 0
        for customer_data in customers_data:
            # Check if customer already exists
            existing = Customer.query.filter_by(email=customer_data["email"]).first()
            if not existing:
                # Password is first name + 'pass' (e.g., johnpass, sarahpass)
                first_name = customer_data["full_name"].split()[0].lower()
                password = f"{first_name}pass"
                
                customer = Customer(
                    email=customer_data["email"],
                    password_hash=generate_password_hash(password),
                    full_name=customer_data["full_name"],
                    phone=customer_data["phone"],
                    organization=customer_data["organization"],
                    active=True
                )
                db.session.add(customer)
                customers_created += 1
        
        # Seed 30 Vendors with various service combinations
        vendors_data = [
            # Full service vendors (all services)
            {
                "email": "printpro@example.com",
                "business_name": "PrintPro Solutions",
                "full_name": "David Martinez",
                "phone": "+254722100001",
                "business_address": "Tom Mboya Street, Nairobi CBD",
                "business_type": "Full Service Print Shop",
                "tax_id": "P051234567A",
                "services": ["doc", "photo", "uniform", "merch", "large"]
            },
            {
                "email": "allprint@example.com",
                "business_name": "AllPrint Services",
                "full_name": "Maria Garcia",
                "phone": "+254722100002",
                "business_address": "Kenyatta Avenue, Nairobi",
                "business_type": "Full Service Print Shop",
                "tax_id": "P051234568B",
                "services": ["doc", "photo", "uniform", "merch", "large"]
            },
            {
                "email": "megaprint@example.com",
                "business_name": "MegaPrint Hub",
                "full_name": "Robert Lee",
                "phone": "+254722100003",
                "business_address": "Moi Avenue, Nairobi",
                "business_type": "Full Service Print Shop",
                "tax_id": "P051234569C",
                "services": ["doc", "photo", "uniform", "merch", "large"]
            },
            
            # Document printing specialists
            {
                "email": "quickdocs@example.com",
                "business_name": "QuickDocs Print",
                "full_name": "Jennifer White",
                "phone": "+254722100004",
                "business_address": "Kimathi Street, Nairobi",
                "business_type": "Copy Center",
                "tax_id": "P051234570D",
                "services": ["doc"]
            },
            {
                "email": "docmaster@example.com",
                "business_name": "DocMaster Pro",
                "full_name": "Kevin Harris",
                "phone": "+254722100005",
                "business_address": "Westlands, Nairobi",
                "business_type": "Copy Center",
                "tax_id": "P051234571E",
                "services": ["doc"]
            },
            {
                "email": "speedyprint@example.com",
                "business_name": "Speedy Print Services",
                "full_name": "Lisa Thompson",
                "phone": "+254722100006",
                "business_address": "Ngong Road, Nairobi",
                "business_type": "Print & Signage Shop",
                "tax_id": "P051234572F",
                "services": ["doc", "large"]
            },
            {
                "email": "officedocs@example.com",
                "business_name": "Office Docs Hub",
                "full_name": "Daniel Clark",
                "phone": "+254722100007",
                "business_address": "Upper Hill, Nairobi",
                "business_type": "Copy Center",
                "tax_id": "P051234573G",
                "services": ["doc"]
            },
            
            # Photo printing specialists
            {
                "email": "photoperfect@example.com",
                "business_name": "PhotoPerfect Studios",
                "full_name": "Amanda Rodriguez",
                "phone": "+254722100008",
                "business_address": "Sarit Centre, Westlands",
                "business_type": "Photo Studio",
                "tax_id": "P051234574H",
                "services": ["photo"]
            },
            {
                "email": "snapprint@example.com",
                "business_name": "SnapPrint Gallery",
                "full_name": "Christopher Lewis",
                "phone": "+254722100009",
                "business_address": "The Junction Mall, Nairobi",
                "business_type": "Photo Studio & Signage",
                "tax_id": "P051234575I",
                "services": ["photo", "large"]
            },
            {
                "email": "memorylane@example.com",
                "business_name": "Memory Lane Photos",
                "full_name": "Patricia Walker",
                "phone": "+254722100010",
                "business_address": "Yaya Centre, Kilimani",
                "business_type": "Photo Studio",
                "tax_id": "P051234576J",
                "services": ["photo"]
            },
            {
                "email": "pixelprint@example.com",
                "business_name": "Pixel Print Pro",
                "full_name": "Matthew Hall",
                "phone": "+254722100011",
                "business_address": "Gigiri, Nairobi",
                "business_type": "Photo & Merchandise Shop",
                "tax_id": "P051234577K",
                "services": ["photo", "merch"]
            },
            
            # Uniform & apparel specialists
            {
                "email": "uniformpro@example.com",
                "business_name": "UniformPro Kenya",
                "full_name": "Susan Allen",
                "phone": "+254722100012",
                "business_address": "Industrial Area, Nairobi",
                "business_type": "Uniform & Apparel",
                "tax_id": "P051234578L",
                "services": ["uniform"]
            },
            {
                "email": "apparelplus@example.com",
                "business_name": "Apparel Plus",
                "full_name": "Mark Young",
                "phone": "+254722100013",
                "business_address": "Mombasa Road, Nairobi",
                "business_type": "Uniform & Merchandise",
                "tax_id": "P051234579M",
                "services": ["uniform", "merch"]
            },
            {
                "email": "teamgear@example.com",
                "business_name": "TeamGear Uniforms",
                "full_name": "Rebecca King",
                "phone": "+254722100014",
                "business_address": "Eastleigh, Nairobi",
                "business_type": "Uniform Supplier",
                "tax_id": "P051234580N",
                "services": ["uniform"]
            },
            {
                "email": "corporatewear@example.com",
                "business_name": "CorporateWear Solutions",
                "full_name": "Paul Wright",
                "phone": "+254722100015",
                "business_address": "Karen, Nairobi",
                "business_type": "Corporate Uniform & Merchandise",
                "tax_id": "P051234581O",
                "services": ["uniform", "merch"]
            },
            
            # Merchandise specialists
            {
                "email": "brandmerch@example.com",
                "business_name": "BrandMerch Co",
                "full_name": "Nancy Scott",
                "phone": "+254722100016",
                "business_address": "Lavington, Nairobi",
                "business_type": "Branded Merchandise",
                "tax_id": "P051234582P",
                "services": ["merch"]
            },
            {
                "email": "promogifts@example.com",
                "business_name": "PromoGifts Kenya",
                "full_name": "Steven Green",
                "phone": "+254722100017",
                "business_address": "Parklands, Nairobi",
                "business_type": "Promotional Merchandise & Documents",
                "tax_id": "P051234583Q",
                "services": ["merch", "doc"]
            },
            {
                "email": "swagstore@example.com",
                "business_name": "Swag Store Print",
                "full_name": "Karen Adams",
                "phone": "+254722100018",
                "business_address": "Hurlingham, Nairobi",
                "business_type": "Merchandise & Uniforms",
                "tax_id": "P051234584R",
                "services": ["merch", "uniform"]
            },
            {
                "email": "giftprint@example.com",
                "business_name": "GiftPrint Hub",
                "full_name": "Joshua Baker",
                "phone": "+254722100019",
                "business_address": "Kilimani, Nairobi",
                "business_type": "Merchandise & Photo Gifts",
                "tax_id": "P051234585S",
                "services": ["merch", "photo"]
            },
            
            # Large format specialists
            {
                "email": "bigprint@example.com",
                "business_name": "BigPrint Banners",
                "full_name": "Michelle Nelson",
                "phone": "+254722100020",
                "business_address": "Thika Road, Nairobi",
                "business_type": "Large Format Printing",
                "tax_id": "P051234586T",
                "services": ["large"]
            },
            {
                "email": "signagepro@example.com",
                "business_name": "SignagePro Kenya",
                "full_name": "Ryan Carter",
                "phone": "+254722100021",
                "business_address": "Jogoo Road, Nairobi",
                "business_type": "Signage & Documents",
                "tax_id": "P051234587U",
                "services": ["large", "doc"]
            },
            {
                "email": "bannerboss@example.com",
                "business_name": "Banner Boss",
                "full_name": "Laura Mitchell",
                "phone": "+254722100022",
                "business_address": "Outering Road, Nairobi",
                "business_type": "Banner Printing",
                "tax_id": "P051234588V",
                "services": ["large"]
            },
            {
                "email": "outdoorprint@example.com",
                "business_name": "Outdoor Print Masters",
                "full_name": "Brian Perez",
                "phone": "+254722100023",
                "business_address": "Enterprise Road, Nairobi",
                "business_type": "Large Format & Merchandise",
                "tax_id": "P051234589W",
                "services": ["large", "merch"]
            },
            
            # Mixed service vendors
            {
                "email": "versatileprint@example.com",
                "business_name": "Versatile Print Shop",
                "full_name": "Angela Roberts",
                "phone": "+254722100024",
                "business_address": "Riverside Drive, Nairobi",
                "business_type": "Multi-Service Print Shop",
                "tax_id": "P051234590X",
                "services": ["doc", "photo", "merch"]
            },
            {
                "email": "cityprint@example.com",
                "business_name": "City Print Center",
                "full_name": "George Turner",
                "phone": "+254722100025",
                "business_address": "Ronald Ngala Street, Nairobi",
                "business_type": "Print Shop",
                "tax_id": "P051234591Y",
                "services": ["doc", "photo"]
            },
            {
                "email": "designprint@example.com",
                "business_name": "Design & Print Co",
                "full_name": "Diana Phillips",
                "phone": "+254722100026",
                "business_address": "Lang'ata Road, Nairobi",
                "business_type": "Design & Print Studio",
                "tax_id": "P051234592Z",
                "services": ["doc", "large", "merch"]
            },
            {
                "email": "expressprint@example.com",
                "business_name": "Express Print Services",
                "full_name": "Thomas Campbell",
                "phone": "+254722100027",
                "business_address": "Biashara Street, Nairobi",
                "business_type": "Quick Print Shop",
                "tax_id": "P051234593A1",
                "services": ["doc", "photo", "uniform"]
            },
            {
                "email": "creativehub@example.com",
                "business_name": "Creative Print Hub",
                "full_name": "Emily Parker",
                "phone": "+254722100028",
                "business_address": "Ngong Road, Nairobi",
                "business_type": "Creative Print Studio",
                "tax_id": "P051234594B1",
                "services": ["photo", "large", "merch"]
            },
            {
                "email": "premiumprint@example.com",
                "business_name": "Premium Print Solutions",
                "full_name": "Andrew Evans",
                "phone": "+254722100029",
                "business_address": "Uhuru Highway, Nairobi",
                "business_type": "Premium Print Shop",
                "tax_id": "P051234595C1",
                "services": ["doc", "uniform", "large"]
            },
            {
                "email": "qualityprint@example.com",
                "business_name": "Quality Print Works",
                "full_name": "Jessica Edwards",
                "phone": "+254722100030",
                "business_address": "Waiyaki Way, Nairobi",
                "business_type": "Quality Print Services",
                "tax_id": "P051234596D1",
                "services": ["photo", "uniform", "merch", "large"]
            }
        ]
        
        vendors_created = 0
        for vendor_data in vendors_data:
            # Check if vendor already exists
            existing = Vendor.query.filter_by(email=vendor_data["email"]).first()
            if not existing:
                services = vendor_data["services"]
                # Password is first name + 'pass' (e.g., davidpass, mariapass)
                first_name = vendor_data["full_name"].split()[0].lower()
                password = f"{first_name}pass"
                
                # Build services_offered string from services list
                service_names = []
                if "doc" in services:
                    service_names.append("Document Printing")
                if "photo" in services:
                    service_names.append("Photo Printing")
                if "uniform" in services:
                    service_names.append("Uniforms & Apparel")
                if "merch" in services:
                    service_names.append("Custom Merchandise")
                if "large" in services:
                    service_names.append("Large Format Printing")
                services_offered = ", ".join(service_names)
                
                vendor = Vendor(
                    email=vendor_data["email"],
                    password_hash=generate_password_hash(password),
                    business_name=vendor_data["business_name"],
                    full_name=vendor_data["full_name"],
                    phone=vendor_data["phone"],
                    organization=vendor_data["business_name"],
                    business_address=vendor_data.get("business_address"),
                    business_type=vendor_data.get("business_type"),
                    tax_id=vendor_data.get("tax_id"),
                    services_offered=services_offered,
                    service_document_printing="doc" in services,
                    service_photos="photo" in services,
                    service_uniforms="uniform" in services,
                    service_merchandise="merch" in services,
                    service_large_format="large" in services,
                    active=True
                )
                db.session.add(vendor)
                vendors_created += 1
        
        db.session.commit()
        
        print(f"✅ Successfully created {customers_created} customers and {vendors_created} vendors")
        print("\n📝 Login credentials:")
        print("   Password format: [firstname]pass")
        print("   Examples: johnpass, sarahpass, davidpass")
        print("\n👥 Sample customer logins:")
        print("   - john.doe@example.com / johnpass")
        print("   - sarah.wilson@example.com / sarahpass")
        print("   - michael.brown@example.com / michaelpass")
        print("\n🏪 Sample vendor logins:")
        print("   - printpro@example.com / davidpass (All services)")
        print("   - quickdocs@example.com / jenniferpass (Document printing only)")
        print("   - photoperfect@example.com / amandapass (Photo printing only)")
        print("   - uniformpro@example.com / susanpass (Uniforms only)")
        print("   - brandmerch@example.com / nancypass (Merchandise only)")
        print("   - bigprint@example.com / michellepass (Large format only)")

if __name__ == "__main__":
    seed_users()
