# corridorcrew_filter_fixed.py

import streamlit as st
import yt_dlp

# Direct link to the channel's "Videos" tab (not @handle)
CHANNEL_VIDEOS_URL = "https://www.youtube.com/@CorridorCrew/videos"
FILTER_KEYWORDS = ["react", "reaction", "vfx artist"]

def get_channel_videos(channel_videos_url):
    """Fetch all videos from the channel's 'Videos' tab."""
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_videos_url, download=False)
    
    videos = info.get('entries', [])
    return videos

def filter_videos(videos, keywords):
    """Filter out unwanted videos by title."""
    filtered = []
    for v in videos:
        title = v.get('title', '').lower()
        if not any(kw in title for kw in keywords):
            filtered.append(v)
    return filtered

def main():
    st.title("Corridor Crew Videos (Filtered)")
    st.write("🎬 Excluding videos with titles containing:")
    st.write(", ".join([f"‘{k}’" for k in FILTER_KEYWORDS]))

    with st.spinner("Fetching videos... Please wait ⏳"):
        videos = get_channel_videos(CHANNEL_VIDEOS_URL)

    if not videos:
        st.error("No videos found. Try again later — YouTube may be throttling requests.")
        return

    st.success(f"Fetched {len(videos)} videos.")
    filtered = filter_videos(videos, FILTER_KEYWORDS)
    st.info(f"Showing {len(filtered)} filtered videos.")

    for v in filtered:
        title = v.get('title', 'Untitled')
        url = v.get('url')
        thumbnail = v.get('thumbnail')
        st.markdown(f"### [{title}]({url})")
        if thumbnail:
            st.image(thumbnail, width=240)

if __name__ == "__main__":
    main()
