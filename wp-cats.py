import requests
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_wordpress_categories(username, password, url):
    endpoint = f"{url}/wp-json/wp/v2/categories"
    response = requests.get(endpoint, auth=(username, password))

    if response.status_code == 200:
        categories = response.json()
        for category in categories:
            print(f"ID: {category['id']}, Name: {category['name']}")
    else:
        print(f"Failed to retrieve categories: {response.content}")

def main():
    parser = argparse.ArgumentParser(description='Retrieve WordPress categories.')
    parser.add_argument('--wp_username', help='The WordPress username.')
    parser.add_argument('--wp_password', help='The WordPress password.')
    parser.add_argument('--wp_url', help='The WordPress site URL.')

    args = parser.parse_args()

    # Check for WordPress credentials in environment variables if not provided in command line
    wp_username = args.wp_username if args.wp_username else os.getenv('WORDPRESS_USERNAME')
    wp_password = args.wp_password if args.wp_password else os.getenv('WORDPRESS_PASSWORD')
    wp_url = args.wp_url if args.wp_url else os.getenv('WORDPRESS_SITE_URL')

    missing_credentials = []
    if not wp_username:
        missing_credentials.append('WORDPRESS_USERNAME')
    if not wp_password:
        missing_credentials.append('WORDPRESS_PASSWORD')
    if not wp_url:
        missing_credentials.append('WORDPRESS_SITE_URL')

    if missing_credentials:
        print(f"WordPress credentials not provided. The following variable(s) are missing: {', '.join(missing_credentials)}")
        return

    get_wordpress_categories(wp_username, wp_password, wp_url)

if __name__ == "__main__":
    main()
