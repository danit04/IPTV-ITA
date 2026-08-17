import re
import urllib.request
from pathlib import Path

FREE_TV = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_italy.m3u8"
IPTV_ORG = "https://iptv-org.github.io/iptv/countries/it.m3u"
OUTPUT = "playlist.m3u"


def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_playlist(text):
    lines = text.splitlines()
    items = []

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF:") and i + 1 < len(lines):
            items.append((line, lines[i + 1]))

    return items


def get_tvg_id(extinf):
    match = re.search(r'tvg-id="([^"]+)"', extinf)

    if match:
        return match.group(1)

    return ""


def main():

    print("Downloading Free-TV...")
    free_tv = download(FREE_TV)

    print("Downloading IPTV-org...")
    iptv_org = download(IPTV_ORG)

    free_items = parse_playlist(free_tv)
    org_items = parse_playlist(iptv_org)

    # Build a dictionary containing the CURRENT stream
    # from IPTV-org for every channel.
    org_streams = {}

    for extinf, url in org_items:

        tvg_id = get_tvg_id(extinf)

        if tvg_id and url.startswith("http"):
            org_streams[tvg_id] = url.strip()

    print(f"Found {len(org_streams)} IPTV-org streams.")

    output = ["#EXTM3U"]

    replaced = 0

    for extinf, url in free_items:

        tvg_id = get_tvg_id(extinf)

        # Replace ONLY Rai channels.
        # Everything else remains exactly as Free-TV.
        if tvg_id.startswith("Rai") and tvg_id in org_streams:

            output.append(extinf)
            output.append(org_streams[tvg_id])

            replaced += 1

        else:

            output.append(extinf)
            output.append(url)

    Path(OUTPUT).write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    print("Playlist generated.")
    print(f"Total Free-TV channels: {len(free_items)}")
    print(f"Rai streams replaced from IPTV-org: {replaced}")


if __name__ == "__main__":
    main()
