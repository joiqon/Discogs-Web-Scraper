import re
import os
import requests

def slugify(value):
    return re.sub(r'[\\/*?:"<>|]', '', value)

def download_cover_image(url, output_dir, name_base):
    if not url:
        return ''
    ext = url.split('.')[-1].split('?')[0]
    filename = f"{slugify(name_base)}_cover.{ext}"
    filepath = os.path.join(output_dir, filename)
    try:
        headers = {
            'User-Agent': 'ObsidianDiscogsScraper/1.0',
            'Referer': 'https://www.discogs.com'
        }
        img = requests.get(url, headers=headers)
        img.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(img.content)
        return filename
    except Exception as e:
        print(f"⚠️ Could not download image: {e}")
        return ''
