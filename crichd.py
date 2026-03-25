import requests
import re

# --- API URL ---
JSON_API = "https://sm-iptv-channel-data.pages.dev/CricHD_id.json"

OUTPUT_FILE = "crichd.m3u"

def get_stream(id):
    try:
        url = f"https://profamouslife.com/premium.php?player=desktop&live={id}"

        headers = {
            "Referer": f"https://streamcrichd.com/update/{id}.php",
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            html = res.text

            match = re.search(r'return \(\[(.*?)\]\.join', html)

            if match:
                parts = match.group(1).split(',')
                stream = "".join([p.strip().strip('"') for p in parts])
                stream = stream.replace("\\/", "/")
                return stream

    except Exception as e:
        print(f"Error for {id}: {e}")

    return None


def main():
    try:
        # JSON load
        res = requests.get(JSON_API)
        data = res.json()

        m3u = "#EXTM3U\n\n"

        for ch in data:
            ch_id = ch.get("id")
            name = ch.get("name")
            logo = ch.get("logo")
            referer = ch.get("referer")

            print(f"Fetching: {name}")

            stream = get_stream(ch_id)

            if stream:
                m3u += f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n'
                m3u += f'#EXTVLCOPT:http-referrer={referer}\n'
                m3u += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0\n'
                m3u += f"{stream}\n\n"
            else:
                print(f"❌ Stream not found: {name}")

        # save file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(m3u)

        print("✅ Playlist created: crichd.m3u")

    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    main()
