import requests
import re
import json
from datetime import datetime

JSON_API = "https://sm-iptv-channel-data.pages.dev/CricHD_id.json"

M3U_FILE = "crichd.m3u"
JSON_FILE = "crichd.json"


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
                return stream.replace("\\/", "/")

    except Exception as e:
        print(f"Error for {id}: {e}")

    return None


def main():
    res = requests.get(JSON_API)
    data = res.json()

    m3u = "#EXTM3U\n"
    m3u += "#=================================\n"
    m3u += "# 🖥️ Developed by: Monirul Islam\n"
    m3u += "# 🔗 Telegram: https://t.me/monirul_Islam_SM\n"

    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
    date_str = now.strftime("%Y-%m-%d")

    channel_list = []
    count = 0

    temp_m3u = ""

    for ch in data:
        ch_id = ch.get("id")
        name = ch.get("name")
        logo = ch.get("logo")
        referer = ch.get("referer")

        print(f"Fetching: {name}")

        stream = get_stream(ch_id)

        if stream:
            count += 1

            # M3U part
            temp_m3u += f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n'
            temp_m3u += f'#EXTVLCOPT:http-referrer={referer}\n'
            temp_m3u += f"{stream}\n\n"

            # JSON part
            channel_list.append({
                "id": ch_id,
                "title": name,
                "logo": logo,
                "url": stream,
                "category": "sports"
            })

        else:
            print(f"❌ Skip: {name}")

    # Header finish
    m3u += f"# 🕒 Last Updated: {time_str}\n"
    m3u += f"# 📺 Channels Count: {count}\n"
    m3u += "#=================================\n\n"

    m3u += temp_m3u

    # Save M3U
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

    # JSON structure
    output_json = {
        "status": "success",
        "name": "CricHD Live Channels",
        "owner": "Monirul Islam",
        "channels_amount": count,
        "Last_update": date_str,
        "response": channel_list
    }

    # Save JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)

    print("✅ Done! M3U + JSON created")


if __name__ == "__main__":
    main()
