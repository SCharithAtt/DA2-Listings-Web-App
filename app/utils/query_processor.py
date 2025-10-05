"""Query preprocessing and expansion utilities for improved semantic search"""
import re
from typing import Dict, List

# Common synonyms and search term mappings
SYNONYM_MAP: Dict[str, List[str]] = {
    "apple phone": ["iphone", "ios phone", "apple smartphone"],
    "apple": ["iphone", "ios", "apple inc", "apple device"],
    "samsung phone": ["samsung", "galaxy", "android samsung"],
    "android phone": ["android smartphone", "google android", "android device"],
    "oneplus": ["one plus", "oneplus phone", "android oneplus"],
    "one plus": ["oneplus", "oneplus device"],
    "car": ["vehicle", "automobile", "motor vehicle", "auto"],
    "bike": ["bicycle", "motorcycle", "two wheeler"],
    "motorcycle": ["bike", "motorbike", "two wheeler"],
    "boat": ["watercraft", "vessel", "marine vehicle", "water vehicle"],
    "dog": ["canine", "puppy", "pet dog", "dog pet"],
    "cat": ["feline", "kitten", "pet cat", "cat pet"],
    "pet": ["animal", "companion animal"],
    "laptop": ["notebook", "computer", "portable computer", "notebook computer"],
    "phone": ["smartphone", "mobile", "cell phone", "mobile phone"],
    "tv": ["television", "smart tv", "display"],
    "house": ["home", "property", "residence", "dwelling"],
    "apartment": ["flat", "unit", "condo"],
    "furniture": ["furnishing", "home furniture"],
    "clothes": ["clothing", "apparel", "garments", "wear"],
    "book": ["books", "literature", "reading material"],
    "toy": ["toys", "plaything", "children toy"],
    "food": ["edible", "cuisine", "meal"],
    "game": ["gaming", "video game", "board game"],
}

# Brand to product category mappings
BRAND_PRODUCTS: Dict[str, List[str]] = {
    "apple": ["iphone", "ipad", "macbook", "airpods", "apple watch", "imac"],
    "samsung": ["galaxy", "samsung phone", "samsung tablet", "samsung tv"],
    "oneplus": ["oneplus phone", "one plus device", "android phone"],
    "one plus": ["oneplus phone", "oneplus device", "android phone"],
    "lexus": ["lexus car", "luxury vehicle", "toyota luxury", "premium car"],
    "toyota": ["toyota car", "toyota vehicle", "automobile"],
    "honda": ["honda car", "honda vehicle", "motorcycle"],
    "bmw": ["bmw car", "luxury car", "german car"],
    "mercedes": ["mercedes car", "luxury vehicle", "german car"],
    "nike": ["nike shoes", "sportswear", "athletic wear"],
    "adidas": ["adidas shoes", "sportswear", "athletic wear"],
    "sony": ["sony electronics", "playstation", "sony tv"],
    "lg": ["lg electronics", "lg tv", "lg appliance"],
}

# Category-specific expansions
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "electronics": ["electronic device", "gadget", "tech", "technology"],
    "vehicles": ["car", "auto", "automobile", "transport", "vehicle"],
    "pets": ["animal", "pet", "companion", "dog", "cat"],
    "furniture": ["home furniture", "furnishing", "household"],
    "clothing": ["clothes", "apparel", "wear", "garment", "fashion"],
    "books": ["book", "literature", "reading", "publication"],
    "sports": ["sporting goods", "athletic", "fitness", "sports equipment"],
    "toys": ["toy", "plaything", "children", "kids"],
    "home_garden": ["home", "garden", "house", "yard", "outdoor"],
    "health_beauty": ["health", "beauty", "cosmetics", "wellness", "personal care"],
    "food_beverages": ["food", "drink", "beverage", "edible", "cuisine"],
}


def expand_query(query: str) -> str:
    """
    Expand query with synonyms and related terms
    
    Args:
        query: Original search query
        
    Returns:
        Expanded query with synonyms separated by pipes
    """
    query_lower = query.lower().strip()
    expanded_terms = [query]
    
    # Check for direct synonym matches
    for key, synonyms in SYNONYM_MAP.items():
        if key in query_lower:
            expanded_terms.extend(synonyms)
    
    # Check for brand mentions and add product types
    for brand, products in BRAND_PRODUCTS.items():
        if brand in query_lower:
            expanded_terms.extend(products)
    
    # Check for category keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category.replace("_", " ") in query_lower:
            expanded_terms.extend(keywords)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_terms = []
    for term in expanded_terms:
        term_normalized = term.lower()
        if term_normalized not in seen:
            seen.add(term_normalized)
            unique_terms.append(term)
    
    return " | ".join(unique_terms)


def preprocess_query(query: str) -> str:
    """
    Clean, normalize, and expand a search query
    
    Args:
        query: Raw search query from user
        
    Returns:
        Preprocessed and expanded query ready for embedding
    """
    # Remove special characters but keep spaces and hyphens
    cleaned = re.sub(r'[^\w\s-]', ' ', query)
    
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Convert to lowercase for matching
    cleaned = cleaned.lower()
    
    # Expand with synonyms and related terms
    expanded = expand_query(cleaned)
    
    return expanded


def extract_keywords(query: str) -> List[str]:
    """
    Extract important keywords from query for filtering
    
    Args:
        query: Search query
        
    Returns:
        List of keywords
    """
    # Remove common stop words
    stop_words = {
        'a', 'an', 'the', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or',
        'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'can',
        'could', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'this', 'that', 'these', 'those', 'what', 'which', 'who',
        'when', 'where', 'why', 'how'
    }
    
    # Clean and tokenize
    cleaned = re.sub(r'[^\w\s]', ' ', query.lower())
    words = cleaned.split()
    
    # Filter stop words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords
