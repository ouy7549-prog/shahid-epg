import requests
import re

def get_token():
    url = "https://www.dubaiplus.net/epg?channel=702096936070"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    match = re.search(r'(https://dmi-live-a\.akamaized\.net/[^"\']+\.mpd\?hdntl=[^"\']+)', response.text)
    return match.group(0) if match else None

token_link = get_token()
if token_link:
    with open("dubai_one.m3u", "w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXTINF:-1, Dubai One\n")
        f.write(token_link)
