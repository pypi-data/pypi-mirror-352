"""
Command line interface for Pyntrest
"""

import argparse
import os
import sys
from .client.pinterest import PinterestClient

def download_image(url, output_dir="downloads"):
    """Download a single image"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    try:
        import requests
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filename = os.path.join(output_dir, url.split('/')[-1])
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filename
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Pyntrest - Pinterest Image Search CLI")
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands", required=True)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for images")
    search_parser.add_argument("query", help="Search query for Pinterest images")
    search_parser.add_argument("-n", "--num", type=int, default=5, help="Number of images (default: 5)")
    search_parser.add_argument("-o", "--output", default="downloads", help="Output directory (default: downloads)")
    
    # Random image command
    random_parser = subparsers.add_parser("random", help="Get random images")
    random_parser.add_argument("query", nargs="?", help="Optional search query")
    random_parser.add_argument("-n", "--num", type=int, default=1, help="Number of random images (default: 1)")
    random_parser.add_argument("-o", "--output", default="downloads", help="Output directory")
    
    # Inspiration command
    inspire_parser = subparsers.add_parser("inspire", help="Get inspiration images")
    inspire_parser.add_argument("-n", "--num", type=int, default=1, help="Number of inspiration images (default: 1)")
    inspire_parser.add_argument("-o", "--output", default="downloads", help="Output directory")
    
    args = parser.parse_args()
    client = PinterestClient()
    
    try:
        if args.command == "search":
            print(f"Searching Pinterest for '{args.query}'...")
            urls = client.get_image_links(args.query, args.num)
            if not urls:
                print("No images found!")
                return
        if args.command == "random":
            if args.query:
                print(f"Getting {args.num} random images for '{args.query}'...")
                urls = client.get_image_links(args.query, args.num * 2)  # Get extra for randomization
                if not urls:
                    print("No images found!")
                    return
                # Randomly select the requested number of images
                import random
                urls = random.sample(urls, min(args.num, len(urls)))
            else:
                print(f"Getting {args.num} random inspiration images...")
                urls = []
                for _ in range(args.num):
                    result = client.get_random_inspiration()
                    if result:
                        urls.append(result)
        
        elif args.command == "inspire":
            print(f"Getting {args.num} inspiration images...")
            urls = []
            for _ in range(args.num):
                result = client.get_random_inspiration()
                if result:
                    urls.append(result)
        
        else:  # Default search command
            print(f"Searching Pinterest for '{args.query}'...")
            urls = client.get_image_links(args.query, args.num)
            if not urls:
                print("No images found!")
                return
        
        print(f"Found {len(urls)} images. Downloading...")
        
        for i, image in enumerate(urls, 1):
            print(f"Downloading image {i}/{len(urls)}...")
            url = image["url"] if isinstance(image, dict) else image
            filename = download_image(url, args.output)
            if filename:
                print(f"Downloaded: {filename}")
        
        print("\nDownload complete!")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
