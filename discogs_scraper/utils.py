import re
import os
import requests

def slugify(value):
    return re.sub(r'[\\/*?:"<>|]', '', value)

def download_cover_image(url, output_dir, name_base):
    if not url:
        raise ValueError("No cover image URL provided.")

    print(f"Attempting to download image from: {url}")  # debug

    ext = url.split('.')[-1].split('?')[0]
    filename = f"{slugify(name_base)}_cover.{ext}"
    filepath = os.path.join(output_dir, filename)

    headers = {
        'User-Agent': 'ObsidianDiscogsScraper/1.0',
        'Referer': 'https://www.discogs.com'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filename
    except Exception as e:
        raise RuntimeError(f"❌ Failed to download cover image: {e}")
