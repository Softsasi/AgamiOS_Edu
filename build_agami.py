import os
import sys
import shutil
import urllib.request
import zipfile
import subprocess
import re

# ==========================================================================
# Configuration and Path Definitions
# ==========================================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
ISO_EXTRACTED = os.path.join(BASE_DIR, "iso_extracted")
SQUASHFS_EXTRACTED = os.path.join(BASE_DIR, "squashfs_extracted")

BASE_ISO_NAME = "debian-live-13.5.0-amd64-gnome.iso"
BASE_ISO_URL = f"https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/{BASE_ISO_NAME}"
BASE_ISO_PATH = os.path.join(BASE_DIR, "base.iso")

OUTPUT_ISO_PATH = os.path.join(BASE_DIR, "Agami_OS_Education.iso")

SEVEN_ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"

# ==========================================================================
# Helper Downloader with Progress Reporting
# ==========================================================================

def download_file(url, filepath):
    print(f"Downloading: {url} -> {filepath}")
    
    def report_hook(block_num, block_size, total_size):
        read_so_far = block_num * block_size
        if total_size > 0:
            percent = min(100, (read_so_far * 100) // total_size)
            sys.stdout.write(f"\rProgress: {percent}% ({read_so_far // (1024*1024)} MB / {total_size // (1024*1024)} MB)")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\rProgress: {read_so_far // (1024*1024)} MB downloaded")
            sys.stdout.flush()
            
    urllib.request.urlretrieve(url, filepath, report_hook)
    print("\nDownload complete!\n")

# ==========================================================================
# Build Execution Pipeline
# ==========================================================================

def main():
    print("==========================================================================")
    print("          Agami OS Education - Windows Native Build System                ")
    print("==========================================================================\n")
    
    # 0. Setup directories
    os.makedirs(TOOLS_DIR, exist_ok=True)
    
    # Verify logo.png exists in root
    logo_path = os.path.join(BASE_DIR, "logo.png")
    if not os.path.exists(logo_path):
        print(f"Error: {logo_path} is missing! Please make sure the logo is placed correctly.")
        sys.exit(1)
        
    # Verify wallpaper.png exists in root
    wallpaper_path = os.path.join(BASE_DIR, "wallpaper.png")
    if not os.path.exists(wallpaper_path):
        print(f"Error: {wallpaper_path} is missing! Please make sure the wallpaper is placed correctly.")
        sys.exit(1)

    # 1. Download Windows Toolchain (SquashFS tools + xorriso)
    print("--- [Step 1/9] Setting up Windows Native Toolchain ---")
    
    squashfs_zip = os.path.join(TOOLS_DIR, "squashfs-tools-ng.zip")
    squashfs_zip_url = "https://infraroot.at/pub/squashfs/windows/squashfs-tools-ng-1.3.2-mingw64.zip"
    
    if not os.path.exists(os.path.join(TOOLS_DIR, "mksquashfs.exe")):
        download_file(squashfs_zip_url, squashfs_zip)
        print("Extracting SquashFS tools...")
        with zipfile.ZipFile(squashfs_zip, 'r') as zip_ref:
            # We want to extract bin/mksquashfs.exe and bin/unsquashfs.exe
            for file in zip_ref.namelist():
                if file.startswith("bin/"):
                    filename = os.path.basename(file)
                    if filename:
                        dest = os.path.join(TOOLS_DIR, filename)
                        with zip_ref.open(file) as zf, open(dest, 'wb') as df:
                            shutil.copyfileobj(zf, df)
        os.remove(squashfs_zip)
        print("SquashFS tools extracted successfully.\n")
    else:
        print("SquashFS tools already present. Skipping.\n")
        
    # Download xorriso & cygwin DLL dependencies
    xorriso_files = {
        "xorriso.exe": "https://raw.githubusercontent.com/PeyTy/xorriso-exe-for-windows/master/xorriso.exe",
        "cygwin1.dll": "https://raw.githubusercontent.com/PeyTy/xorriso-exe-for-windows/master/cygwin1.dll",
        "cygiconv-2.dll": "https://raw.githubusercontent.com/PeyTy/xorriso-exe-for-windows/master/cygiconv-2.dll"
    }
    
    for filename, url in xorriso_files.items():
        dest_path = os.path.join(TOOLS_DIR, filename)
        if not os.path.exists(dest_path):
            download_file(url, dest_path)
            
    print("Xorriso toolchain setup complete.\n")

    # 2. Download Debian 13 GNOME Live base ISO
    print("--- [Step 2/9] Retrieving Debian 13 Live GNOME base ISO ---")
    if not os.path.exists(BASE_ISO_PATH):
        print(f"Base ISO not found in workspace. Retrieving official Debian Live image...")
        download_file(BASE_ISO_URL, BASE_ISO_PATH)
    else:
        print("Base ISO 'base.iso' already exists in workspace. Skipping download.\n")

    # 3. Extract MBR boot template from base ISO
    print("--- [Step 3/9] Extracting MBR boot template ---")
    mbr_path = os.path.join(TOOLS_DIR, "isohdpfx.bin")
    if not os.path.exists(mbr_path):
        print("Extracting first 432 bytes of original ISO (Isohybrid MBR)...")
        with open(BASE_ISO_PATH, 'rb') as src, open(mbr_path, 'wb') as dst:
            dst.write(src.read(432))
        print("MBR template successfully extracted.\n")
    else:
        print("MBR template already exists. Skipping.\n")

    # 4. Deconstruct ISO using 7-Zip
    print("--- [Step 4/9] Deconstructing base ISO using 7-Zip ---")
    if os.path.exists(ISO_EXTRACTED):
        print("Cleaning previous extracted ISO directory...")
        shutil.rmtree(ISO_EXTRACTED)
        
    if not os.path.exists(SEVEN_ZIP_PATH):
        print(f"Error: 7-Zip was not found at {SEVEN_ZIP_PATH}. Please install 7-Zip to continue.")
        sys.exit(1)
        
    cmd_7z = [SEVEN_ZIP_PATH, "x", "-y", f"-o{ISO_EXTRACTED}", BASE_ISO_PATH]
    print(f"Running: {' '.join(cmd_7z)}")
    subprocess.run(cmd_7z, check=True)
    print("ISO successfully extracted.\n")

    # 5. Extract SquashFS root filesystem
    print("--- [Step 5/9] Extracting compressed root filesystem (SquashFS) ---")
    if os.path.exists(SQUASHFS_EXTRACTED):
        print("Cleaning previous extracted SquashFS directory...")
        shutil.rmtree(SQUASHFS_EXTRACTED)
        
    unsquashfs_bin = os.path.join(TOOLS_DIR, "unsquashfs.exe")
    squashfs_file = os.path.join(ISO_EXTRACTED, "live", "filesystem.squashfs")
    
    cmd_unsquash = [unsquashfs_bin, "-d", SQUASHFS_EXTRACTED, squashfs_file]
    print(f"Running: {' '.join(cmd_unsquash)}")
    subprocess.run(cmd_unsquash, check=True)
    print("Root filesystem successfully extracted.\n")

    # 6. Apply Agami OS Customizations & Inject Educational Dashboard
    print("--- [Step 6/9] Customizing OS & Injecting Agami Education Hub ---")
    
    # 6a. Copy Premium Wallpapers
    bg_dir = os.path.join(SQUASHFS_EXTRACTED, "usr", "share", "backgrounds")
    os.makedirs(bg_dir, exist_ok=True)
    shutil.copy(wallpaper_path, os.path.join(bg_dir, "agami_wallpaper.png"))
    
    # 6b. Copy Brand Logos
    pixmaps_dir = os.path.join(SQUASHFS_EXTRACTED, "usr", "share", "pixmaps")
    os.makedirs(pixmaps_dir, exist_ok=True)
    shutil.copy(logo_path, os.path.join(pixmaps_dir, "agami-logo.png"))
    
    # 6c. Copy Agami Education Hub HTML dashboard
    hub_dest = os.path.join(SQUASHFS_EXTRACTED, "usr", "share", "agami-hub")
    if os.path.exists(hub_dest):
        shutil.rmtree(hub_dest)
    shutil.copytree(os.path.join(BASE_DIR, "agami_hub"), hub_dest)
    
    # 6d. Create desktop shortcuts & folders inside Skeleton (/etc/skel/)
    skel_desktop = os.path.join(SQUASHFS_EXTRACTED, "etc", "skel", "Desktop")
    os.makedirs(skel_desktop, exist_ok=True)
    
    # Create the Desktop Entry launcher
    launcher_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Agami Education Hub
Comment=Interactive Educational Hub and Portal
Exec=gnome-web-browser /usr/share/agami-hub/index.html || firefox-esr /usr/share/agami-hub/index.html || xdg-open /usr/share/agami-hub/index.html
Icon=/usr/share/pixmaps/agami-logo.png
Terminal=false
Categories=Education;Development;
"""
    launcher_path = os.path.join(skel_desktop, "agami-hub.desktop")
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
        
    # 6e. Setup Boot-Time Autostart Settings (Wallpaper & settings daemon)
    bin_dir = os.path.join(SQUASHFS_EXTRACTED, "usr", "local", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    
    # Runtime initialization script (runs when GNOME boots inside Live OS)
    init_script_content = """#!/bin/bash
# Wait for D-Bus and GSettings services to initialize
sleep 3

# Set custom Agami OS 4K wallpaper (for both Light and Dark GNOME themes)
gsettings set org.gnome.desktop.background picture-uri "file:///usr/share/backgrounds/agami_wallpaper.png"
gsettings set org.gnome.desktop.background picture-uri-dark "file:///usr/share/backgrounds/agami_wallpaper.png"
gsettings set org.gnome.desktop.background picture-options "zoom"

# Set Screensaver Background
gsettings set org.gnome.desktop.screensaver picture-uri "file:///usr/share/backgrounds/agami_wallpaper.png"

# Ensure the Desktop Launcher is executable
chmod +x /home/user/Desktop/agami-hub.desktop 2>/dev/null
chmod +x /etc/skel/Desktop/agami-hub.desktop 2>/dev/null
"""
    init_script_path = os.path.join(bin_dir, "agami-init.sh")
    with open(init_script_path, 'w', newline='\n', encoding='utf-8') as f:
        f.write(init_script_content)
        
    # Register the autostart .desktop configuration
    autostart_dir = os.path.join(SQUASHFS_EXTRACTED, "etc", "xdg", "autostart")
    os.makedirs(autostart_dir, exist_ok=True)
    
    autostart_content = """[Desktop Entry]
Type=Application
Name=Agami OS Init Daemon
Exec=/usr/local/bin/agami-init.sh
Terminal=false
NoDisplay=true
"""
    autostart_path = os.path.join(autostart_dir, "agami-init.desktop")
    with open(autostart_path, 'w', encoding='utf-8') as f:
        f.write(autostart_content)
        
    print("Agami OS customizations successfully injected.\n")

    # 7. Repack filesystem using mksquashfs
    print("--- [Step 7/9] Repacking customized root filesystem (SquashFS) ---")
    
    # Delete old squashfs from the extracted ISO structure before building a new one
    if os.path.exists(squashfs_file):
        os.remove(squashfs_file)
        
    mksquashfs_bin = os.path.join(TOOLS_DIR, "mksquashfs.exe")
    cmd_mksquash = [mksquashfs_bin, SQUASHFS_EXTRACTED, squashfs_file, "-comp", "gzip", "-noappend"]
    print(f"Running: {' '.join(cmd_mksquash)}")
    subprocess.run(cmd_mksquash, check=True)
    print("SquashFS repacked successfully.\n")

    # 8. Extract original El Torito boot params from base.iso
    print("--- [Step 8/9] Extracting original bootloader layout parameters ---")
    xorriso_bin = os.path.join(TOOLS_DIR, "xorriso.exe")
    
    # We run xorriso -indev base.iso -report_el_torito as_mkisofs to fetch original boot configs
    cmd_report = [xorriso_bin, "-indev", BASE_ISO_PATH, "-report_el_torito", "as_mkisofs"]
    print(f"Running: {' '.join(cmd_report)}")
    res = subprocess.run(cmd_report, capture_output=True, text=True, check=True)
    
    # Parse output to extract options
    original_args = res.stdout.strip().splitlines()
    print("Original boot arguments detected:")
    
    clean_args = []
    skip_next = False
    
    # Filter arguments to remove original directories and output paths
    for line in original_args:
        line = line.strip()
        if not line or line.startswith("\\"):
            continue
        
        # Split tokens
        tokens = re.split(r'\s+', line)
        for i, token in enumerate(tokens):
            if skip_next:
                skip_next = False
                continue
            
            # Skip output parameters, source dirs, and isolinux MBR (since we replace it)
            if token in ["-o", "--output", "-out"]:
                skip_next = True
                continue
            if token == "-isohybrid-mbr":
                skip_next = True
                continue
            if token == "-as" and i < len(tokens) - 1 and tokens[i+1] == "mkisofs":
                continue
            if token == "mkisofs":
                continue
            if token.startswith("/") or token.startswith("."):
                # Skip source directories (which are absolute paths on the original build server)
                continue
                
            clean_args.append(token)
            
    print(f"Sanitized arguments: {clean_args}\n")

    # 9. Generate bootable Hybrid ISO using xorriso
    print("--- [Step 9/9] Generating bootable Hybrid ISO image ---")
    
    if os.path.exists(OUTPUT_ISO_PATH):
        os.remove(OUTPUT_ISO_PATH)
        
    # Build complete execution argument list
    xorriso_args = [
        xorriso_bin,
        "-as", "mkisofs",
    ]
    
    # Append the sanitized bootloader configurations
    xorriso_args.extend(clean_args)
    
    # Append our custom Windows output paths & hybrid parameters
    xorriso_args.extend([
        "-isohybrid-mbr", os.path.join(TOOLS_DIR, "isohdpfx.bin"),
        "-o", OUTPUT_ISO_PATH,
        ISO_EXTRACTED
    ])
    
    print(f"Running: {' '.join(xorriso_args)}")
    subprocess.run(xorriso_args, check=True)
    
    print("\n==========================================================================")
    print("🎉 SUCCESS! Agami OS Education has been built successfully!")
    print(f"Output File: {OUTPUT_ISO_PATH}")
    print("==========================================================================\n")

if __name__ == "__main__":
    main()
