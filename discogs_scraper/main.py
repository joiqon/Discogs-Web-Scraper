import sys
from config import OUTPUT_LOCATION
from discogs import get_discogs_metadata
from writer import write_to_obsidian

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <discogs_url> [output_folder]")
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
