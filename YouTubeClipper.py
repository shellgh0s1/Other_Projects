import os
from pytube import YouTube
from moviepy.editor import VideoFileClip

def download_video(url, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Download YouTube video
    youtube = YouTube(url)
    video = youtube.streams.filter(adaptive=True).first()
    video_file = video.download(output_path=output_dir)

    return video_file

def create_tiktok_videos(video_file, output_dir):
    # Load the video clip
    clip = VideoFileClip(video_file)

    # Calculate the total duration of the video in seconds
    total_duration = clip.duration

    # Calculate the number of 3-minute segments needed
    num_segments = int(total_duration / (3 * 60))
    remaining_duration = total_duration % (3 * 60)

    # Create TikTok videos
    for i in range(num_segments):
        start_time = i * 3 * 60
        end_time = (i + 1) * 3 * 60

        # Extract the segment from the original video
        segment = clip.subclip(start_time, end_time)

        # Save the segment as a TikTok video
        segment_file = os.path.join(output_dir, f"tiktok_segment_{i + 1}.mp4")
        segment.write_videofile(segment_file)

    # Create a final TikTok video with the remaining duration if it's less than 3 minutes
    if remaining_duration > 0:
        segment = clip.subclip(total_duration - remaining_duration, total_duration)
        segment_file = os.path.join(output_dir, f"tiktok_segment_{num_segments + 1}.mp4")
        segment.write_videofile(segment_file)

    # Close the clip
    clip.close()

if __name__ == "__main__":
    # YouTube URL provided by the user
    youtube_url = input("Enter the YouTube URL: ")

    # Output directory
    output_directory = "Auto_Vid"

    # Download the YouTube video
    video_file_path = download_video(youtube_url, output_directory)

    # Create TikTok videos from the downloaded video
    create_tiktok_videos(video_file_path, output_directory)
