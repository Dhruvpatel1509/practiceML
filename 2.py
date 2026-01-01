import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="YouTube Video Filter", page_icon="🎬", layout="wide")

st.title("🎬 Corridor Crew Video Filter")
st.markdown("Filter out 'React' videos and Shorts from Corridor Crew")

# API key embedded
API_KEY = "AIzaSyAKkcQ323CFr541iLLddmym06MVT2Q5AfQ"

# Channel ID for Corridor Crew
CHANNEL_ID = "UCSpFnDQr88xCZ80N-X7t0nQ"

def get_video_durations(api_key, video_ids):
    """Fetch video durations to filter out shorts"""
    url = "https://www.googleapis.com/youtube/v3/videos"
    durations = {}
    
    # Process in batches of 50
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            "key": api_key,
            "id": ",".join(batch),
            "part": "contentDetails"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("items", []):
                duration = item["contentDetails"]["duration"]
                durations[item["id"]] = duration
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching durations: {str(e)}")
    
    return durations

def parse_duration(duration_str):
    """Parse ISO 8601 duration to seconds"""
    import re
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def get_channel_videos(api_key, channel_id, start_date, end_date):
    """Fetch videos from a YouTube channel within date range"""
    videos = []
    url = "https://www.googleapis.com/youtube/v3/search"
    next_page_token = None
    
    with st.spinner(f"Fetching videos from {start_date} to {end_date}..."):
        while True:
            params = {
                "key": api_key,
                "channelId": channel_id,
                "part": "snippet",
                "order": "date",
                "maxResults": 50,
                "type": "video",
                "publishedAfter": f"{start_date}T00:00:00Z",
                "publishedBefore": f"{end_date}T23:59:59Z"
            }
            
            if next_page_token:
                params["pageToken"] = next_page_token
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("items", []):
                    video = {
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
                    }
                    videos.append(video)
                
                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching videos: {str(e)}")
                break
    
    # Filter out shorts (videos under 60 seconds)
    if videos:
        video_ids = [v["id"] for v in videos]
        durations = get_video_durations(api_key, video_ids)
        
        filtered_videos = []
        for video in videos:
            duration_str = durations.get(video["id"], "PT0S")
            duration_seconds = parse_duration(duration_str)
            if duration_seconds >= 120:  # Only videos 2+ minutes
                filtered_videos.append(video)
        
        return filtered_videos
    
    return videos

def filter_react_videos(videos, filter_keywords):
    """Filter out videos containing specified keywords"""
    filtered = []
    for video in videos:
        title_lower = video["title"].lower()
        if not any(keyword.lower() in title_lower for keyword in filter_keywords):
            filtered.append(video)
    return filtered

# Sidebar filters
st.sidebar.header("Filter Settings")

# Year and period selection
year = st.sidebar.selectbox("Select Year:", list(range(2025, 2013, -1)))
period = st.sidebar.selectbox("Select Period:", ["First 6 Months (Jan-Jun)", "Last 6 Months (Jul-Dec)"])

if period == "First 6 Months (Jan-Jun)":
    start_date = f"{year}-01-01"
    end_date = f"{year}-06-30"
else:
    start_date = f"{year}-07-01"
    end_date = f"{year}-12-31"

st.sidebar.info(f"Date range: {start_date} to {end_date}")

default_keywords = ["react", "vfx artists react", "animators react", "stuntmen react"]
keywords_input = st.sidebar.text_area(
    "Filter keywords (one per line):",
    value="\n".join(default_keywords),
    help="Videos containing these keywords will be filtered out"
)
filter_keywords = [k.strip() for k in keywords_input.split("\n") if k.strip()]

if st.sidebar.button("Fetch & Filter Videos", type="primary"):
    videos = get_channel_videos(API_KEY, CHANNEL_ID, start_date, end_date)
    
    if videos:
        filtered_videos = filter_react_videos(videos, filter_keywords)
        
        # Store in session state
        st.session_state.all_videos = videos
        st.session_state.filtered_videos = filtered_videos
        st.session_state.filter_keywords = filter_keywords
        st.session_state.date_range = f"{start_date} to {end_date}"

# Display results
if "filtered_videos" in st.session_state:
    all_count = len(st.session_state.all_videos)
    filtered_count = len(st.session_state.filtered_videos)
    removed_count = all_count - filtered_count
    
    st.markdown(f"### 📅 {st.session_state.date_range}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Videos (no shorts)", all_count)
    col2.metric("Filtered Videos", filtered_count)
    col3.metric("Removed (React videos)", removed_count)
    
    st.markdown("---")
    
    # Tabs for viewing
    tab1, tab2 = st.tabs(["✅ Filtered Videos", "❌ Removed Videos"])
    
    with tab1:
        st.subheader(f"Videos without '{', '.join(st.session_state.filter_keywords)}' keywords")
        
        if st.session_state.filtered_videos:
            for video in st.session_state.filtered_videos:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.image(video["thumbnail"], use_column_width=True)
                
                with col2:
                    st.markdown(f"### [{video['title']}](https://www.youtube.com/watch?v={video['id']})")
                    date = datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%SZ")
                    st.caption(f"📅 Published: {date.strftime('%B %d, %Y')}")
                    with st.expander("Show description"):
                        st.text(video["description"][:300] + "..." if len(video["description"]) > 300 else video["description"])
                
                st.markdown("---")
        else:
            st.info("No videos match your filter criteria.")
    
    with tab2:
        removed_videos = [v for v in st.session_state.all_videos if v not in st.session_state.filtered_videos]
        st.subheader(f"Videos containing filter keywords ({len(removed_videos)})")
        
        for video in removed_videos:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image(video["thumbnail"], use_column_width=True)
            
            with col2:
                st.markdown(f"### [{video['title']}](https://www.youtube.com/watch?v={video['id']})")
                date = datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%SZ")
                st.caption(f"📅 Published: {date.strftime('%B %d, %Y')}")
            
            st.markdown("---")

else:
    st.info("👈 Select a year and period, then click 'Fetch & Filter Videos' to get started!")
    st.markdown("""
    ### Features:
    - 🎬 Filters out React videos
    - 🚫 Excludes YouTube Shorts (videos under 60 seconds)
    - 📅 Browse by year and 6-month periods
    - 🔍 Customizable keyword filtering
    """)