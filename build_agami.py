import os
import sys
import shutil
import urllib.request
import zipfile
import subprocess
import re
import shlex
import time

# ==========================================================================
# Configuration and Path Definitions
# ==========================================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
ISO_EXTRACTED = os.path.join(BASE_DIR, "iso_extracted")

BASE_ISO_NAME = "debian-live-13.5.0-amd64-gnome.iso"
BASE_ISO_URL = f"https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/{BASE_ISO_NAME}"
BASE_ISO_PATH = os.path.join(BASE_DIR, "base.iso")

OUTPUT_ISO_NAME = "Agami_OS_Education.iso"
OUTPUT_ISO_PATH = os.path.join(BASE_DIR, OUTPUT_ISO_NAME)

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
    
    global_start_time = time.time()
    
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
    
    # We require gensquashfs.exe, rdsquashfs.exe, sqfs2tar.exe, tar2sqfs.exe and all DLL dependencies
    required_binaries = ["gensquashfs.exe", "rdsquashfs.exe", "sqfs2tar.exe", "tar2sqfs.exe", "libsquashfs.dll"]
    missing_binaries = [b for b in required_binaries if not os.path.exists(os.path.join(TOOLS_DIR, b))]
    
    if missing_binaries:
        print("Downloading SquashFS Tools NG...")
        download_file(squashfs_zip_url, squashfs_zip)
        print("Extracting SquashFS Tools NG...")
        with zipfile.ZipFile(squashfs_zip, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if "/bin/" in file:
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

    # 5. Extract SquashFS root filesystem into uncompressed Tar archive
    print("--- [Step 5/9] Translating SquashFS root filesystem into POSIX Tar archive ---")
    squashfs_file = os.path.join(ISO_EXTRACTED, "live", "filesystem.squashfs")
    tar_file = os.path.join(BASE_DIR, "filesystem.tar")
    
    if os.path.exists(tar_file):
        os.remove(tar_file)
        
    sqfs2tar_bin = os.path.join(TOOLS_DIR, "sqfs2tar.exe")
    print(f"Running sqfs2tar: {sqfs2tar_bin} {squashfs_file} -> {tar_file}")
    
    start_time = time.time()
    with open(tar_file, 'wb') as f:
        subprocess.run([sqfs2tar_bin, squashfs_file], stdout=f, check=True)
    print(f"Root filesystem translated successfully in {time.time() - start_time:.2f} seconds.\n")

    # 6. Apply Agami OS Customizations & Inject Educational Dashboard into Tar
    print("--- [Step 6/9] Streaming customizations and assets into Tar archive ---")
    custom_tar_file = os.path.join(BASE_DIR, "filesystem_custom.tar")
    if os.path.exists(custom_tar_file):
        os.remove(custom_tar_file)
        
    hub_src_dir = os.path.join(BASE_DIR, "agami_hub")
    
    # Custom files to inject
    overrides = {
        "usr/share/backgrounds/agami_wallpaper.png",
        "usr/share/pixmaps/agami-logo.png",
        "etc/skel/Desktop/agami-hub.desktop",
        "etc/skel/Desktop/agami-install-software.desktop",
        "usr/local/bin/agami-init.sh",
        "usr/local/bin/agami-install-software.sh",
        "etc/xdg/autostart/agami-init.desktop",
    }

    # Desktop Entry Launcher Content
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

    # Educational Software Installer Launcher Content
    installer_launcher_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Install Educational Software
Comment=Install LibreOffice, Brave, programming IDEs, and STEM simulators
Exec=bash -c "sudo /usr/local/bin/agami-install-software.sh; echo; echo 'Press Enter to close...'; read"
Icon=system-software-install
Terminal=true
Categories=System;Setup;
"""

    # Init Script Content
    init_script_content = """#!/bin/bash
# Wait for D-Bus and GSettings services to initialize
sleep 3

# Set custom Agami OS 4K wallpaper (for both Light and Dark GNOME themes)
gsettings set org.gnome.desktop.background picture-uri "file:///usr/share/backgrounds/agami_wallpaper.png"
gsettings set org.gnome.desktop.background picture-uri-dark "file:///usr/share/backgrounds/agami_wallpaper.png"
gsettings set org.gnome.desktop.background picture-options "zoom"

# Set Screensaver Background
gsettings set org.gnome.desktop.screensaver picture-uri "file:///usr/share/backgrounds/agami_wallpaper.png"

# Ensure desktop shortcuts are executable
chmod +x /home/user/Desktop/agami-hub.desktop 2>/dev/null
chmod +x /home/user/Desktop/agami-install-software.desktop 2>/dev/null
chmod +x /etc/skel/Desktop/agami-hub.desktop 2>/dev/null
chmod +x /etc/skel/Desktop/agami-install-software.desktop 2>/dev/null
"""

    # Post-Install Software Setup Script Content
    installer_script_content = """#!/bin/bash
set -e

# Visual formatting
GREEN='\\033[0;32m'
TEAL='\\033[0;36m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m' # No Color

echo -e "${TEAL}=========================================================================="
echo -e "          Agami OS Education - Software Installation Suite                "
echo -e "                     Built by Softsasi (www.softsasi.com)                 "
echo -e "==========================================================================${NC}\\n"

# Verify we are running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Error: Please run this script with sudo or as root!${NC}"
  echo "Example: sudo $0"
  exit 1
fi

echo -e "${YELLOW}Step 1/8: Updating and Upgrading System Repositories...${NC}"
apt update && apt upgrade -y

echo -e "\\n${YELLOW}Step 2/8: Installing LibreOffice & PDF/eBook Viewers...${NC}"
apt install -y libreoffice libreoffice-l10n-en-us libreoffice-help-en-us evince calibre xournalpp

echo -e "\\n${YELLOW}Step 3/8: Setting up Brave Secure Web Browser...${NC}"
apt install -y curl apt-transport-https
curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list
apt update && apt install -y brave-browser

echo -e "\\n${YELLOW}Step 4/8: Installing Kid-Friendly Educational Tools...${NC}"
apt install -y gcompris-qt tuxmath tuxtype tuxpaint tuxpaint-stamps-default

echo -e "\\n${YELLOW}Step 5/8: Installing STEM, Geography & Astronomy Simulators...${NC}"
apt install -y kalzium marble kstars kanagram kwordquiz stellarium wxmaxima step avogadro gnuplot geogebra

echo -e "\\n${YELLOW}Step 6/8: Installing Programming IDEs & Learning Environments...${NC}"
apt install -y scratch thonny geany arduino bluej

echo -e "\\n${YELLOW}Step 7/8: Installing High-End Multimedia & Creative suites...${NC}"
apt install -y gimp inkscape krita kdenlive audacity musescore3

echo -e "\\n${YELLOW}Step 8/8: Installing System utilities, Security & Accessibility...${NC}"
apt install -y flatpak timeshift orca onboard redshift redshift-gtk synaptic keepassxc clamav clamav-daemon clamtk ufw
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
ufw enable || true

# Debian Edu meta-packages
echo -e "\\n${YELLOW}Optional: Installing Debian Edu project packages...${NC}"
apt install -y education-mathematics education-science education-language education-geography education-misc

echo -e "\\n${YELLOW}Cleaning up package cache...${NC}"
apt autoremove -y && apt clean

echo -e "\\n${GREEN}=========================================================================="
echo -e "🎉 SUCCESS! All educational software packages have been installed!"
echo -e "You can now find them in your GNOME Applications Menu!"
echo -e "==========================================================================${NC}"
"""

    # Autostart Entry Content
    autostart_content = """[Desktop Entry]
Type=Application
Name=Agami OS Init Daemon
Exec=/usr/local/bin/agami-init.sh
Terminal=false
NoDisplay=true
"""

    import io
    start_time = time.time()
    
    with tarfile.open(tar_file, 'r') as tar_in, tarfile.open(custom_tar_file, 'w') as tar_out:
        count = 0
        copied = 0
        skipped = 0
        
        for member in tar_in:
            count += 1
            name = member.name.lstrip("./")
            if name in overrides or name.startswith("usr/share/agami-hub/"):
                skipped += 1
                continue
                
            if member.isfile():
                f = tar_in.extractfile(member)
                tar_out.addfile(member, f)
            else:
                tar_out.addfile(member)
            copied += 1
            
        # 1. Custom Wallpaper
        info = tarfile.TarInfo(name="usr/share/backgrounds/agami_wallpaper.png")
        info.size = os.path.getsize(wallpaper_path)
        info.mode = 0o644
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        with open(wallpaper_path, 'rb') as f:
            tar_out.addfile(info, f)

        # 2. Custom Logo
        info = tarfile.TarInfo(name="usr/share/pixmaps/agami-logo.png")
        info.size = os.path.getsize(logo_path)
        info.mode = 0o644
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        with open(logo_path, 'rb') as f:
            tar_out.addfile(info, f)

        # 3. Desktop Hub Shortcut
        shortcut_data = launcher_content.encode('utf-8')
        info = tarfile.TarInfo(name="etc/skel/Desktop/agami-hub.desktop")
        info.size = len(shortcut_data)
        info.mode = 0o755
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        tar_out.addfile(info, io.BytesIO(shortcut_data))

        # 4. Desktop Installer Shortcut
        installer_launcher_data = installer_launcher_content.encode('utf-8')
        info = tarfile.TarInfo(name="etc/skel/Desktop/agami-install-software.desktop")
        info.size = len(installer_launcher_data)
        info.mode = 0o755
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        tar_out.addfile(info, io.BytesIO(installer_launcher_data))

        # 5. Init Script
        init_data = init_script_content.encode('utf-8')
        info = tarfile.TarInfo(name="usr/local/bin/agami-init.sh")
        info.size = len(init_data)
        info.mode = 0o755
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        tar_out.addfile(info, io.BytesIO(init_data))

        # 6. Post-Install Software Setup Script
        installer_script_data = installer_script_content.encode('utf-8')
        info = tarfile.TarInfo(name="usr/local/bin/agami-install-software.sh")
        info.size = len(installer_script_data)
        info.mode = 0o755
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        tar_out.addfile(info, io.BytesIO(installer_script_data))

        # 7. Autostart Desktop Entry
        autostart_data = autostart_content.encode('utf-8')
        info = tarfile.TarInfo(name="etc/xdg/autostart/agami-init.desktop")
        info.size = len(autostart_data)
        info.mode = 0o644
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        tar_out.addfile(info, io.BytesIO(autostart_data))

        # 8. Agami Education Hub HTML files
        for root, dirs, files in os.walk(hub_src_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, hub_src_dir).replace('\\', '/')
                tar_path = f"usr/share/agami-hub/{rel_path}"
                
                info = tarfile.TarInfo(name=tar_path)
                info.size = os.path.getsize(full_path)
                info.mode = 0o644
                info.uid = 0
                info.gid = 0
                info.uname = "root"
                info.gname = "root"
                with open(full_path, 'rb') as f:
                    tar_out.addfile(info, f)
                    
    # Clean up unmodified input tar file
    os.remove(tar_file)
    print(f"Branding, installer, and portal successfully injected in {time.time() - start_time:.2f} seconds.\n")

    # 7. Repack filesystem using tar2sqfs
    print("--- [Step 7/9] Repacking customized root filesystem (SquashFS) ---")
    
    # Delete old squashfs from the extracted ISO structure
    if os.path.exists(squashfs_file):
        os.remove(squashfs_file)
        
    tar2sqfs_bin = os.path.join(TOOLS_DIR, "tar2sqfs.exe")
    
    # Detect CPU jobs
    cpu_count = os.cpu_count() or 4
    print(f"Compressing with {cpu_count} threads using xz (optimized level 3)...")
    
    start_time = time.time()
    with open(custom_tar_file, 'rb') as infile:
        subprocess.run(
            [tar2sqfs_bin, "--compressor", "xz", "-X", "level=3", "-j", str(cpu_count), "--force", squashfs_file],
            stdin=infile,
            check=True
        )
        
    # Clean up custom tar file
    os.remove(custom_tar_file)
    print(f"SquashFS compressed and repacked successfully in {time.time() - start_time:.2f} seconds.\n")

    # 8. Extract original El Torito boot params from base.iso
    print("--- [Step 8/9] Extracting original bootloader layout parameters ---")
    xorriso_bin = os.path.join(TOOLS_DIR, "xorriso.exe")
    
    cmd_report = [xorriso_bin, "-indev", BASE_ISO_PATH, "-report_el_torito", "as_mkisofs"]
    print(f"Running: {' '.join(cmd_report)}")
    res = subprocess.run(cmd_report, capture_output=True, text=True, check=True)
    
    # Parse output to extract options
    original_args = res.stdout.strip().splitlines()
    clean_args = []
    
    for line in original_args:
        line = line.strip()
        if not line:
            continue
        if any(line.startswith(prefix) for prefix in ["xorriso", "Drive current", "Media current", "Media status", "Boot record", "Media summary", "Volume id"]):
            continue
        if "-isohybrid-mbr" in line:
            continue
        
        try:
            tokens = shlex.split(line)
            if len(tokens) >= 2 and tokens[0] == "-V":
                tokens[1] = "Agami_OS_Edu"
            clean_args.extend(tokens)
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
            
    print(f"Sanitized arguments compiled.\n")

    # 9. Generate bootable Hybrid ISO using xorriso
    print("--- [Step 9/9] Generating bootable Hybrid ISO image ---")
    
    if os.path.exists(OUTPUT_ISO_PATH):
        os.remove(OUTPUT_ISO_PATH)
        
    xorriso_args = [
        xorriso_bin,
        "-as", "mkisofs",
    ]
    xorriso_args.extend(clean_args)
    xorriso_args.extend([
        "-isohybrid-mbr", "tools/isohdpfx.bin",
        "-o", OUTPUT_ISO_NAME,
        "iso_extracted"
    ])
    
    print(f"Running final xorriso compilation in base directory...")
    subprocess.run(xorriso_args, cwd=BASE_DIR, check=True)
    
    print("\n==========================================================================")
    print("SUCCESS! Agami OS Education has been built successfully!")
    print(f"Output File: {OUTPUT_ISO_PATH}")
    print(f"Total Time Taken: {(time.time() - global_start_time)/60:.2f} minutes")
    print("==========================================================================\n")

if __name__ == "__main__":
    import tarfile
    main()
