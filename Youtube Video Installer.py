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

def download_video(url, destination_folder, time_range, download_thumbnail, force8K, force4K, force2K):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4', # mkv for better quality but more storage, mp4 for worse quality but less storage
        'writethumbnail': download_thumbnail,
        'restrictfilenames': True
    }

    # Postprocessor arguments for ffmpeg with NVENC hardware acceleration
    if time_range:
        start_time, end_time = time_range.lstrip('*').split('-')

        if force8K:
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
                '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
                '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
                '-rc-lookahead', '32',  # Enhance future frame prediction
                '-spatial-aq', '1',  # Adaptive quantization to preserve details
                '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
                '-vf', 'scale=7680:4320,unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
        elif force4K:
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
                '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
                '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
                '-rc-lookahead', '32',  # Enhance future frame prediction
                '-spatial-aq', '1',  # Adaptive quantization to preserve details
                '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
                '-vf', 'scale=3840:2160,unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
        elif force2K:
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
                '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
                '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
                '-rc-lookahead', '32',  # Enhance future frame prediction
                '-spatial-aq', '1',  # Adaptive quantization to preserve details
                '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
                '-vf', 'scale=1920:1080,unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
        else:
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
                '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
                '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
                '-rc-lookahead', '32',  # Enhance future frame prediction
                '-spatial-aq', '1',  # Adaptive quantization to preserve details
                '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
                '-vf', 'unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
    else:
        if force8K:
            ydl_opts['postprocessor_args'] = [
            '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
            '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
            '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
            '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
            '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
            '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
            '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
            '-rc-lookahead', '32',  # Enhance future frame prediction
            '-spatial-aq', '1',  # Adaptive quantization to preserve details
            '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
            '-vf', 'scale=7680:4320,unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
        elif force4K:
            ydl_opts['postprocessor_args'] = [
            '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
            '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
            '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
            '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
            '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
            '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
            '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
            '-rc-lookahead', '32',  # Enhance future frame prediction
            '-spatial-aq', '1',  # Adaptive quantization to preserve details
            '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
            '-vf', 'scale=3840:2160,unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
        elif force2K:
            ydl_opts['postprocessor_args'] = [
            '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
            '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
            '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
            '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
            '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
            '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
            '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
            '-rc-lookahead', '32',  # Enhance future frame prediction
            '-spatial-aq', '1',  # Adaptive quantization to preserve details
            '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
            '-vf', 'scale=1920:1080,unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
        else:
            ydl_opts['postprocessor_args'] = [
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-pix_fmt', 'yuv420p',  # Use 4:2:0 chroma subsampling for better quality and retaining color
                '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
                '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
                '-rc-lookahead', '32',  # Enhance future frame prediction
                '-spatial-aq', '1',  # Adaptive quantization to preserve details
                '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
                '-vf', 'unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
    

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == '__main__':
    url = input("Enter the YouTube video URL: ")
    destination_folder = input("Enter the destination folder: ")

    if not os.path.exists(destination_folder):
        print("Destination folder does not exist.")

    time_input = input("Enter the time range to download (e.g., '6:01-6:50' or '20:47-23:03'), or press Enter to download the whole video: ")
    thumbnail = input("Would you like to download the thumbnail? (y/n): ")

    forceResolution = input("Would you like to force the video to be in a high resolution? (8K/4K/2K or press enter to not change it from the original): ")
    
    time_range = None
    if time_input:
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

    eightK = False
    if forceResolution.lower() == '8k':
        confirmation = input("Forcing 8K may cause visual issues, high file sizes and an extremely long wait time, are you sure you want to force 8K resolution? (y/n): ")
        if confirmation.lower() == 'y':
            eightK = True
        else:
            eightK = False
    
    fourK = False
    if forceResolution.lower() == '4k':
        confirmation = input("Forcing 4K may cause visual issues, big file sizes and a long wait time, are you sure you want to force 4K resolution? (y/n): ")
        if confirmation.lower() == 'y':
            fourK = True
        else:
            fourK = False
    
    twoK = False   
    if forceResolution.lower() == '2k':
        confirmation = input("Forcing 2K may cause visual issues and a longer than usual wait time, are you sure you want to force 2K resolution? (y/n): ")
        if confirmation.lower() == 'y':
            twoK = True
        else:
            twoK = False
    
    download_video(url, destination_folder, time_range, download_thumbnail, eightK, fourK, twoK)