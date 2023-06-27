import subprocess
import os
import argparse
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_transcript_file(file_path):
    with open(file_path, 'r') as file:
        transcript = file.read()
    return transcript

def summarize_text(text):
    # Call summarize.py as a subprocess and capture the output
    command = ['python', 'summarize.py', '--prompt', text]
    output = subprocess.check_output(command, universal_newlines=True)
    return output.strip()

def post_to_wordpress(title, content):
    # Retrieve WordPress credentials from environment variables
    username = os.getenv('WORDPRESS_USERNAME')
    password = os.getenv('WORDPRESS_PASSWORD')
    site_url = os.getenv('WORDPRESS_SITE_URL')

    # Set up WordPress XML-RPC client
    wp = Client(site_url, username, password)

    # Create a new blog post
    post = WordPressPost()
    post.title = title
    post.content = content

    # Publish the blog post
    post.post_status = 'publish'
    wp.call(NewPost(post))

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('transcript_file', help='Path to the video transcript file')
    parser.add_argument('--title', help='Custom title for the WordPress blog post')
    args = parser.parse_args()

    # Read video transcript file
    transcript = read_transcript_file(args.transcript_file)

    # Generate default title using summarize.py if not provided by the user
    if args.title:
        post_title = args.title
    else:
        default_title_prompt = 'Read this transcript and come up with the most click-worthy headline for a blog post about the video.'
        post_title = summarize_text(default_title_prompt)

    # Summarize the transcript
    summary = summarize_text(transcript)

    # Post the summary to WordPress
    post_to_wordpress(post_title, summary)

if __name__ == '__main__':
    main()
