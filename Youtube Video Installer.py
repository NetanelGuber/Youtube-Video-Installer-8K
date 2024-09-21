import os
import sys
import subprocess
import ctypes
import urllib.request
import shutil
import zipfile
import winreg as reg
import re
import tempfile
import ssl

def is_ffmpeg_installed():
    """Check if ffmpeg is installed by trying to run 'ffmpeg -version'."""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def prompt_install_ffmpeg():
    """Prompt the user to install ffmpeg."""
    choice = input("ffmpeg is not installed. Do you want to install it now? (y/n): ").lower()
    return choice == 'y'

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-launch the script with administrator privileges."""
    # Build the command line
    cmd = [sys.executable] + sys.argv
    params = ' '.join(f'"{x}"' for x in cmd[1:])
    # Show the UAC prompt
    ctypes.windll.shell32.ShellExecuteW(None, "runas", cmd[0], params, None, 1)
    sys.exit()

def download_ffmpeg(url, output_path):
    """Download the ffmpeg .zip file from the given URL."""
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) as response, open(output_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def extract_zip(zip_path, extract_to):
    """Extract the downloaded zip file to the specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def install_ffmpeg(extract_path, install_path):
    """Move the extracted ffmpeg files to the installation directory."""
    extracted_folders = os.listdir(extract_path)
    # Find the folder that starts with 'ffmpeg'
    for folder_name in extracted_folders:
        if folder_name.lower().startswith('ffmpeg'):
            extracted_folder = os.path.join(extract_path, folder_name)
            break
    else:
        raise FileNotFoundError("Extracted ffmpeg folder not found.")
    if os.path.exists(install_path):
        shutil.rmtree(install_path)
    shutil.move(extracted_folder, install_path)

def add_ffmpeg_to_path(ffmpeg_bin_path):
    """Add the ffmpeg bin directory to the system PATH environment variable."""
    # Open the registry key
    reg_key = reg.OpenKey(
        reg.HKEY_CURRENT_USER,
        r'Environment',
        0,
        reg.KEY_READ | reg.KEY_WRITE
    )
    try:
        # Read the existing PATH value
        value, regtype = reg.QueryValueEx(reg_key, 'Path')
    except FileNotFoundError:
        value = ''
    if ffmpeg_bin_path.lower() in value.lower():
        print("ffmpeg path is already in PATH.")
        reg.CloseKey(reg_key)
        return

    new_value = value + ';' + ffmpeg_bin_path

    # Set the new PATH value
    reg.SetValueEx(reg_key, 'Path', 0, reg.REG_EXPAND_SZ, new_value)
    reg.CloseKey(reg_key)

    # Notify the system about the environment variable change
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    SMTO_ABORTIFHUNG = 0x0002
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, None)
    print("ffmpeg path added to system PATH. You WILL have to restart the program for this to take affect.")

def check_ffmpeg():
    if is_ffmpeg_installed():
        print("ffmpeg is already installed.")
        return

    if not prompt_install_ffmpeg():
        print("ffmpeg installation cancelled.")
        return

    if not is_admin():
        print("Requesting administrator privileges...")
        run_as_admin()
        return

    print("Downloading ffmpeg...")
    url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'
    user_home = os.path.expanduser('~')
    output_path = os.path.join(user_home, 'ffmpeg-git-full.zip')
    try:
        download_ffmpeg(url, output_path)
    except Exception as e:
        print(f"Error downloading ffmpeg: {e}")
        return

    print("Extracting ffmpeg...")
    extract_path = os.path.join(user_home, 'ffmpeg_temp')
    try:
        extract_zip(output_path, extract_path)
    except Exception as e:
        print(f"Error extracting ffmpeg: {e}")
        return

    print("Installing ffmpeg...")
    install_path = r'C:\ffmpeg'
    try:
        install_ffmpeg(extract_path, install_path)
    except Exception as e:
        print(f"Error installing ffmpeg: {e}")
        return

    print("Adding ffmpeg to system PATH...")
    ffmpeg_bin_path = os.path.join(install_path, 'bin')
    try:
        add_ffmpeg_to_path(ffmpeg_bin_path)
    except Exception as e:
        print(f"Error adding ffmpeg to PATH: {e}")
        return

    print("Cleaning up temporary files...")
    try:
        os.remove(output_path)
        shutil.rmtree(extract_path)
    except Exception as e:
        print(f"Error cleaning up temporary files: {e}")
        return

    print("ffmpeg installation completed successfully.")

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

def check_python_installed():
    python_path = shutil.which('python')
    return python_path is not None


def get_latest_python_download_url():
    print("Retrieving the latest stable Python version...")
    base_url = 'https://www.python.org/ftp/python/'
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(base_url, context=context) as response:
        html = response.read().decode('utf-8')

    # Extract all directory names
    versions = re.findall(r'href="([0-9\.]+)/"', html)
    # Filter out pre-release versions (those that contain letters)
    stable_versions = [v for v in versions if re.fullmatch(r'\d+\.\d+\.\d+', v)]
    # Sort versions in reverse order (latest first)
    stable_versions.sort(key=lambda s: list(map(int, s.split('.'))), reverse=True)

    # Check if installer exists for each version
    for version in stable_versions:
        installer_url = f'{base_url}{version}/python-{version}-amd64.exe'
        try:
            req = urllib.request.Request(installer_url, method='HEAD')
            with urllib.request.urlopen(req, context=context) as resp:
                if resp.status == 200:
                    print(f"Latest stable Python version is {version}")
                    return installer_url
        except urllib.error.HTTPError:
            continue  # Installer does not exist for this version

    print("Could not find a suitable Python installer.")
    sys.exit(1)

def download_python_installer(download_url, save_path):
    print("Downloading Python installer...")
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(download_url, context=context) as response, open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def install_python(installer_path):
    print("Installing Python...")
    subprocess.call([installer_path, '/quiet', 'InstallAllUsers=1', 'PrependPath=1'], shell=True)

def update_path_env():
    print("Updating PATH environment variable...")
    # Refresh environment variables
    import ctypes
    SendMessageTimeout = ctypes.windll.user32.SendMessageTimeoutW
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002
    result = ctypes.c_long()
    SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))

def check_python():
    if check_python_installed():
        print("Python is already installed.")
    else:
        confirm = input("Python is not installed. Would you like to install it? (y/n): ")
        if confirm.lower() == 'y':
            if not is_admin():
                print("Requesting administrative privileges...")
                # Re-run the program with admin rights
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
                sys.exit()
            else:
                download_url = get_latest_python_download_url()
                installer_path = os.path.join(tempfile.gettempdir(), 'python_installer.exe')
                download_python_installer(download_url, installer_path)
                install_python(installer_path)
                update_path_env()
                print("Python has been successfully installed and added to PATH.")
                print("Please restart your computer to complete the installation.")
                sys.exit()  # Exit the script after installing Python
        else:
            print("Python installation cancelled.")
            sys.exit()

    # Continue with the rest of your script (if Python was already installed)
    # Example: using pip to install packages
    try:
        subprocess.check_call(['pip', '--version'])
    except FileNotFoundError:
        print("pip not found. Installing pip...")
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])

    # Your main application logic here
    print("Your script is now running with Python installed.")

def download_video(url, destination_folder, time_range, download_thumbnail, force8K, force4K, force2K, lowPerformance):
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

        if lowPerformance != True:
            if force8K:
                ydl_opts['postprocessor_args'] = [
                    '-ss', start_time,
                    '-to', end_time,
                    '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                    '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                    '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                    '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
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
                    '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
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
                    '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
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
                    '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
                    '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                    '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
                    '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
                    '-rc-lookahead', '32',  # Enhance future frame prediction
                    '-spatial-aq', '1',  # Adaptive quantization to preserve details
                    '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
                    '-vf', 'unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
                ]
        else:
            ydl_opts['postprocessor_args'] = [
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p5',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '22',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-c:a', 'AAC',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-profile:v', 'main',   # Set H.264 profile to main for compatibility with most devices
                '-vf', 'unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
    else:
        if lowPerformance != True:
            if force8K:
                ydl_opts['postprocessor_args'] = [
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p7',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '18',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
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
                '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
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
                '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
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
                    '-pix_fmt', 'yuv444p',  # Use 4:4:4 chroma subsampling for better quality and retaining color
                    '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                    '-profile:v', 'main10',   # Set H.264 profile to main for compatibility with most devices
                    '-colorspace', 'bt2020nc',  # Use BT.2020 color space for better color representation
                    '-rc-lookahead', '32',  # Enhance future frame prediction
                    '-spatial-aq', '1',  # Adaptive quantization to preserve details
                    '-temporal-aq', '1',  # Temporal adaptive quantization for better motion handling
                    '-vf', 'unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
                ]
        else:
            ydl_opts['postprocessor_args'] = [
                '-c:v', 'hevc_nvenc',   # Use NVIDIA NVENC encoder
                '-preset', 'p5',        # NVENC presets from p1 (fastest, lower quality) to p7 (slowest, better quality), set to p5 or p4 for good quality and speed
                '-cq', '22',            # Set constant quality level (lower is better quality, set to around 18-24 and 0 is lowest)
                '-c:a', 'flac',         # Use FLAC audio codec for lossless audio, AAC for faster encoding
                '-profile:v', 'main',   # Set H.264 profile to main for compatibility with most devices
                '-vf', 'unsharp=5:5:0.8:3:3:0.4',  # sharpen for better quality
            ]
    

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == '__main__':
    check_ffmpeg()
    check_python()

    try:
        import yt_dlp
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp'])
        import yt_dlp

    url = input("Enter the YouTube video URL: ")
    destination_folder = input("Enter the destination folder: ")

    if not os.path.exists(destination_folder):
        print("Destination folder does not exist.")

    time_input = input("Enter the time range to download (e.g., '6:01-6:50' or '20:47-23:03'), or press Enter to download the whole video: ")
    thumbnail = input("Would you like to download the thumbnail? (y/n): ")

    low_performance = input("If you have a weak computer I highly recommend saying \"y\" to this. (y/n): ")

    if low_performance.lower() != 'y':
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
    
    lowPerformance = False
    if low_performance.lower() == 'y':
       lowPerformance = True
    
    download_video(url, destination_folder, time_range, download_thumbnail, eightK, fourK, twoK, lowPerformance)