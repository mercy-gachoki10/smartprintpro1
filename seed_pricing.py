"""
Seed pricing data into the database
"""
from app import app
from models import ServicePrice, db

PRICING_DATA = [
    # Document Printing
    {"category": "Document Printing", "service_name": "Black & White (A4)", "min": 2, "max": 5, "unit": "per page", "desc": "Standard office paper"},
    {"category": "Document Printing", "service_name": "Color (A4)", "min": 8, "max": 12, "unit": "per page", "desc": "Standard office paper"},
    {"category": "Document Printing", "service_name": "Black & White (A3)", "min": 5, "max": 8, "unit": "per page", "desc": "Larger format"},
    {"category": "Document Printing", "service_name": "Color (A3)", "min": 15, "max": 25, "unit": "per page", "desc": "Larger format"},
    
    # Pictures / Photos
    {"category": "Pictures / Photos", "service_name": "Standard photo print (4x6)", "min": 30, "max": 50, "unit": "per photo", "desc": "Glossy finish"},
    {"category": "Pictures / Photos", "service_name": "Large photo print (A4)", "min": 150, "max": 250, "unit": "per photo", "desc": "Poster-size"},
    {"category": "Pictures / Photos", "service_name": "Extra-large photo (A3)", "min": 300, "max": 500, "unit": "per photo", "desc": "Wall-size"},
    {"category": "Pictures / Photos", "service_name": "Canvas print (A2/A1)", "min": 1500, "max": 3000, "unit": "per photo", "desc": "Premium wall art"},
    
    # Framing Options
    {"category": "Framing Options", "service_name": "Basic plastic frame (A4)", "min": 300, "max": 500, "unit": "per frame", "desc": "Budget option"},
    {"category": "Framing Options", "service_name": "Wooden frame (A4)", "min": 500, "max": 800, "unit": "per frame", "desc": "Classic look"},
    {"category": "Framing Options", "service_name": "Wooden frame (A3)", "min": 800, "max": 1200, "unit": "per frame", "desc": "Larger format"},
    {"category": "Framing Options", "service_name": "Decorative frame (A4/A3)", "min": 1000, "max": 2000, "unit": "per frame", "desc": "Ornate design"},
    {"category": "Framing Options", "service_name": "Canvas stretch frame (A2/A1)", "min": 2000, "max": 4000, "unit": "per frame", "desc": "For canvas prints"},
    
    # Uniforms
    {"category": "Uniforms", "service_name": "Polo shirt with logo (embroidery)", "min": 800, "max": 1200, "unit": "per item", "desc": "Corporate uniforms"},
    {"category": "Uniforms", "service_name": "T-shirt with screen print", "min": 500, "max": 800, "unit": "per item", "desc": "Staff/event wear"},
    {"category": "Uniforms", "service_name": "Branded caps", "min": 300, "max": 500, "unit": "per item", "desc": "Promotional"},
    {"category": "Uniforms", "service_name": "Hoodies with embroidery", "min": 1500, "max": 2500, "unit": "per item", "desc": "Premium option"},
    
    # Banners
    {"category": "Banners (Digital & Vinyl)", "service_name": "Small banner (A2)", "min": 1000, "max": 2000, "unit": "per banner", "desc": "Indoor use"},
    {"category": "Banners (Digital & Vinyl)", "service_name": "Medium banner (A1)", "min": 2500, "max": 4000, "unit": "per banner", "desc": "Event signage"},
    {"category": "Banners (Digital & Vinyl)", "service_name": "Large outdoor vinyl (A0/3m x 1m)", "min": 5000, "max": 8000, "unit": "per banner", "desc": "Outdoor advertising"},
    
    # Signage
    {"category": "Signage", "service_name": "Acrylic signage (small)", "min": 2000, "max": 4000, "unit": "per sign", "desc": "Office door signs"},
    {"category": "Signage", "service_name": "Vinyl signage (medium)", "min": 5000, "max": 10000, "unit": "per sign", "desc": "Shopfront"},
    {"category": "Signage", "service_name": "Billboards (per sqm)", "min": 2000, "max": 3500, "unit": "per sqm", "desc": "Outdoor advertising"},
    
    # Flyers & Brochures
    {"category": "Flyers & Brochures", "service_name": "Flyers (A5, 100 copies)", "min": 1500, "max": 2500, "unit": "per batch", "desc": "Bulk discount available"},
    {"category": "Flyers & Brochures", "service_name": "Brochures (A4, folded, 100 copies)", "min": 3000, "max": 5000, "unit": "per batch", "desc": "Glossy paper"},
    {"category": "Flyers & Brochures", "service_name": "Event prints (posters A3, 50 copies)", "min": 2500, "max": 4000, "unit": "per batch", "desc": "Promotional"},
    
    # Custom Merchandise
    {"category": "Custom Merchandise", "service_name": "T-shirts (custom print)", "min": 500, "max": 800, "unit": "per item", "desc": "Screen or DTG printing"},
    {"category": "Custom Merchandise", "service_name": "Hoodies (custom print)", "min": 1500, "max": 2500, "unit": "per item", "desc": "Embroidery or DTG"},
    {"category": "Custom Merchandise", "service_name": "Caps (embroidered logo)", "min": 300, "max": 500, "unit": "per item", "desc": "Promotional"},
    {"category": "Custom Merchandise", "service_name": "Embroidery (per logo)", "min": 200, "max": 400, "unit": "per logo", "desc": "Add-on service"},
    
    # Packaging & Labels
    {"category": "Packaging & Labels", "service_name": "Packaging boxes (small, 50 pcs)", "min": 2500, "max": 4000, "unit": "per batch", "desc": "Custom printed"},
    {"category": "Packaging & Labels", "service_name": "Packaging boxes (large, 50 pcs)", "min": 5000, "max": 8000, "unit": "per batch", "desc": "Heavy-duty"},
    {"category": "Packaging & Labels", "service_name": "Labels (roll of 500)", "min": 1500, "max": 3000, "unit": "per roll", "desc": "Stickers for branding"},
    {"category": "Packaging & Labels", "service_name": "Custom boxes (premium design, 50 pcs)", "min": 8000, "max": 12000, "unit": "per batch", "desc": "Luxury packaging"},
]


def seed_prices():
    """Seed pricing data into database"""
    with app.app_context():
        # Check if prices already exist
        existing_count = ServicePrice.query.count()
        if existing_count > 0:
            print(f"✅ Pricing data already exists ({existing_count} entries)")
            return
        
        print("🌱 Seeding pricing data...")
        
        for price_data in PRICING_DATA:
            service_price = ServicePrice(
                category=price_data["category"],
                service_name=price_data["service_name"],
                unit_price_min=price_data["min"],
                unit_price_max=price_data["max"],
                unit=price_data["unit"],
                description=price_data["desc"],
                active=True
            )
            db.session.add(service_price)
        
        db.session.commit()
        print(f"✅ Successfully seeded {len(PRICING_DATA)} price entries")


if __name__ == "__main__":
    seed_prices()
