import os
from .utils import slugify, download_cover_image

def write_to_obsidian(fields, tracklist, credits, output_dir):
    filename = f"{slugify(fields['artist'])} - {slugify(fields['title'])}.md"
    filepath = os.path.join(output_dir, filename)
    os.makedirs(output_dir, exist_ok=True)
    image_filename = download_cover_image(fields['cover_image_url'], output_dir, fields['title'])

    with open(filepath, 'w', encoding='utf-8') as f:
        # Dataview inline fields
        f.write("tags:: #discogs #music\n")
        f.write(f"artist:: {fields['artist']}\n")
        f.write(f"title:: {fields['title']}\n")
        f.write(f"year:: {fields['year']}\n")
        f.write(f"genres:: {fields['genres']}\n")
        f.write(f"styles:: {fields['styles']}\n")
        f.write(f"label:: {fields['label']}\n")
        f.write(f"country:: {fields.get('country', '')}\n")
        f.write(f"discogs:: {fields['discogs_url']}\n\n")

        # Obsidian-friendly image embed
        if image_filename:
            f.write(f"![[{image_filename}]]\n\n")

        f.write("## Tracklist\n")
        for track in tracklist:
            f.write(f"- {track}\n")

        if credits:
            f.write("\n## Credits\n")
            for credit in credits:
                f.write(f"- {credit}\n")

    print(f"✅ Saved note to: {filepath}")
    if image_filename:
        print(f"🖼️  Saved image: {image_filename}")
