import os
import re
import json
import requests
from dotenv import load_dotenv

# === Load env variables ===
load_dotenv()
SOURCE_URL = os.environ.get("SOURCE_URL")
CHANNEL_GROUPS_RAW = os.getenv("CHANNEL_GROUPS")

if not SOURCE_URL or not CHANNEL_GROUPS_RAW:
    print("❌ SOURCE_URL or CHANNEL_GROUPS not set in .env")
    exit()

# Convert CHANNEL_GROUPS JSON string to dict
try:
    channel_groups = json.loads(CHANNEL_GROUPS_RAW)
except json.JSONDecodeError as e:
    print(f"❌ Invalid CHANNEL_GROUPS format: {e}")
    exit()

# Create lowercase lookup for allowed channels
allowed_channels = {}
for group, channels in channel_groups.items():
    for name in channels:
        allowed_channels[name.lower()] = group

# === Your custom EXTINF replacements ===
custom_channel_data = {
  "sony sports ten 5": {
    "tvg-id": "hello",
    "tvg-name": "Sony sports ten 5",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten5-HD-New-Logo.png",
    "display-name": "Sony sports ten 5"
  },
  "sony sports ten 5 hd": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 5 HD",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten5-New-Logo.png",
    "display-name": "Sony sports ten 5 HD"
  },
  "sony sports ten 1 hd": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 1 HD",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten1-HD-New-Logo.png",
    "display-name": "Sony sports ten 1 HD"
  },
  "sony sports ten 1": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 1",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten1-New-Logo.png",
    "display-name": "Sony sports ten 1"
  },
  "sony sports ten 2 hd": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 2 HD",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten2-HD-New-Logo.png",
    "display-name": "Sony sports ten 2 HD"
  },
  "sony sports ten 2": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 2",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten2-HD-New-Logo.png",
    "display-name": "Sony sports ten 2"
  },
  "sony sports ten 3 hd": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 3 HD",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten3-HD.png",
    "display-name": "Sony sports ten 3 HD"
  },
  "sony sports ten 3": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 3",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten3-HD.png",
    "display-name": "Sony sports ten 3"
  },
  "sony sports ten 4 hd": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 4 HD",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten4.png",
    "display-name": "Sony sports ten 4 HD"
  },
  "sony sports ten 4": {
    "tvg-id": "",
    "tvg-name": "Sony sports ten 4",
    "tvg-logo": "https://www.indiantvinfo.com/media/2022/10/Sony-Sports-Ten4.png",
    "display-name": "Sony sports ten 4"
  }
}

# === Fetch playlist ===
print(f"📥 Fetching playlist from: {SOURCE_URL}")
try:
    response = requests.get(SOURCE_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
except Exception as e:
    print(f"❌ Error fetching playlist: {e}")
    exit()

# === Process 2-line blocks ===
output_blocks = []
i = 0
while i + 1 < len(lines):
    if lines[i].startswith("#EXTINF:") and lines[i+1].startswith("http"):
        extinf = lines[i]
        url = lines[i+1]
        channel_name = extinf.split(",")[-1].strip()
        group = allowed_channels.get(channel_name.lower())

        if group:
            channel_key = channel_name.lower()
            custom_info = custom_channel_data.get(channel_key)

            if custom_info:
                # Build full custom EXTINF line
                updated_extinf = (
                    f'#EXTINF:-1 '
                    f'tvg-id="{custom_info.get("tvg-id", "")}" '
                    f'tvg-name="{custom_info.get("tvg-name", "")}" '
                    f'tvg-logo="{custom_info.get("tvg-logo", "")}" '
                    f'tvg-chno="{custom_info.get("tvg-chno", "")}" '
                    f'group-title="{group}",' 
                    f'{custom_info.get("display-name", channel_name)}'
                )
            else:
                # fallback: just update group-title if no custom data
                if 'group-title="' in extinf:
                    updated_extinf = re.sub(r'group-title=".*?"', f'group-title="{group}"', extinf)
                else:
                    updated_extinf = extinf.replace(",", f' group-title="{group}",', 1)

            output_blocks.append(f"{updated_extinf}\n{url}")
        i += 2
    else:
        i += 1

# === Write output ===
output_file = "sony-with-sports.m3u"
if output_blocks:
    print(f"✅ Found {len(output_blocks)} categorized channels.")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Updated By Himanshu\n\n")
        for block in output_blocks:
            f.write(block + "\n")
else:
    print("⚠️ No matching channels found.")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# No matching channels found\n")

os.chmod(output_file, 0o666)
print(f"✅ '{output_file}' written successfully.")
