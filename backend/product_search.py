"""
RapidAPI Product Search Service for StyleAI
Searches for clothing items based on style recommendations
"""

import os
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Product:
    """Represents a product from the search API"""
    title: str
    price: str
    image_url: str
    product_url: str
    source: str
    rating: Optional[float] = None
    rating_count: Optional[int] = None

class ProductSearcher:
    """RapidAPI Product Search integration for outfit recommendations"""
    
    def __init__(self):
        """Initialize RapidAPI client"""
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('RAPIDAPI_HOST')
        self.api_url = os.getenv('PRODUCT_SEARCH_API_URL')
        
        if not all([self.api_key, self.api_host, self.api_url]):
            print("Warning: RapidAPI credentials not found. Product search will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
    
    def search_products(self, query: str, max_price: Optional[int] = None, 
                       num_results: int = 5) -> List[Product]:
        """
        Search for products using RapidAPI
        
        Args:
            query: Search term (e.g., "women's blouse", "black jeans")
            max_price: Maximum price filter
            num_results: Number of products to return
            
        Returns:
            List of Product objects
        """
        if not self.enabled:
            print("Product search disabled - missing API credentials")
            return []
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-rapidapi-host': self.api_host,
            'x-rapidapi-key': self.api_key
        }
        
        # Prepare search data
        data = f'query={query}&num={num_results}'
        if max_price:
            data += f'&max_price={max_price}'
        
        try:
            response = requests.post(self.api_url, headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                products = result.get('products', [])
                return self._parse_products(products)
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Product search error: {e}")
            return []
    
    def _parse_products(self, products_data: List[Dict]) -> List[Product]:
        """Parse API response into Product objects"""
        products = []
        
        for item in products_data:
            try:
                product = Product(
                    title=item.get('title', 'No title'),
                    price=item.get('price', 'Price not available'),
                    image_url=item.get('imageUrl', ''),
                    product_url=item.get('link', ''),
                    source=item.get('source', 'Unknown'),
                    rating=item.get('rating'),
                    rating_count=item.get('ratingCount')
                )
                products.append(product)
            except Exception as e:
                print(f"Error parsing product: {e}")
                continue
        
        return products
    
    def search_for_outfit_item(self, item_description: str, user_preferences: Dict,
                              max_results: int = 3) -> List[Product]:
        """
        Search for products based on outfit recommendation
        
        Args:
            item_description: Description from recommendation engine (e.g., "wrap dress")
            user_preferences: User preferences including colors and budget
            max_results: Number of products to return
            
        Returns:
            List of Product objects
        """
        # Build search query
        search_query = self._build_search_query(item_description, user_preferences)
        
        # Get price range from budget preference
        max_price = self._get_max_price(user_preferences.get('budget_range', 'mid'))
        
        return self.search_products(
            query=search_query,
            max_price=max_price,
            num_results=max_results
        )
    
    def _build_search_query(self, item_description: str, user_preferences: Dict) -> str:
        """Build search query from item description and user preferences"""
        # Map common recommendation terms to better search terms
        search_mapping = {
            'tank tops': 'tank top',
            'wrap tops': 'wrap blouse',
            'button-downs': 'button down shirt',
            'bootcut': 'bootcut jeans',
            'wide leg': 'wide leg pants',
            'a-line': 'a-line dress',
            'wrap': 'wrap dress',
            'fit and flare': 'fit and flare dress',
            'pencil': 'pencil skirt',
            'circle': 'circle skirt',
            'cargo pants': 'cargo pants',
            'professional heels': 'dress heels',
            'heels or dressy sandals': 'dress sandals',
            'statement jewelry': 'statement necklace',
            'delicate jewelry': 'delicate necklace'
        }
        
        # Use mapped term if available, otherwise use original
        search_term = search_mapping.get(item_description.lower(), item_description)
        
        # Build base query
        query = f"women's {search_term}"
        
        # Add color preferences to search
        colors = user_preferences.get('favorite_colors', '')
        if colors:
            if isinstance(colors, str):
                color_list = [c.strip() for c in colors.split(',')]
            else:
                color_list = colors
            
            # Add the first preferred color to search (if it's a clothing item, not shoes/accessories)
            if color_list and not any(word in search_term.lower() for word in ['shoes', 'heels', 'sandals', 'jewelry', 'bag']):
                query = f"{color_list[0]} {query}"
        
        return query
    
    def _get_max_price(self, budget_range: str) -> Optional[int]:
        """Convert budget range to maximum price"""
        budget_mapping = {
            'low': 50,
            'mid': 150,
            'high': 500
        }
        return budget_mapping.get(budget_range)
    
    def search_complete_outfit(self, outfit_recommendations: Dict, 
                              user_preferences: Dict) -> Dict[str, List[Product]]:
        """
        Search for all items in an outfit recommendation
        
        Args:
            outfit_recommendations: Outfit dict from recommendation engine
            user_preferences: User preferences
            
        Returns:
            Dict mapping item type to list of products
        """
        outfit_products = {}
        
        for item_type, item_description in outfit_recommendations.items():
            if item_description and item_description != 'N/A':
                products = self.search_for_outfit_item(
                    item_description, 
                    user_preferences,
                    max_results=3
                )
                if products:  # Only add if we found products
                    outfit_products[item_type] = products
        
        return outfit_products