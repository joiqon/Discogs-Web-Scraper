
import requests
import sys
import os
import re
from urllib.parse import urlparse
from pathlib import Path

# Replace with your Discogs personal token
DISCOGS_TOKEN = 'fvNMHFELJsMuauaYYTzyMbWDgsGirydfBHSXjvoW' # 'YOUR_DISCOGS_PERSONAL_ACCESS_TOKEN'
OUTPUT_LOCATION = '/Users/josephknight/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/003 Music'

def extract_master_or_release_id(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')

    if 'master' in parts or 'release' in parts:
        item_type = 'master' if 'master' in parts else 'release'
        try:
            index = parts.index(item_type)
            # Handle cases like "734427" or "734427-Aphex-Twin-Syro"
            item_id = parts[index + 1].split('-')[0]
            if not item_id.isdigit():
                raise ValueError(f"Invalid {item_type} ID extracted: {item_id}")
            return item_type, item_id
        except (IndexError, ValueError) as e:
            raise ValueError(f"Could not extract valid ID from URL: {url}") from e
    else:
        raise ValueError("URL must contain 'master' or 'release'")

def get_discogs_metadata(url):
    item_type, item_id = extract_master_or_release_id(url)
    api_url = f"https://api.discogs.com/{item_type}s/{item_id}"
    headers = {'User-Agent': 'ObsidianDiscogsScraper/1.0'}
    params = {'token': DISCOGS_TOKEN}

# 🔍 Debug info
    print(f"\n--- Debug ---")
    print(f"Fetching: {api_url}")
    print(f"Token begins with: {DISCOGS_TOKEN[:4]}...")  # To confirm it's set
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    print("---\n")

    response = requests.get(api_url, headers=headers, params=params)

    print(f"Status Code: {response.status_code}")
    print(f"Response Text (first 500 chars):\n{response.text[:500]}\n")


    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")

    data = response.json()

    fields = {
        'artist': data['artists'][0]['name'] if 'artists' in data else '',
        'title': data.get('title', ''),
        'year': data.get('year', ''),
        'genres': ', '.join(data.get('genres', [])),
        'styles': ', '.join(data.get('styles', [])),
        'label': data['labels'][0]['name'] if 'labels' in data else '',
        'discogs_url': url,
        'cover_image_url': data.get('images', [{}])[0].get('uri', '')
    }

    tracklist = [
        f"{track['position']}. {track['title']} ({track.get('duration', 'n/a')})"
        for track in data.get('tracklist', [])
        if track['type_'] == 'track'
    ]

    credits = [
        f"{credit['name']} – {credit['role']}"
        for credit in data.get('extraartists', [])
    ] if 'extraartists' in data else []

    return fields, tracklist, credits

def slugify(value):
    return re.sub(r'[\\/*?:"<>|]', '', value)

def download_cover_image(url, output_dir, name_base):
    if not url:
        return ''
    
    ext = url.split('.')[-1].split('?')[0]  # Strip query parameters
    filename = f"{slugify(name_base)}_cover.{ext}"
    filepath = os.path.join(output_dir, filename)

    try:
        headers = {
            'User-Agent': 'ObsidianDiscogsScraper/1.0',
            'Referer': 'https://www.discogs.com'  # Optional, but helps bypass blocks
        }

        img = requests.get(url, headers=headers)
        img.raise_for_status()

        with open(filepath, 'wb') as f:
            f.write(img.content)

        return filename
    except Exception as e:
        print(f"⚠️ Could not download image: {e}")
        return ''

def write_to_obsidian(fields, tracklist, credits, output_dir):
    filename = f"{slugify(fields['artist'])} - {slugify(fields['title'])}.md"
    filepath = os.path.join(output_dir, filename)
    image_filename = download_cover_image(fields['cover_image_url'], output_dir, fields['title'])

    os.makedirs(output_dir, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        # Embed local image
        if image_filename:
            f.write(f"![[{image_filename}]]\n\n")

        # Inline fields
        for key in ['artist', 'title', 'year', 'genres', 'styles', 'label']:
            f.write(f"{key}:: {fields[key]}\n")

        # Obsidian-style Discogs link
        f.write(f"discogs:: [[{fields['discogs_url']}]]\n")

        # Tracklist
        f.write("\ntracklist::\n")
        for track in tracklist:
            f.write(f"- {track}\n")

        # Credits
        if credits:
            f.write("\ncredits::\n")
            for credit in credits:
                f.write(f"- {credit}\n")

    print(f"✅ Saved note to: {filepath}")
    if image_filename:
        print(f"🖼️  Saved image: {image_filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python discogs_to_obsidian.py <discogs_url> [output_folder]")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_LOCATION

    try:
        fields, tracklist, credits = get_discogs_metadata(url)
        write_to_obsidian(fields, tracklist, credits, output_dir)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()