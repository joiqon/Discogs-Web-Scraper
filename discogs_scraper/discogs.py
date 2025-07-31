import requests
from urllib.parse import urlparse
from discogs_scraper.config import DISCOGS_TOKEN

def extract_master_or_release_id(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    if 'master' in parts or 'release' in parts:
        item_type = 'master' if 'master' in parts else 'release'
        try:
            index = parts.index(item_type)
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

    response = requests.get(api_url, headers=headers, params=params)
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
        'country': data.get('country', ''),
        'catalog_number': data['labels'][0].get('catno', '') if 'labels' in data else '',
        'formats': ', '.join(fmt.get('name', '') for fmt in data.get('formats', [])),
        'identifiers': ', '.join(
            f"{id['type']}: {id['value']}"
            for id in data.get('identifiers', [])
            if 'value' in id
        ),
        'discogs_url': url,
        'cover_image_url': data.get('images', [{}])[0].get('resource_url', ''),
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

