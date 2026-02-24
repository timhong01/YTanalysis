import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="YouTube Channel Analyzer", page_icon="📊", layout="wide")

def parse_duration(duration_str):
    """將 ISO 8601 長度 (例如 PT1H2M10S) 轉換為秒數"""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def get_channel_info(api_key, handle):
    if handle.startswith('@'):
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&forHandle={handle}&key={api_key}"
    else:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&id={handle}&key={api_key}"
        
    response = requests.get(url).json()
    if "error" in response:
        return None, f"API 錯誤: {response['error']['message']}"
    if not response.get("items"):
        return None, "找不到指定的頻道"
        
    channel = response["items"][0]
    return {
        "title": channel["snippet"]["title"],
        "description": channel["snippet"]["description"],
        "thumbnail": channel["snippet"]["thumbnails"]["high"]["url"],
        "uploads_playlist": channel["contentDetails"]["relatedPlaylists"]["uploads"],
        "total_videos": int(channel["statistics"].get("videoCount", 0)),
        "total_views": int(channel["statistics"].get("viewCount", 0)),
        "subscriber_count": int(channel["statistics"].get("subscriberCount", 0))
    }, None

def get_all_videos(api_key, playlist_id, limit=500):
    videos = []
    next_page_token = ""
    
    with st.spinner('正在獲取影片清單...'):
        while True:
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={playlist_id}&key={api_key}"
            if next_page_token:
                url += f"&pageToken={next_page_token}"
                
            response = requests.get(url).json()
            if "items" not in response:
                break
                
            for item in response["items"]:
                videos.append(item["contentDetails"]["videoId"])
                
            if len(videos) >= limit:
                videos = videos[:limit]
                break
                
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
    return videos

def get_video_stats(api_key, video_ids):
    stats = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_batches = (len(video_ids) + 49) // 50
    
    for i in range(total_batches):
        chunk = video_ids[i*50:(i+1)*50]
        ids_str = ",".join(chunk)
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={ids_str}&key={api_key}"
        
        response = requests.get(url).json()
        if "items" in response:
            for item in response["items"]:
                published_at = datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                duration_seconds = parse_duration(item["contentDetails"]["duration"])
                
                stats.append({
                    "Video ID": item["id"],
                    "標題": item["snippet"]["title"],
                    "發布時間": published_at,
                    "長度(秒)": duration_seconds,
                    "觀看次數": int(item["statistics"].get("viewCount", 0)),
                    "按讚數": int(item["statistics"].get("likeCount", 0)),
                    "留言數": int(item["statistics"].get("commentCount", 0))
                })
        
        progress = (i + 1) / total_batches
        progress_bar.progress(progress)
        status_text.text(f"已獲取數據: {min((i+1)*50, len(video_ids))} / {len(video_ids)} 支影片")
        
    status_text.empty()
    progress_bar.empty()
    return stats

# === UI 介面設計 ===
st.title("YouTube 頻道數據分析工具 📈")
st.markdown("透過 YouTube Data API v3，分析頻道上片策略與觀看數據。(最多抓取最近 500 部影片)")

st.sidebar.header("📊 設定參數")
api_key_input = st.sidebar.text_input("輸入 YouTube API Key", type="password", help="請至 Google Cloud Console 申請免費的 API Key")
handle_input = st.sidebar.text_input("輸入頻道 ID 或是 Handle", value="@gaoweirenzhi", help="支援 @ 開頭的 Handle，例如: @gaoweirenzhi")
limit_input = st.sidebar.slider("最多抓取影片數量", min_value=10, max_value=2000, value=200, step=50)

if st.sidebar.button("開始分析", type="primary"):
    if not api_key_input:
        st.sidebar.error("請先輸入 API Key！")
    elif not handle_input:
        st.sidebar.error("請輸入頻道 ID 或是 Handle！")
    else:
        channel_info, error = get_channel_info(api_key_input, handle_input)
        
        if error:
            st.error(error)
        else:
            # 顯示頻道資訊
            st.header("📺 頻道基本資訊")
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(channel_info["thumbnail"], use_container_width=True)
            with col2:
                st.subheader(channel_info["title"])
                st.write(f"**詳細描述:** {channel_info['description'][:150]}...")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("總訂閱數", f"{channel_info['subscriber_count']:,}")
                m2.metric("總觀看數", f"{channel_info['total_views']:,}")
                m3.metric("總影片數", f"{channel_info['total_videos']:,}")
            
            st.divider()
            
            # 開始抓取影片資料
            st.header("📹 擷取影片數據")
            video_ids = get_all_videos(api_key_input, channel_info["uploads_playlist"], limit=limit_input)
            
            if video_ids:
                stats = get_video_stats(api_key_input, video_ids)
                df = pd.DataFrame(stats)
                
                # 計算衍生欄位 (星期幾、時間點)
                df["發布星期"] = df["發布時間"].dt.day_name()
                df["發布小時"] = df["發布時間"].dt.hour
                
                # 顯示數據表格
                st.subheader("📋 影片詳細數據列表")
                st.dataframe(df, use_container_width=True)
                
                # 下載按鈕
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載 CSV 檔案",
                    data=csv,
                    file_name=f"{handle_input.replace('@', '')}_channel_data.csv",
                    mime="text/csv",
                )
                
                st.divider()
                st.header("📊 數據視覺化分析")
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.subheader("觀看次數前 10 名影片")
                    top10 = df.nlargest(10, "觀看次數").sort_values("觀看次數", ascending=True)
                    st.bar_chart(data=top10, x="標題", y="觀看次數", horizontal=True)
                    
                with col_chart2:
                    st.subheader("影片長度 vs 觀看次數")
                    st.scatter_chart(data=df, x="長度(秒)", y="觀看次數")
                    
                st.subheader("每週發布時間分析")
                day_counts = df["發布星期"].value_counts().reindex(
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                ).fillna(0)
                st.bar_chart(day_counts)
                
            else:
                st.warning("這個頻道似乎沒有公開的影片。")
