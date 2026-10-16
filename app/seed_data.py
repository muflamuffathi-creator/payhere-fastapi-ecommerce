from sqlalchemy.orm import Session
from app.models.product import Product

SAMPLE_PRODUCTS = [
    # ── SPICES ──────────────────────────────────────────────────────────────
    {
        "name": "Ceylon Cinnamon Alba Grade (100g)",
        "slug": "ceylon-cinnamon-alba-grade",
        "category": "Spices",
        "description": "The rarest pencil-thin quill grade of true Ceylon cinnamon with sweet aroma and low coumarin.",
        "price": 2850.00,
        "stock_quantity": 45,
        "image_url": "https://images.unsplash.com/photo-1509358271058-acd22cc93898?auto=format&fit=crop&w=800&q=80",
        "badge": "Top Seller"
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
        "name": "Whole Black Pepper King Grade (100g)",
        "slug": "black-pepper-king-grade",
        "category": "Spices",
        "description": "Bold, pungent King-grade whole black peppercorns sun-dried at peak ripeness in Sri Lanka's Southern Province for maximum piperine content.",
        "price": 1750.00,
        "stock_quantity": 80,
        "image_url": "https://images.unsplash.com/photo-1595252129732-29948a29ea7f?auto=format&fit=crop&w=800&q=80",
        "badge": "Bold Flavour"
    },
    {
        "name": "Organic Turmeric Finger Powder (150g)",
        "slug": "organic-turmeric-finger-powder",
        "category": "Spices",
        "description": "Stone-ground from naturally cultivated Sri Lankan turmeric fingers. High curcumin content with vivid golden colour and earthy depth.",
        "price": 1200.00,
        "stock_quantity": 70,
        "image_url": "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=800&q=80",
        "badge": "Organic"
    },
    {
        "name": "Sri Lankan Roasted Curry Powder Blend (200g)",
        "slug": "sri-lankan-roasted-curry-powder",
        "category": "Spices",
        "description": "Traditional dark-roasted blend of coriander, cumin, fennel, chilli, curry leaf and cinnamon — the soul of authentic Sri Lankan rice & curry.",
        "price": 980.00,
        "stock_quantity": 90,
        "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=800&q=80",
        "badge": "Authentic"
    },

    # ── CEYLON TEA ───────────────────────────────────────────────────────────
    {
        "name": "Single Origin Nuwara Eliya BOP Tea (250g)",
        "slug": "single-origin-nuwara-eliya-bop-tea",
        "category": "Ceylon Tea",
        "description": "High-grown orthodox pure Ceylon black tea from 6,000+ ft elevations in Nuwara Eliya. Delicate golden liquor with floral notes.",
        "price": 3400.00,
        "stock_quantity": 60,
        "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
        "badge": "Single Origin"
    },
    {
        "name": "Organic Ceylon Green Tea — Sencha Style (100g)",
        "slug": "organic-ceylon-green-tea-sencha",
        "category": "Ceylon Tea",
        "description": "Unoxidised Ceylon green tea leaves processed in Japanese sencha style, delivering grassy sweetness and a light emerald brew.",
        "price": 2750.00,
        "stock_quantity": 40,
        "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=800&q=80",
        "badge": "Organic"
    },
    {
        "name": "Uva Highlands Silver Tips White Tea (50g)",
        "slug": "uva-highlands-silver-tips-white-tea",
        "category": "Ceylon Tea",
        "description": "Rare hand-plucked silver tip buds from the Uva province — minimally processed to preserve delicate floral notes and antioxidants.",
        "price": 5800.00,
        "stock_quantity": 15,
        "image_url": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?auto=format&fit=crop&w=800&q=80",
        "badge": "Rare & Limited"
    },
    {
        "name": "Sabaragamuwa Malty Black Tea (150g)",
        "slug": "sabaragamuwa-smoky-black-tea",
        "category": "Ceylon Tea",
        "description": "Low-grown Sabaragamuwa tea with rich, malty depth and slight smokiness — perfect for breakfast or iced brewing.",
        "price": 2100.00,
        "stock_quantity": 50,
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=800&q=80",
        "badge": "Malty & Bold"
    },

    # ── ARTISANAL FOODS ──────────────────────────────────────────────────────
    {
        "name": "Pure Sinharaja Wild Rainforest Honey (350g)",
        "slug": "sinharaja-wild-rainforest-honey",
        "category": "Artisanal Foods",
        "description": "Unfiltered raw forest honey sustainably foraged from wild blossoms bordering the UNESCO Sinharaja Biosphere Reserve.",
        "price": 4200.00,
        "stock_quantity": 25,
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=80",
        "badge": "100% Organic"
    },
    {
        "name": "Ceylon Kithul Treacle — Pure Artisanal (750ml)",
        "slug": "ceylon-kithul-treacle-pure-artisanal",
        "category": "Artisanal Foods",
        "description": "Authentic sap tapped from Caryota urens palm flowers and slow-simmered over wood fires. Zero refined sugars.",
        "price": 2600.00,
        "stock_quantity": 40,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80",
        "badge": "Pure"
    },
    {
        "name": "Coconut Jaggery Rounds — Unrefined (500g)",
        "slug": "coconut-jaggery-rounds-unrefined",
        "category": "Artisanal Foods",
        "description": "Traditional palm sugar rounds made by boiling fresh coconut flower nectar. Caramel-butterscotch sweetness, perfect for hoppers and desserts.",
        "price": 1450.00,
        "stock_quantity": 60,
        "image_url": "https://images.unsplash.com/photo-1627484986410-f12b23e0d39f?auto=format&fit=crop&w=800&q=80",
        "badge": "Natural Sweet"
    },
    {
        "name": "Sri Lankan Jak Seed Flour (400g)",
        "slug": "sri-lankan-jak-seed-flour",
        "category": "Artisanal Foods",
        "description": "Nutritious gluten-free flour milled from dried jackfruit seeds. High fibre and protein. Ideal for rotis, pancakes and baking.",
        "price": 890.00,
        "stock_quantity": 55,
        "image_url": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=800&q=80",
        "badge": "Gluten Free"
    },

    # ── GOURMET SNACKS ───────────────────────────────────────────────────────
    {
        "name": "Roasted Ceylon Cashews — Hot Chili & Lime (200g)",
        "slug": "roasted-ceylon-cashews-hot-chili-lime",
        "category": "Gourmet Snacks",
        "description": "Whole jumbo Sri Lankan cashews oven-roasted to crisp golden perfection and dusted with Jaffna red chili and kaffir lime zest.",
        "price": 3950.00,
        "stock_quantity": 35,
        "image_url": "https://images.unsplash.com/photo-1536591375315-1b8368903277?auto=format&fit=crop&w=800&q=80",
        "badge": "Spicy Favorite"
    },
    {
        "name": "Coconut Oil Murukku Crisps — Traditional (150g)",
        "slug": "coconut-oil-murukku-crisps",
        "category": "Gourmet Snacks",
        "description": "Crispy spiral murukku deep-fried in pure coconut oil with roasted cumin and sesame seeds. A beloved Sri Lankan snack.",
        "price": 720.00,
        "stock_quantity": 100,
        "image_url": "https://images.unsplash.com/photo-1519676867240-f03562e64548?auto=format&fit=crop&w=800&q=80",
        "badge": "Local Favourite"
    },
    {
        "name": "Banana Chips — Spiced Jaggery Glaze (180g)",
        "slug": "banana-chips-spiced-jaggery-glaze",
        "category": "Gourmet Snacks",
        "description": "Thin-sliced Embul banana crisps glazed in cinnamon-spiced kithul jaggery syrup, finished with a sprinkle of sea salt.",
        "price": 650.00,
        "stock_quantity": 120,
        "image_url": "https://images.unsplash.com/photo-1528825871115-3581a5387919?auto=format&fit=crop&w=800&q=80",
        "badge": "Sweet & Crunchy"
    },

    # ── HANDCRAFTS ───────────────────────────────────────────────────────────
    {
        "name": "Dumbara Handloom Laptop Tote Bag",
        "slug": "dumbara-handloom-laptop-tote-bag",
        "category": "Handcrafts",
        "description": "Eco-friendly handwoven heavy-cotton tote with traditional Dumbara geometric weave patterns and a padded 15-inch laptop pocket.",
        "price": 6500.00,
        "stock_quantity": 20,
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80",
        "badge": "Handmade"
    },
    {
        "name": "Brass Oil Lamp — Traditional Kuththuvilakku",
        "slug": "brass-oil-lamp-kuththuvilakku",
        "category": "Handcrafts",
        "description": "Hand-cast solid brass five-arm oil lamp symbolic of Sri Lankan heritage. Ideal for home décor and religious ceremonies.",
        "price": 8900.00,
        "stock_quantity": 12,
        "image_url": "https://images.unsplash.com/photo-1574180566232-aaad1b5b8450?auto=format&fit=crop&w=800&q=80",
        "badge": "Heritage Piece"
    },
    {
        "name": "Hand-Painted Wooden Elephant Figurine",
        "slug": "hand-painted-wooden-elephant-figurine",
        "category": "Handcrafts",
        "description": "Sustainably sourced Mahogany elephant intricately carved and hand-painted with traditional Perahera tusker motifs by Kandy artisans.",
        "price": 3200.00,
        "stock_quantity": 30,
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=800&q=80",
        "badge": "Artisan Made"
    },
    {
        "name": "Batik Silk Scarf — Kandyan Lotus Motif",
        "slug": "batik-silk-scarf-kandyan-lotus",
        "category": "Handcrafts",
        "description": "Lightweight 100% silk scarf hand-batik printed by Kandy craftswomen with the iconic blue lotus pattern. Each piece is one of a kind.",
        "price": 4750.00,
        "stock_quantity": 18,
        "image_url": "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?auto=format&fit=crop&w=800&q=80",
        "badge": "One of a Kind"
    },

    # ── WELLNESS ─────────────────────────────────────────────────────────────
    {
        "name": "Virgin Coconut Cold-Pressed Oil (500ml)",
        "slug": "virgin-coconut-cold-pressed-oil",
        "category": "Wellness",
        "description": "Centrifuged cold-pressed extra-virgin coconut oil from fresh kernel meat harvested in the Coconut Triangle.",
        "price": 1950.00,
        "stock_quantity": 55,
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
        "badge": "Eco Friendly"
    },
    {
        "name": "Moringa Leaf Powder — Raw Superfood (200g)",
        "slug": "moringa-leaf-powder-raw-superfood",
        "category": "Wellness",
        "description": "Pure sun-dried and stone-milled Moringa oleifera leaf powder from organic farms in North-Central Province. Rich in iron, calcium and Vitamin C.",
        "price": 1680.00,
        "stock_quantity": 65,
        "image_url": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?auto=format&fit=crop&w=800&q=80",
        "badge": "Superfood"
    },
    {
        "name": "Neem & Turmeric Ayurvedic Soap Bar (100g)",
        "slug": "neem-turmeric-ayurvedic-soap",
        "category": "Wellness",
        "description": "Cold-process handmade soap blending antibacterial neem extract with golden turmeric and coconut oil. No SLS, no parabens.",
        "price": 550.00,
        "stock_quantity": 150,
        "image_url": "https://images.unsplash.com/photo-1607006344380-b6775a0824a7?auto=format&fit=crop&w=800&q=80",
        "badge": "Ayurvedic"
    },
    {
        "name": "Ceylon Gotukola Herbal Capsules (60 caps)",
        "slug": "ceylon-gotukola-herbal-capsules",
        "category": "Wellness",
        "description": "Standardised Centella asiatica (Gotukola) vegan capsules — a revered Sri Lankan Ayurvedic herb for memory, skin and circulation.",
        "price": 2200.00,
        "stock_quantity": 45,
        "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=800&q=80",
        "badge": "Ayurvedic"
    },
]


def seed_database(db: Session):
    """Insert any products not yet in the database (matched by slug).
    Safe to run multiple times — never duplicates or deletes existing data.
    """
    existing_slugs = {slug for (slug,) in db.query(Product.slug).all()}
    new_products = [p for p in SAMPLE_PRODUCTS if p["slug"] not in existing_slugs]

    if new_products:
        for p_data in new_products:
            db.add(Product(**p_data))
        db.commit()
        print(f"[seed] ✅ Added {len(new_products)} new product(s) to the catalogue.")
    else:
        print("[seed] Catalogue is up-to-date — no new products to add.")
