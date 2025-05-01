import os
import requests
import subprocess
import json
from datetime import datetime
from dateutil import parser

# Get environment variables
client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")
channel_name = os.getenv("TWITCH_CHANNEL_NAME")
keyword = os.getenv("KEYWORD_FILTER", "ストグラジオ")
audio_dir = "docs/audio"

def get_oauth_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    return response.json()["access_token"]

def get_user_id(token):
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {token}"}
    r = requests.get(f"https://api.twitch.tv/helix/users?login={channel_name}", headers=headers)
    return r.json()["data"][0]["id"]

def get_latest_vod(token, user_id):
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {token}"}
    url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&first=5&type=archive"
    r = requests.get(url, headers=headers)
    for video in r.json()["data"]:
        if keyword in video["title"]:
            return video
    return None

def download_vod(video_url, output_path):
    subprocess.run(["ffmpeg", "-i", video_url, "-vn", "-acodec", "libmp3lame", output_path])

def update_rss(file_name, title, pub_date):
    rss_path = "docs/rss.xml"
    if not os.path.exists(rss_path):
        with open(rss_path, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<rss version="2.0">\n')
            f.write('<channel>\n')
            f.write('<title>ストグラジオ</title>\n')
            f.write('<link>https://bootscafe.github.io/podcasting/</link>\n')
            f.write('<description>shobosukeのストグラジオ自動Podcast</description>\n')
            f.write('</channel>\n')
            f.write('</rss>\n')
    with open(rss_path, "r") as f:
        content = f.read()
    new_item = f"""  <item>
    <title>{title}</title>
    <enclosure url="https://bootscafe.github.io/podcasting/audio/{file_name}" type="audio/mpeg" />
    <guid>{file_name}</guid>
    <pubDate>{pub_date}</pubDate>
  </item>\n</rss>"""
    content = content.replace("</rss>", new_item)
    with open(rss_path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    token = get_oauth_token()
    user_id = get_user_id(token)
    vod = get_latest_vod(token, user_id)
    if vod:
        published_at = parser.parse(vod["published_at"])
        date_str = published_at.strftime("%Y%m%d_%H%M")
        title = vod["title"]
        file_name = f"{date_str}.mp3"
        output_path = f"{audio_dir}/{file_name}"
        download_vod(vod["url"], output_path)
        update_rss(file_name, title, published_at.strftime("%a, %d %b %Y %H:%M:%S +0000"))
