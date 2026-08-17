import re
import urllib.request
from pathlib import Path

FREE_TV = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_italy.m3u8"
IPTV_ORG = "https://iptv-org.github.io/iptv/countries/it.m3u"
OUTPUT = "playlist.m3u"

RAI_STREAMS = {
    "Rai1.it": "https://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=2606803&output=7&forceUserAgent=raiplayappletv",
    "Rai2.it": "https://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=308718&output=7&forceUserAgent=raiplayappletv",
    "Rai3.it": "https://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=308709&output=7&forceUserAgent=raiplayappletv",
}


def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_playlist(text):
    lines = text.splitlines()
    result = []

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF:") and i + 1 < len(lines):
            result.append((line, lines[i + 1]))

    return result


def get_tvg_id(extinf):
    match = re.search(r'tvg-id="([^"]+)"', extinf)

    if match:
        return match.group(1)

    return ""


def main():

    print("Scarico Free-TV...")
    free_tv = download(FREE_TV)

    print("Scarico IPTV-org...")
    iptv_org = download(IPTV_ORG)

    free_items = parse_playlist(free_tv)
    org_items = parse_playlist(iptv_org)

    rai_streams = {}

    for extinf, url in org_items:

        tvg_id = get_tvg_id(extinf)

        if tvg_id.startswith("Rai") and url.startswith("http"):
            rai_streams[tvg_id] = url.strip()

    print(f"Trovati {len(rai_streams)} stream Rai su IPTV-org")

    output = ["#EXTM3U"]

    replaced = 0

    for extinf, url in free_items:

        tvg_id = get_tvg_id(extinf)

        if tvg_id in RAI_STREAMS:

            output.append(extinf)
            output.append(RAI_STREAMS[tvg_id])

            replaced += 1

        elif tvg_id in rai_streams:

            output.append(extinf)
            output.append(rai_streams[tvg_id])

            replaced += 1

        else:

            output.append(extinf)
            output.append(url)

    Path(OUTPUT).write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    print(f"Playlist generata.")
    print(f"Canali totali: {len(free_items)}")
    print(f"Stream Rai sostituiti: {replaced}")


if __name__ == "__main__":
    main()
