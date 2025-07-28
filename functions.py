#!/usr/bin/env python3
import subprocess
import sys

# 設定
STREAMER_NAME = "shobosuke"
SEARCH_KEYWORD = "#ストグラジオ"
OUTPUT_DIR = "./downloads"

def main():
    print(f"配信者: {STREAMER_NAME}")
    print(f"検索キーワード: {SEARCH_KEYWORD}")
    print(f"出力先: {OUTPUT_DIR}")
    print()
    
    # 出力ディレクトリ作成
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 動画情報取得
    print("動画一覧を取得中...")
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s|||%(title)s",
        f"https://www.twitch.tv/{STREAMER_NAME}/videos"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        video_lines = result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"エラー: 動画情報を取得できませんでした - {e}")
        return
    
    match_count = 0
    download_count = 0
    
    print("キーワードにマッチする動画を検索中...")
    print()
    
    for line in video_lines:
        if '|||' not in line:
            continue
            
        video_id, title = line.split('|||', 1)
        
        # video_idからvプレフィックスを除去
        if video_id.startswith('v'):
            video_id = video_id[1:]
        
        if SEARCH_KEYWORD in title:
            match_count += 1
            print(f"✓ マッチ: {title}")
            print(f"  動画ID: {video_id}")
            
            # ダウンロード確認
            response = input("この動画をダウンロードしますか？ (y/N): ").strip().lower()
            
            if response in ['y', 'yes']:
                print("ダウンロード開始...")
                
                download_cmd = [
                    "yt-dlp",
                    "-x",
                    "--audio-format", "mp3",
                    "-o", f"{OUTPUT_DIR}/%(uploader)s - %(title)s.%(ext)s",
                    f"https://www.twitch.tv/videos/{video_id}"
                ]
                
                try:
                    subprocess.run(download_cmd, check=True)
                    print("✓ ダウンロード完了")
                    download_count += 1
                except subprocess.CalledProcessError as e:
                    print(f"✗ ダウンロード失敗: 動画が削除されたか、アクセスできません")
                    print(f"  URL: https://www.twitch.tv/videos/{video_id}")
            else:
                print("スキップしました")
            print()
    
    print("=" * 50)
    print(f"マッチした動画数: {match_count}")
    print(f"ダウンロード数: {download_count}")
    print("=" * 50)

if __name__ == "__main__":
    main()