# 🚀 Master OS Builder Prompt: The Ultimate AI Instructions

This document contains a comprehensive, production-ready **Master Prompt** designed for cutting-edge AI coding assistants. If you feed this prompt into a powerful AI model in the future, it will automatically orchestrate, write the build scripts, design the offline portal, configure the keyboard hookups, and master the hybrid ISO for a customized operating system identical to **Agami OS Education Version 2.0**.

---

## 📋 How to Use This Document
1. Copy the entire contents of the **Master Prompt** section below.
2. Paste it into your AI coding assistant (like Antigravity / Claude / GPT) at the start of a new session.
3. Place your custom assets (`logo.png`, `wallpaper.png`, `boot_splash.png`) in your workspace, and watch the AI assemble the entire customized operating system natively!

---

# 👑 THE MASTER PROMPT (Copy from Here)

```text
You are an expert operating system systems engineer and premium UI designer. Your goal is to build a customized, bootable hybrid Live ISO named "Agami_OS_Education.iso" based on a Debian 13 (Trixie) GNOME Live template. 

The build system must support BOTH:
1. An automated Windows-native Python build orchestrator (operating without WSL, Hyper-V, or Docker).
2. A direct step-by-step Linux-native terminal command-line pipeline.

---

### I. CORE ARCHITECTURE SPECIFICATIONS

1. Base Template ISO: "debian-live-13.5.0-amd64-gnome.iso"
2. Custom Brand Wallpaper: "wallpaper.png" (set for light/dark GNOME desktops)
3. Custom OS Branding Logo: "logo.png"
4. Custom Boot Splash Screen: "boot_splash.png" (applied to both GRUB and Legacy BIOS bootloaders)
5. Custom Offline Educational Portal: "Agami Education Hub" (beautiful glassmorphic UI)

---

### II. BUILD PIPELINE LOGIC (WINDOWS-NATIVE PYTHON ORCHESTRATOR)

You must write a comprehensive Python orchestrator script named "build_agami.py" that implements these exact build stages:
1. Setup Workspace & Verify Assets: Ensure "logo.png", "wallpaper.png", and "boot_splash.png" are in the root directory. Setup a "tools/" folder.
2. Setup Toolchain: Automatically download Windows-native SquashFS-NG tools (tar2sqfs, sqfs2tar) and xorriso binaries.
3. Base ISO Retrieval: Automatically download the official Debian GNOME Live ISO if not present in the workspace.
4. MBR Sector Extraction: Extract the first 432 bytes of the original ISO to act as the Isohybrid MBR boot partition template.
5. Deconstruct Base ISO: Call local "7-Zip" to extract the base ISO structure into "iso_extracted/". Overwrite GRUB (/boot/grub/splash.png) and Legacy isolinux (/isolinux/splash.png) boot splash images with our branded "boot_splash.png".
6. Tar Decompression: Execute "sqfs2tar" to extract "filesystem.squashfs" into a POSIX-compliant "filesystem.tar" archive, fully preserving symlinks.
7. Customize Rootfs: Stream customizations directly into the POSIX tarball (or directory) to avoid path corruptions.
8. SquashFS Recompression: Recompress the customized archive back into "filesystem.squashfs" using "tar2sqfs" with high-compression XZ algorithm parameters, block size of 1MB, and 8 parallel threads.
9. Mastering: Re-assemble a UEFI + Legacy hybrid bootable ISO using xorriso with precise partition, boot catalog, and GPT/MBR boot headers.
10. Cleanup: Automatically delete massive intermediate tar files (~18GB total) upon a successful compile to preserve disk space.

---

### III. EXACT OS CUSTOMIZATIONS & INJECTIONS

Your build system must inject the following files and configurations into the SquashFS filesystem:

#### 1. Language & Wallpaper Autostart Initialization Script
* Target Path: /usr/local/bin/agami-init.sh (marked executable)
* System Autostart Hook: /etc/xdg/autostart/agami-init.desktop
* Script Rationale: GNOME Live OS ignores pre-boot system-wide input overrides. You must configure this startup script to run as a user-session agent on GNOME login to execute:
  gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'us'), ('ibus', 'm17n:bn:phonetic')]"
  gsettings set org.gnome.desktop.input-sources show-all-sources true
  gsettings set org.gnome.desktop.background picture-uri 'file:///usr/share/backgrounds/agami_wallpaper.png'
  gsettings set org.gnome.desktop.background picture-uri-dark 'file:///usr/share/backgrounds/agami_wallpaper.png'

#### 2. Glassmorphic Offline Portal: "Agami Education Hub"
* Target Directory: /usr/share/agami-hub/
* Access Launcher Shortcut: /etc/skel/Desktop/agami-hub.desktop (copied dynamically for all user profiles)
* Portal Requirements: Write index.html, style.css, and script.js inside "agami_hub/".
  - Theme: Premium dark-slate teal glassmorphism, Outfit Google typography, sleek hover micro-animations, glowing active badges.
  - Tab 1 (STEM & Library): Quick launch buttons for Geography, Astronomy, Physics, and Chemistry simulation packages, along with Kiwix offline desktop reader.
  - Tab 2 (Bangla Typing): A fully interactive offline Bangla phonetic Typing Sandbox. Provide real-time typing fields, character count meters, and a graphic cheat sheet for phonetic layout mappings.
  - Tab 3 (USB Persistence): Comprehensive tutorial explaining Rufus and Ventoy persistence volume allocation steps to allow students to save files between reboots.

#### 3. Branded Boot Splash Screen Override
* Target Paths:
  - UEFI GRUB: /boot/grub/splash.png
  - Legacy ISOLINUX: /isolinux/splash.png
* Overwrite these paths in the extracted ISO structure with our high-resolution "boot_splash.png".

#### 4. Automated Educational Software Installer Script
* Launcher Path: /etc/skel/Desktop/agami-install-software.desktop
* Script Path: /usr/local/bin/agami-install-software.sh (marked executable)
* Script Logic: To avoid image bloating, write an installer bash script that, when triggered with internet access, automates:
  - Retrieving and registering secure Brave Browser GPG keys.
  - Installing full LibreOffice suites (with Bangla localization/help files), Kiwix Desktop, GCompris Qt, Tuxmath, Scratch, GeoGebra, and chemistry molecular editors.
  - Cleaning temporary caches.

---

### IV. LINUX-NATIVE COMMAND PIPELINE DOCUMENTATION

You must document the native Linux command-line steps inside the README.md so developers working in pure Linux terminal environments can perform all build steps manually:
1. `7z x base.iso -oextracted_iso/`
2. `unsquashfs -d rootfs/ extracted_iso/live/filesystem.squashfs`
3. Custom paths copy instructions:
   - Hub -> `rootfs/usr/share/agami-hub/`
   - Wallpapers/Logo -> `rootfs/usr/share/backgrounds/agami_wallpaper.png`, `rootfs/usr/share/pixmaps/agami-logo.png`
   - Desktop launchers -> `rootfs/etc/skel/Desktop/`
   - Autostarts -> `rootfs/etc/xdg/autostart/agami-init.desktop`, `rootfs/usr/local/bin/agami-init.sh`
   - Splashes -> `extracted_iso/boot/grub/splash.png`, `extracted_iso/isolinux/splash.png`
4. `mksquashfs rootfs/ extracted_iso/live/filesystem.squashfs -comp xz -b 1M`
5. `xorriso -as mkisofs` command mapping with precise UEFI/BIOS hybrid parameters.

---

### V. CORE TEAM & LICENSING ATTRIBUTION

Ensure your documentation includes proper licensing and team attributions:
* Website: agami.softsasi.com
* Download Link: agami.softsasi.com/os/Agami_OS_Education.iso
* Core Team:
  - Shakil Anower Samrat (Chief Executive Officer)
  - Izaz Uddin Mahmud (Researcher)
  - Sumaiya Fatima Nahin (Project Manager)
  - Lian Mollick (Embedded Engineer and UX Designer)
* License: GPL v3.0 (Include a standard license text in the repo root).

Please implement the entire codebase, directory mappings, HTML/CSS/JS dashboard interfaces, and build orchestrator structures immediately! Do not use any generic placeholders. All guides, keyboard switcher mappings, and installation arrays must be fully defined and functional.
```

---

## 🛠️ Developer Verification & Build Checklist

When your future AI assistant finishes compiling the files, make sure the workspace matches this layout before running the compilation command:

### 1. Root Workspace Checklist
* [ ] **`logo.png`**: Branded logo image.
* [ ] **`wallpaper.png`**: Premium 4K gradient desktop background.
* [ ] **`boot_splash.png`**: Themed UEFI/BIOS bootloader background.
* [ ] **`build_agami.py`**: The automated Python native builder script.
* [ ] **`LICENSE`**: Fully written GPLv3 text file.
* [ ] **`README.md`**: Fully written Markdown description with our core team.
* [ ] **`ROADMAP.md`**: Software packages setup script file.
* [ ] **`agami_hub/`**: Contains the complete offline glassmorphic dashboard files.

### 2. Output Compilation Commands
Once verified, standard execution is completely automated:

* **On Windows**:
  ```powershell
  python build_agami.py
  ```
* **On Linux**:
  Follow the Linux Native Build Pipeline commands documented in the [README.md](file:///C:/Users/softs/Documents/Agami_OS_Education/README.md) or run the Python orchestrator script directly.

---
*Created by Softsasi as an open-source tool to empower teachers, developers, and builders worldwide.*
