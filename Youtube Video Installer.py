import os
import yt_dlp

def parse_time(time_str):
    parts = time_str.strip().split(':')
    parts = [int(p) for p in parts]
    if len(parts) == 1:
        return f"{parts[0]:02d}"
    elif len(parts) == 2:
        return f"{parts[0]:02d}:{parts[1]:02d}"
    elif len(parts) == 3:
        return f"{parts[0]:02d}:{parts[1]:02d}:{parts[2]:02d}"
    else:
        raise ValueError("Invalid time format. Use hh:mm:ss, mm:ss, or ss.")

def download_video(url, destination_folder, time_range, download_thumbnail, model):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'merge_output_format': 'mkv', # mkv for better quality but more storage, mp4 for worse quality but less storage
        'writethumbnail': download_thumbnail,
        'restrictfilenames': True
    }

    if time_range:
        start_time, end_time = time_range.lstrip('*').split('-')

        # Postprocessor arguments for ffmpeg with NVENC hardware acceleration
        if model == "best":
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p1',        # NVENC presets from p1 (slowest, better quality) to p7 (fastest, lower quality), set to p4 or p3 for good quality and speed
                '-rc', 'constqp',        # Use constant quantization for consistent high quality
                '-b:v', '100m',            # 0 to let encoder determine bitrate based on quality. 480p: 1m-2.5m, 720p: 2.5m-5m, 1080p: 5m-10m, 1440p (2K): 10m-20m, 2160p (4K): 20m-50m, 4320p (8K): 50m-100m or higher.
                '-cq', '0',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
                '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-b:a', '3072k',         # Set audio bitrate. Options: 128k, 256k (normal in yt videos), 320k, 512k (lossless, best quality for non-profesionals), 1536k (high amount of storage), 3072k (biggest amount of storage)
                '-profile:v', 'main',   # Set H.264 profile to main for compatibility with most devices
            ]
        elif model == "good":
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p3',        # p3 offers a balance between speed and quality
                '-rc', 'constqp',       # Constant quantization for consistent quality
                '-b:v', '50m',          # Bitrate for 4K, approximately 20-50Mbps
                '-cq', '18',            # Constant quality level (slightly higher for 4K)
                '-pix_fmt', 'yuv420p',  # 4:2:0 chroma subsampling for decent quality and smaller size
                '-c:a', 'aac',          # Use AAC codec for faster encoding
                '-b:a', '1536k',        # Audio bitrate for 4K
                '-profile:v', 'main',   # H.264 main profile for compatibility
            ]
        elif model == "medium":
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p4',        # Balanced preset for quality and speed
                '-rc', 'constqp',       # Constant quantization for consistent quality
                '-b:v', '20m',          # Bitrate for 2K (1440p), around 10-20Mbps
                '-cq', '22',            # Higher constant quality value for faster encoding
                '-pix_fmt', 'yuv420p',  # 4:2:0 chroma subsampling for decent quality
                '-c:a', 'aac',          # Use AAC for good audio quality
                '-b:a', '512k',         # Moderate audio bitrate
                '-profile:v', 'main',   # H.264 main profile for wide compatibility
            ]
        elif model == "low":
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p5',        # Faster encoding at the expense of slightly lower quality
                '-rc', 'constqp',       # Constant quantization
                '-b:v', '5m',           # Bitrate for 1080p (around 5-10Mbps)
                '-cq', '26',            # Higher constant quality value for faster encoding
                '-pix_fmt', 'yuv420p',  # 4:2:0 chroma subsampling for lower size
                '-c:a', 'aac',          # AAC codec for faster encoding
                '-b:a', '512k',         # Moderate audio bitrate
                '-profile:v', 'main',   # H.264 main profile
            ]
        else:
            print("Invalid model. Please choose from 'Best', 'Good', 'Medium', or 'Low'.")
            exit(1)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == '__main__':
    url = input("Enter the YouTube video URL: ")
    destination_folder = input("Enter the destination folder: ")

    if not os.path.exists(destination_folder):
        print("Destination folder does not exist.")

    time_input = input("Enter the time range to download (e.g., '6:01-6:50' or '20:46-23:03'), or press Enter to download the whole video: ")
    thumbnail = input("Would you like to download the thumbnail? (y/n): ")
    
    time_range = None
    if time_input:
        print("Model Description: \n\n"
      "Best: 8K videos with 3072k audio bitrate. High-quality visuals and lossless audio. 2-minute videos take ~6 minutes to process and require ~100MB of storage. Best for professional use or archiving.\n\n"
      "Good: 4K videos with 1536k audio bitrate. High-definition visuals with excellent audio quality. 2-minute videos take ~3 minutes to process and use ~50MB of storage. Ideal for high-quality viewing with a balance of speed and size.\n\n"
      "Medium: 2K videos (1440p) with 512k audio bitrate. Balanced video quality with standard audio. 2-minute videos take ~1.5 minutes to process and require ~20MB of storage. Suitable for everyday use where quality and speed are both important.\n\n"
      "Low: 1080p videos with 512k audio bitrate. Standard HD visuals with acceptable audio quality. 2-minute videos take ~30 seconds to process and use ~10MB of storage. Best for fast processing and small file sizes, ideal for mobile viewing or quick downloads.\n\n")

        model = input("What quality would you like? (Best, Good, Medium, Low): ").lower()

        try:
            start_time_str, end_time_str = time_input.split('-')
            start_time = parse_time(start_time_str)
            end_time = parse_time(end_time_str)
            time_range = f'*{start_time}-{end_time}'
        except Exception as e:
            print(f"Error parsing time range: {e}")
            exit(1)
    
    download_thumbnail = False
    if thumbnail.lower() == 'y':
        download_thumbnail = True
    
    download_video(url, destination_folder, time_range, download_thumbnail, model)