import requests
import re
import json
from datetime import datetime

# --- API ---
JSON_API = "https://sm-iptv-channel-data.pages.dev/CricHD_id.json"

# --- Output Files ---
M3U_FILE = "crichd.m3u"
JSON_FILE = "crichd_data.json"


def get_stream(ch_id):
    try:
        url = f"https://profamouslife.com/premium.php?player=desktop&live={ch_id}"

        headers = {
            "Referer": f"https://streamcrichd.com/update/{ch_id}.php",
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
        print(f"❌ Error ({ch_id}): {e}")

    return None


def main():
    try:
        res = requests.get(JSON_API)
        data = res.json()

        # --- Time ---
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
        date_str = now.strftime("%Y-%m-%d")

        # --- M3U Header ---
        m3u = "#EXTM3U\n"
        m3u += "#=================================\n"
        m3u += "# 🖥️ Developed by: Monirul Islam\n"
        m3u += "# 🔗 Telegram: https://t.me/monirul_Islam_SM\n"

        temp_m3u = ""
        channel_list = []
        count = 0

        for ch in data:
            ch_id = ch.get("id")
            name = ch.get("name")
            logo = ch.get("logo")
            referer = ch.get("referer")

            print(f"📡 Fetching: {name}")

            stream = get_stream(ch_id)

            if stream:
                count += 1

                # --- M3U Entry ---
                temp_m3u += f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n'
                temp_m3u += f'#EXTVLCOPT:http-referrer={referer}\n'
                temp_m3u += f"{stream}\n\n"

                # --- JSON Entry ---
                channel_list.append({
                    "id": ch_id,
                    "title": name,
                    "logo": logo,
                    "url": stream,
                    "referer": referer,
                    "category": "sports"
                })

            else:
                print(f"❌ Skip: {name}")

        # --- Final Header ---
        m3u += f"# 🕒 Last Updated: {time_str}\n"
        m3u += f"# 📺 Channels Count: {count}\n"
        m3u += "#=================================\n\n"
        m3u += temp_m3u

        # --- Save M3U ---
        with open(M3U_FILE, "w", encoding="utf-8") as f:
            f.write(m3u)

        # --- JSON Output ---
        output_json = {
            "status": "success",
            "name": "CricHD Live Channels",
            "owner": "Monirul Islam",
            "channels_amount": count,
            "Last_update": date_str,
            "response": channel_list
        }

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=2, ensure_ascii=False)

        print("✅ Done! Files created:")
        print("➡ crichd.m3u")
        print("➡ crichd_data.json")

    except Exception as e:
        print("❌ Fatal Error:", e)


if __name__ == "__main__":
    main()
