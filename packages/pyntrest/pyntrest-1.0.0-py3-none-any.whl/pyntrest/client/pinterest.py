import requests
import json
import os
import random
import time
from urllib.parse import quote

# List of common user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

class PinterestClient:
    def __init__(self):
        self.base_url = "https://www.pinterest.com/resource/BaseSearchResource/get/"
        self.last_refresh = 0
        self.refresh_interval = 600  # Refresh cookies every 10 minutes
        self.user_agent = random.choice(USER_AGENTS)
        self.headers = {
            "authority": "www.pinterest.com",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.5",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://www.pinterest.com/search/pins/?q=cats",
            "sec-ch-ua": '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "x-app-version": "4c9ae87",
            "x-pinterest-appstate": "active",
            "x-pinterest-pws-handler": "www/search/[scope].js",
            "x-pinterest-source-url": "/search/pins/?q=cats",
            "x-requested-with": "XMLHttpRequest"
        }
        self.refresh_session()

    def refresh_session(self):
        """Refresh the session and cookies to avoid rate limiting"""
        current_time = time.time()
        
        # Only refresh if enough time has passed since last refresh
        if current_time - self.last_refresh >= self.refresh_interval:
            self.session = requests.Session()
            self.user_agent = random.choice(USER_AGENTS)
            self.headers["user-agent"] = self.user_agent
            
            try:
                # Visit homepage to get fresh cookies
                self.session.get("https://www.pinterest.com/")
                # Visit search page to get additional cookies
                self.session.get("https://www.pinterest.com/search/pins/")
                self.last_refresh = current_time
            except Exception as e:
                print(f"Warning: Session refresh failed: {e}")

    def get_image_links(self, query, num_images=5):
        """API method to get just the image links without downloading"""
        self.refresh_session()  # Ensure fresh session
        
        # Build the search options
        options = {
            "query": query,
            "scope": "pins",
            "auto_correction_disabled": False,
            "redux_normalize_feed": True,
            "rs": "ac",
            "source_id": "ac_dEeclegc",
            "appliedProductFilters": "---",
            "filters": None,
            "page_size": num_images
        }
        
        # Build the full request data
        data = {
            "options": options,
            "context": {}
        }

        # URL encode the data and query parameters
        encoded_data = quote(json.dumps(data))
        encoded_source_url = quote(f"/search/pins/?q={query}&rs=ac&source_id=ac_dEeclegc")
        
        # Build the URL with parameters
        url = f"{self.base_url}?source_url={encoded_source_url}&data={encoded_data}"

        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            results = response.json()
            
            if results.get("resource_response", {}).get("data", {}).get("results"):
                images = []
                for item in results["resource_response"]["data"]["results"][:num_images]:
                    if "images" in item and "orig" in item["images"]:
                        image_info = {
                            "url": item["images"]["orig"]["url"],
                            "width": item["images"]["orig"].get("width"),
                            "height": item["images"]["orig"].get("height"),
                            "title": item.get("title", ""),
                            "description": item.get("description", "")
                        }
                        images.append(image_info)
                return images
            return []
            
        except Exception as e:
            print(f"Error searching Pinterest: {e}")
            return []

    def search(self, query, num_images=5):
        """Search and return just the URLs for backward compatibility"""
        results = self.get_image_links(query, num_images)
        return [img["url"] for img in results]

    def get_one_image(self, query):
        """Get a single image quickly"""
        results = self.get_image_links(query, num_images=1)
        return results[0] if results else None

    def get_random_inspiration(self):
        """Get a random image from trending topics"""
        trending_topics = ["nature", "art", "photography", "travel", "food", "home", "fashion", "quotes"]
        random_topic = random.choice(trending_topics)
        results = self.get_image_links(random_topic, num_images=10)
        return random.choice(results) if results else None
