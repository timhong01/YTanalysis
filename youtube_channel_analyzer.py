import requests
import json
import csv
from datetime import datetime
import sys
import os

# 請在這裡填入您的 Google YouTube Data API v3 Key
API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

def get_channel_info(handle):
    """透過 Handle (例如 @gaoweirenzhi) 取得頻道基本資訊與 Uploads 播放清單 ID"""
    if handle.startswith('@'):
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&forHandle={handle}&key={API_KEY}"
    else:
        # 如果不是 @ 開頭，假設是 Channel ID
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&id={handle}&key={API_KEY}"
        
    response = requests.get(url).json()
    
    if "error" in response:
        print(f"API 錯誤: {response['error']['message']}")
        return None
        
    if not response.get("items"):
        print(f"找不到頻道: {handle}")
        return None
        
    channel = response["items"][0]
    return {
        "title": channel["snippet"]["title"],
        "uploads_playlist": channel["contentDetails"]["relatedPlaylists"]["uploads"],
        "total_videos": channel["statistics"].get("videoCount", 0),
        "total_views": channel["statistics"].get("viewCount", 0),
        "subscriber_count": channel["statistics"].get("subscriberCount", 0)
    }

def get_all_videos(playlist_id):
    """從 Uploads 播放清單中取得所有影片的 ID"""
    videos = []
    next_page_token = ""
    
    while True:
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={playlist_id}&key={API_KEY}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
            
        response = requests.get(url).json()
        if "items" not in response:
            break
            
        for item in response["items"]:
            videos.append(item["contentDetails"]["videoId"])
            
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
            
    return videos

def get_video_stats(video_ids):
    """批次取得影片的詳細數據 (發布時間、長度、觀看次數等)"""
    stats = []
    
    # YouTube API 每次最多支援查詢 50 筆 ID
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        ids_str = ",".join(chunk)
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={ids_str}&key={API_KEY}"
        
        response = requests.get(url).json()
        if "items" not in response:
            continue
            
        for item in response["items"]:
            stats.append({
                "id": item["id"],
                "title": item["snippet"]["title"],
                "publishedAt": item["snippet"]["publishedAt"], # 格式：2023-10-01T12:00:00Z
                "duration": item["contentDetails"]["duration"], # 格式：PT1H2M10S (ISO 8601)
                "viewCount": item["statistics"].get("viewCount", 0),
                "likeCount": item["statistics"].get("likeCount", 0),
                "commentCount": item["statistics"].get("commentCount", 0)
            })
            
    return stats

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("警告：請先在程式碼中設定您的 YouTube API Key，或設定環境變數 YOUTUBE_API_KEY。")
        return

    # 預設查詢 @gaoweirenzhi，也可以透過命令列參數傳入其他頻道
    handle = "@gaoweirenzhi"
    if len(sys.argv) > 1:
        handle = sys.argv[1]
        
    print(f"正在分析頻道: {handle} ...")
    channel_info = get_channel_info(handle)
    
    if not channel_info:
        return
        
    print(f"頻道名稱: {channel_info['title']}")
    print(f"訂閱人數: {channel_info['subscriber_count']}")
    print(f"總影片數: {channel_info['total_videos']}")
    print(f"總觀看數: {channel_info['total_views']}")
    print("-" * 30)
    print("正在抓取影片清單...")
    
    video_ids = get_all_videos(channel_info['uploads_playlist'])
    print(f"成功取得 {len(video_ids)} 支影片 ID，正在抓取影片詳細數據...")
    
    video_stats = get_video_stats(video_ids)
    
    # 儲存為 CSV 檔案進行後續分析
    filename = f"{handle.replace('@', '')}_channel_data.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["id", "title", "publishedAt", "duration", "viewCount", "likeCount", "commentCount"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(video_stats)
        
    print(f"完成！已成功將頻道分析資料儲存至: {filename}")
    print("您可以使用 Excel、Google Sheets 或 Pandas 匯入此 CSV 以分析其上片策略、影片長度與觀看次數的關聯。")

if __name__ == "__main__":
    main()
