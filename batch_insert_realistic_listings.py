"""
Batch Insert Realistic Sample Listings
Creates one realistic listing for each of the 15 categories with images
Run: python batch_insert_realistic_listings.py <email>
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.settings import settings
from datetime import datetime, timedelta

# Realistic sample listings - one for each category
REALISTIC_LISTINGS = [
    # 1. ELECTRONICS
    {
        "title": "Apple iPhone 14 Pro Max - 256GB Deep Purple",
        "description": "Brand new Apple iPhone 14 Pro Max in stunning Deep Purple color. 256GB storage, A16 Bionic chip, Pro camera system with 48MP Main camera. Dynamic Island, Always-On display, and all-day battery life. Comes with original box, charger, and 1-year Apple warranty. Never used, sealed box. Perfect for professionals and content creators.",
        "price": 385000,
        "city": "Colombo",
        "category": "electronics",
        "tags": ["iphone", "apple", "smartphone", "5g", "pro max", "camera"],
        "features": ["256GB Storage", "A16 Bionic Chip", "48MP Camera", "Dynamic Island", "Face ID", "5G", "MagSafe"],
        "location": {"type": "Point", "coordinates": [79.8612, 6.9271]},
        "images": [
            "https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=800&q=80",
            "https://images.unsplash.com/photo-1663499482523-1c0d97c7af23?w=800&q=80"
        ]
    },
    
    # 2. VEHICLES
    {
        "title": "Toyota Aqua S Grade 2019 - Hybrid",
        "description": "Immaculate Toyota Aqua S Grade 2019 in Pearl White. Only 45,000 km on the odometer. Full service history from authorized Toyota dealer. Excellent fuel economy (25+ km/l). Features include push-start button, reversing camera, alloy wheels, and climate control. Single owner, accident-free. Recently serviced with new tires. Perfect city car with hybrid technology.",
        "price": 5850000,
        "city": "Gampaha",
        "category": "vehicles",
        "tags": ["toyota", "aqua", "hybrid", "fuel efficient", "automatic", "pearl white"],
        "features": ["45,000 km", "Hybrid", "Automatic", "Push Start", "Reverse Camera", "Alloy Wheels", "Full Option"],
        "location": {"type": "Point", "coordinates": [80.0014, 7.0873]},
        "images": [
            "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=800&q=80",
            "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80"
        ]
    },
    
    # 3. REAL ESTATE
    {
        "title": "Luxury 3BR Apartment - Colombo 7 (Cinnamon Gardens)",
        "description": "Stunning 3-bedroom luxury apartment in the heart of Colombo 7, Cinnamon Gardens area. 2,100 sq ft with spacious living areas, modern kitchen with granite countertops, 3 attached bathrooms with premium fixtures. Panoramic city views from the 12th floor. Building amenities include swimming pool, gym, 24/7 security, covered parking for 2 vehicles, and power backup. Walking distance to Royal College, restaurants, and shopping centers. Perfect for families or professionals.",
        "price": 85000,
        "city": "Colombo",
        "category": "real_estate",
        "tags": ["apartment", "luxury", "colombo 7", "3 bedroom", "rent", "furnished"],
        "features": ["3 Bedrooms", "2,100 sq ft", "12th Floor", "Swimming Pool", "Gym", "Parking", "Security", "City View"],
        "location": {"type": "Point", "coordinates": [79.8653, 6.9147]},
        "images": [
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80",
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80"
        ]
    },
    
    # 4. JOBS
    {
        "title": "Senior Full Stack Developer - React & Node.js",
        "description": "Leading tech company in Colombo seeks experienced Senior Full Stack Developer. Requirements: 5+ years experience with React.js, Node.js, MongoDB, and cloud platforms (AWS/Azure). Strong understanding of microservices architecture, RESTful APIs, and modern web technologies. Excellent problem-solving skills and ability to mentor junior developers. Competitive salary range: Rs 250,000 - 350,000 per month plus performance bonuses. Benefits include health insurance, flexible working hours, remote work options, annual training budget, and career growth opportunities.",
        "price": 300000,
        "city": "Colombo",
        "category": "jobs",
        "tags": ["developer", "full stack", "react", "nodejs", "software engineer", "tech job"],
        "features": ["5+ Years Experience", "React.js", "Node.js", "MongoDB", "Remote Option", "Health Insurance", "Training Budget"],
        "location": {"type": "Point", "coordinates": [79.8612, 6.9271]},
        "images": [
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=80"
        ]
    },
    
    # 5. SERVICES
    {
        "title": "Professional Home Cleaning Service - Eco-Friendly",
        "description": "Expert home cleaning service available across Colombo and suburbs. We use 100% eco-friendly, non-toxic cleaning products safe for children and pets. Services include deep cleaning, regular maintenance cleaning, kitchen and bathroom sanitization, window cleaning, and carpet shampooing. Our trained and vetted staff are professional, punctual, and trustworthy. Flexible scheduling - daily, weekly, or monthly packages available. First-time customers get 20% discount. Satisfaction guaranteed or your money back. Contact us for a free quote!",
        "price": 4500,
        "city": "Colombo",
        "category": "services",
        "tags": ["cleaning", "home service", "eco friendly", "professional", "sanitization"],
        "features": ["Eco-Friendly Products", "Trained Staff", "Flexible Schedule", "Satisfaction Guarantee", "Pet Safe", "Licensed & Insured"],
        "location": {"type": "Point", "coordinates": [79.8612, 6.9271]},
        "images": [
            "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&q=80",
            "https://images.unsplash.com/photo-1628177142898-93e36e4e3a50?w=800&q=80"
        ]
    },
    
    # 6. FURNITURE
    {
        "title": "Luxury L-Shape Sofa Set - Italian Leather",
        "description": "Premium L-shaped sofa set made from genuine Italian leather in elegant charcoal grey. This stunning piece features a modern design with deep comfortable seating, stainless steel legs, and removable cushions. Dimensions: L-section 280cm x 180cm. Seats 6-7 people comfortably. Built with solid hardwood frame for durability. Only 6 months old, like new condition. Originally purchased for Rs 285,000, selling due to relocation. Includes matching throw pillows. Perfect centerpiece for modern living rooms.",
        "price": 195000,
        "city": "Kandy",
        "category": "furniture",
        "tags": ["sofa", "leather", "luxury", "living room", "italian", "l-shape"],
        "features": ["Italian Leather", "L-Shape Design", "Seats 6-7", "Removable Cushions", "Hardwood Frame", "Like New", "Modern Design"],
        "location": {"type": "Point", "coordinates": [80.6337, 7.2906]},
        "images": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
            "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800&q=80"
        ]
    },
    
    # 7. CLOTHING
    {
        "title": "Designer Women's Silk Saree Collection - Wedding Special",
        "description": "Exquisite collection of pure silk sarees perfect for weddings and special occasions. Each saree features intricate handloom work with gold zari borders and traditional motifs. Available in multiple colors: royal blue, emerald green, ruby red, and golden beige. Comes with matching blouse piece. Made from 100% pure Kanchipuram silk. These timeless pieces combine traditional craftsmanship with contemporary elegance. Dry clean only. Each saree comes in a protective cover. Perfect gift for weddings, engagements, or festive celebrations.",
        "price": 35000,
        "city": "Colombo",
        "category": "clothing",
        "tags": ["saree", "silk", "wedding", "traditional", "designer", "women's wear"],
        "features": ["Pure Silk", "Handloom Work", "Gold Zari Border", "Blouse Included", "Multiple Colors", "Wedding Special", "Gift Box"],
        "location": {"type": "Point", "coordinates": [79.8612, 6.9271]},
        "images": [
            "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80",
            "https://images.unsplash.com/photo-1583391733981-5aff4c894366?w=800&q=80"
        ]
    },
    
    # 8. BOOKS
    {
        "title": "Complete Harry Potter Box Set - Hardcover First Edition",
        "description": "Rare complete Harry Potter hardcover box set - all 7 books in pristine condition. First edition prints published by Bloomsbury. Books include: Philosopher's Stone, Chamber of Secrets, Prisoner of Azkaban, Goblet of Fire, Order of Phoenix, Half-Blood Prince, and Deathly Hallows. Original dust jackets intact with minimal shelf wear. Pages are crisp and clean with no markings. Perfect for collectors or as a treasured gift for Harry Potter fans. Comes in the original collector's trunk-style box. A magical addition to any library!",
        "price": 45000,
        "city": "Negombo",
        "category": "books",
        "tags": ["harry potter", "books", "hardcover", "first edition", "collection", "jk rowling"],
        "features": ["Complete 7 Book Set", "Hardcover", "First Edition", "Original Dust Jackets", "Collector's Box", "Pristine Condition", "Rare"],
        "location": {"type": "Point", "coordinates": [79.8358, 7.2008]},
        "images": [
            "https://images.unsplash.com/photo-1621351183012-e2f3db3a5aa0?w=800&q=80",
            "https://images.unsplash.com/photo-1589998059171-988d887df646?w=800&q=80"
        ]
    },
    
    # 9. SPORTS
    {
        "title": "Trek Mountain Bike - 29\" Full Suspension",
        "description": "High-performance Trek mountain bike with 29-inch wheels and full suspension system. Perfect for trail riding and mountain adventures. Features Shimano hydraulic disc brakes, 21-speed gear system, aluminum alloy frame (lightweight yet durable), and front suspension fork with lockout. Recently serviced with new brake pads and chain. Includes helmet, water bottle holder, and front/rear lights. Suitable for riders 5'8\" and above. Only used for weekend rides, excellent condition. Great for fitness enthusiasts and adventure seekers!",
        "price": 95000,
        "city": "Kandy",
        "category": "sports",
        "tags": ["mountain bike", "trek", "bicycle", "cycling", "sports", "fitness"],
        "features": ["29-inch Wheels", "Full Suspension", "Shimano Brakes", "21 Speeds", "Aluminum Frame", "Recently Serviced", "Accessories Included"],
        "location": {"type": "Point", "coordinates": [80.6337, 7.2906]},
        "images": [
            "https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800&q=80",
            "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&q=80"
        ]
    },
    
    # 10. PETS
    {
        "title": "Golden Retriever Puppies - Pedigree with Papers",
        "description": "Adorable Golden Retriever puppies ready for their forever homes! 8 weeks old, fully vaccinated, and dewormed. Both parents are registered pedigree Golden Retrievers with excellent temperament and health records (parents can be viewed). Puppies have been vet-checked and come with vaccination certificates and pedigree papers. Socialized with children and other pets. These gentle, intelligent puppies make perfect family companions. Available: 3 males, 2 females. They've been raised in a loving home environment. Serious inquiries only. Lifetime breeder support included.",
        "price": 85000,
        "city": "Mount Lavinia",
        "category": "pets",
        "tags": ["golden retriever", "puppy", "pedigree", "dog", "pet", "vaccinated"],
        "features": ["8 Weeks Old", "Pedigree Papers", "Fully Vaccinated", "Dewormed", "Vet Checked", "Parent Viewing", "Lifetime Support"],
        "location": {"type": "Point", "coordinates": [79.8638, 6.8406]},
        "images": [
            "https://images.unsplash.com/photo-1633722715463-d30f4f325e24?w=800&q=80",
            "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800&q=80"
        ]
    },
    
    # 11. TOYS
    {
        "title": "LEGO Architecture Taj Mahal - 5923 Pieces Collector's Set",
        "description": "Impressive LEGO Architecture Taj Mahal set - one of the largest and most intricate LEGO sets ever created. 5,923 pieces to build an incredibly detailed replica of the iconic monument. Completed model measures 51cm x 41cm x 20cm. This retired collector's set includes detailed instruction booklet and authentic LEGO building experience. All pieces present and accounted for, never been assembled (sealed box). Perfect for adult LEGO enthusiasts, architecture lovers, or as an investment piece. Original retail price was Rs 125,000. A magnificent display piece when completed!",
        "price": 95000,
        "city": "Colombo",
        "category": "toys",
        "tags": ["lego", "collector", "architecture", "building blocks", "taj mahal", "rare"],
        "features": ["5,923 Pieces", "Sealed Box", "Retired Set", "Adult Collector", "Detailed Instructions", "Investment Piece", "Display Model"],
        "location": {"type": "Point", "coordinates": [79.8612, 6.9271]},
        "images": [
            "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800&q=80",
            "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=800&q=80"
        ]
    },
    
    # 12. HOME_GARDEN
    {
        "title": "Automatic Drip Irrigation System - Complete Garden Kit",
        "description": "Professional-grade automatic drip irrigation system perfect for home gardens, balconies, or small farms. Complete kit includes: programmable timer, 50m main hose, 100 drip emitters, connectors, stakes, and pressure regulator. Easy DIY installation with detailed instructions. Save up to 70% water compared to traditional watering. Programmable timer allows you to set watering schedule (up to 4 times per day). Suitable for vegetables, flowers, herbs, and potted plants. Solar-powered timer option available. Covers up to 50 square meters. Durable UV-resistant materials. One-year warranty included.",
        "price": 15000,
        "city": "Gampaha",
        "category": "home_garden",
        "tags": ["irrigation", "garden", "drip system", "automatic", "water saving", "timer"],
        "features": ["Programmable Timer", "50m Coverage", "100 Drip Emitters", "DIY Install", "Water Saving", "UV Resistant", "1 Year Warranty"],
        "location": {"type": "Point", "coordinates": [80.0014, 7.0873]},
        "images": [
            "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80",
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800&q=80"
        ]
    },
    
    # 13. HEALTH_BEAUTY
    {
        "title": "Professional Hair Straightener - Ceramic Tourmaline Plates",
        "description": "Salon-quality professional hair straightener with advanced ceramic tourmaline plates. Heats up in just 30 seconds to temperatures ranging from 150°C to 230°C with digital temperature control. 1-inch floating plates for all hair types and lengths. Ionic technology reduces frizz and adds shine. Auto shut-off safety feature after 60 minutes. 360-degree swivel cord prevents tangling. Dual voltage (110V-240V) - perfect for travel. Used only 3 times, practically brand new. Comes with heat-resistant pouch and original box. Creates smooth, silky, salon-perfect hair at home. Worth Rs 25,000 new.",
        "price": 12500,
        "city": "Colombo",
        "category": "health_beauty",
        "tags": ["hair straightener", "beauty", "salon quality", "ceramic", "ionic", "travel"],
        "features": ["Ceramic Tourmaline", "Digital Control", "Ionic Technology", "Auto Shut-off", "Dual Voltage", "30s Heat Up", "Like New"],
        "location": {"type": "Point", "coordinates": [79.8612, 6.9271]},
        "images": [
            "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800&q=80",
            "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80"
        ]
    },
    
    # 14. FOOD_BEVERAGES
    {
        "title": "Organic Ceylon Cinnamon - Premium Grade A (1kg)",
        "description": "Authentic Sri Lankan organic Ceylon Cinnamon (True Cinnamon) - the finest quality available worldwide. Grade A premium quills sourced directly from certified organic farms in Matale district. Ceylon Cinnamon is known for its sweet, delicate flavor and numerous health benefits (unlike common Cassia cinnamon). Perfect for baking, cooking, tea, and traditional medicine. Hand-rolled quills, minimal coumarin content (safe for daily consumption). Packaged in airtight, food-grade container to preserve freshness and aroma. Free from pesticides, artificial flavors, or additives. Includes recipe booklet with traditional Sri Lankan cinnamon recipes.",
        "price": 3500,
        "city": "Matale",
        "category": "food_beverages",
        "tags": ["cinnamon", "organic", "ceylon", "spices", "grade a", "healthy"],
        "features": ["Grade A Quality", "Certified Organic", "1kg Pack", "Hand-Rolled Quills", "Airtight Container", "Recipe Book", "Pesticide Free"],
        "location": {"type": "Point", "coordinates": [80.6234, 7.4675]},
        "images": [
            "https://images.unsplash.com/photo-1599639957043-f3aa5c986398?w=800&q=80",
            "https://images.unsplash.com/photo-1596040033229-a0b73b7ba2bc?w=800&q=80"
        ]
    },
    
    # 15. OTHER
    {
        "title": "Antique Singer Sewing Machine - 1950s Working Condition",
        "description": "Beautiful antique Singer sewing machine from the 1950s in fully working condition. Classic black body with gold detailing and original wooden cabinet with cast iron treadle base. This iconic piece combines functionality with vintage charm. The machine has been professionally serviced and stitches perfectly. Comes with original accessories including bobbins, needles, and instruction manual. The wooden cabinet features drawers for storage and folds closed to create a beautiful side table. Serial number verified for authenticity. Perfect for sewing enthusiasts, collectors, or as a stunning decorative piece. A true piece of history!",
        "price": 65000,
        "city": "Galle",
        "category": "other",
        "tags": ["antique", "vintage", "singer", "sewing machine", "collectible", "1950s"],
        "features": ["1950s Original", "Working Condition", "Wooden Cabinet", "Cast Iron Base", "Professionally Serviced", "Original Accessories", "Authenticated"],
        "location": {"type": "Point", "coordinates": [80.2170, 6.0535]},
        "images": [
            "https://images.unsplash.com/photo-1597045566677-8cf032d6e4cf?w=800&q=80",
            "https://images.unsplash.com/photo-1613769049987-b31b641f25b1?w=800&q=80"
        ]
    }
]


async def batch_insert_listings(user_email: str):
    """Batch insert realistic sample listings for all categories"""
    print("=" * 80)
    print("BATCH INSERT REALISTIC LISTINGS - ONE PER CATEGORY")
    print("=" * 80)
    
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    
    # Get user
    user = await db.users.find_one({"email": user_email})
    if not user:
        print(f"\n❌ User not found: {user_email}")
        print("Please provide a valid user email.")
        client.close()
        return
    
    user_id = user["_id"]
    print(f"\n📧 User: {user_email}")
    print(f"🆔 User ID: {user_id}")
    print(f"\n📦 Preparing to insert {len(REALISTIC_LISTINGS)} listings...")
    print("-" * 80)
    
    created_count = 0
    failed_count = 0
    
    for i, listing_data in enumerate(REALISTIC_LISTINGS, 1):
        try:
            # Add required fields
            listing_data["userId"] = user_id
            listing_data["posted_date"] = datetime.utcnow()
            listing_data["expires_at"] = datetime.utcnow() + timedelta(days=30)
            
            # Insert listing
            result = await db.listings.insert_one(listing_data.copy())
            created_count += 1
            
            # Display success
            print(f"\n[{i}/{len(REALISTIC_LISTINGS)}] ✅ SUCCESS")
            print(f"  📋 Title: {listing_data['title'][:60]}...")
            print(f"  🆔 ID: {result.inserted_id}")
            print(f"  💰 Price: Rs {listing_data['price']:,}")
            print(f"  📍 City: {listing_data['city']}")
            print(f"  🏷️  Category: {listing_data['category']}")
            print(f"  🖼️  Images: {len(listing_data['images'])}")
            print(f"  🏷️  Tags: {', '.join(listing_data['tags'][:3])}...")
            
        except Exception as e:
            failed_count += 1
            print(f"\n[{i}/{len(REALISTIC_LISTINGS)}] ❌ FAILED")
            print(f"  Title: {listing_data.get('title', 'Unknown')}")
            print(f"  Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("BATCH INSERT SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully created: {created_count} listings")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count} listings")
    print(f"📊 Total listings in database: {await db.listings.count_documents({})}")
    
    # Category breakdown
    print("\n📈 CATEGORY BREAKDOWN:")
    print("-" * 80)
    categories = {}
    for listing in REALISTIC_LISTINGS[:created_count]:
        cat = listing['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"  {category.replace('_', ' ').title()}: {count}")
    
    # View links
    print("\n" + "=" * 80)
    print("🌐 VIEW YOUR LISTINGS:")
    print("=" * 80)
    print(f"  Homepage: http://localhost:5173/")
    print(f"  My Listings: http://localhost:5173/my-listings")
    print(f"  Analytics: http://localhost:5173/analytics")
    
    client.close()
    print("\n✨ Done! Your listings are ready to view.\n")


if __name__ == "__main__":
    print("\n")
    
    if len(sys.argv) < 2:
        print("Usage: python batch_insert_realistic_listings.py <email>")
        print("Example: python batch_insert_realistic_listings.py admin@listings.app")
        print("\nThis will create 15 realistic listings (one for each category) for the specified user.")
    else:
        email = sys.argv[1]
        asyncio.run(batch_insert_listings(email))
