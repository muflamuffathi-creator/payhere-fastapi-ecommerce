from sqlalchemy.orm import Session
from app.models.product import Product

SAMPLE_PRODUCTS = [
    {
        "name": "Ceylon Cinnamon Alba Grade (100g)",
        "slug": "ceylon-cinnamon-alba-grade",
        "category": "Spices",
        "description": "The rarest and most prized pencil-thin quill grade of true Ceylon cinnamon (Cinnamomum verum) with sweet aroma and low coumarin.",
        "price": 2850.00,
        "stock_quantity": 45,
        "image_url": "https://images.unsplash.com/photo-1509358271058-acd22cc93898?auto=format&fit=crop&w=800&q=80",
        "badge": "Top Seller"
    },
    {
        "name": "Single Origin Nuwara Eliya BOP Tea (250g)",
        "slug": "single-origin-nuwara-eliya-bop-tea",
        "category": "Ceylon Tea",
        "description": "High-grown orthodox pure Ceylon black tea harvested from 6,000+ ft elevations in Nuwara Eliya, renowned for delicate golden liquor.",
        "price": 3400.00,
        "stock_quantity": 60,
        "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
        "badge": "Single Origin"
    },
    {
        "name": "Roasted Ceylon Cashews - Hot Chili & Lime (200g)",
        "slug": "roasted-ceylon-cashews-hot-chili-lime",
        "category": "Gourmet Snacks",
        "description": "Whole jumbo Sri Lankan cashews oven roasted to crisp golden perfection and dusted with Jaffna red chili and kaffir lime zest.",
        "price": 3950.00,
        "stock_quantity": 35,
        "image_url": "https://images.unsplash.com/photo-1536591375315-1b8368903277?auto=format&fit=crop&w=800&q=80",
        "badge": "Spicy Favorite"
    },
    {
        "name": "Pure Sinharaja Wild Rainforest Honey (350g)",
        "slug": "sinharaja-wild-rainforest-honey",
        "category": "Artisanal Foods",
        "description": "Unfiltered raw forest bee honey sustainably foraged from wild blossoms bordering the UNESCO Sinharaja Biosphere reserve.",
        "price": 4200.00,
        "stock_quantity": 25,
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=80",
        "badge": "100% Organic"
    },
    {
        "name": "Jumbo Green Cardamom Pods (100g)",
        "slug": "jumbo-green-cardamom-pods",
        "category": "Spices",
        "description": "Hand-sorted premium jumbo green cardamom pods from the Central Highlands, bursting with essential oils and intense fragrance.",
        "price": 4800.00,
        "stock_quantity": 30,
        "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=800&q=80",
        "badge": "Premium"
    },
    {
        "name": "Dumbara Handloom Laptop Tote Bag",
        "slug": "dumbara-handloom-laptop-tote-bag",
        "category": "Handcrafts",
        "description": "Eco-friendly handwoven heavy cotton tote featuring traditional Dumbara geometric weave patterns. Padded 15-inch laptop pocket.",
        "price": 6500.00,
        "stock_quantity": 20,
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80",
        "badge": "Handmade"
    },
    {
        "name": "Ceylon Kithul Treacle - Pure Artisanal (750ml)",
        "slug": "ceylon-kithul-treacle-pure-artisanal",
        "category": "Artisanal Foods",
        "description": "Authentic sap tapped from Caryota urens (Caryota palm) flowers and slow-simmered over wood fires. Zero refined sugars.",
        "price": 2600.00,
        "stock_quantity": 40,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80",
        "badge": "Pure"
    },
    {
        "name": "Virgin Coconut Cold-Pressed Oil (500ml)",
        "slug": "virgin-coconut-cold-pressed-oil",
        "category": "Wellness",
        "description": "Centrifuged cold-pressed extra-virgin coconut oil produced from fresh kernel meat within hours of picking in the Coconut Triangle.",
        "price": 1950.00,
        "stock_quantity": 55,
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
        "badge": "Eco Friendly"
    }
]

def seed_database(db: Session):
    """Seed initial catalog items if the database is currently empty."""
    existing_count = db.query(Product).count()
    if existing_count == 0:
        for p_data in SAMPLE_PRODUCTS:
            product = Product(**p_data)
            db.add(product)
        db.commit()
