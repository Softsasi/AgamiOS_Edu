# Agami OS Education 🎓

[![Base](https://img.shields.io/badge/Base-Debian%2013%20%28Trixie%29-blue?logo=debian)](https://www.debian.org/)
[![Desktop](https://img.shields.io/badge/Desktop-GNOME-purple?logo=gnome)](https://www.gnome.org/)
[![Platform](https://img.shields.io/badge/Build%20Platform-Windows-0078D4?logo=windows)](https://microsoft.com/)

**Agami OS Education** is a premium, customized educational operating system built on top of **Debian 13 (Trixie)** stable release featuring the sleek and modern **GNOME desktop environment**. Designed specifically for students and educators, it integrates tailored learning tools, custom branding, and a beautiful offline learning portal.

This repository hosts the **Windows-native build system** that automates the downloading, deconstructing, customizing, and repacking of the Debian Live ISO directly on standard Windows environments without requiring WSL or Docker.

---

## Key Features 🚀

*   **Premium Branding**: Custom 4K gradient desktop background with the official **Agami OS** logo dynamically set for light and dark modes.
*   **GNOME Desktop Experience**: Clean, intuitive, and modern user experience with customized settings.
*   **Agami Education Hub**: A built-in offline educational dashboard featuring:
    *   Interactive math and science utilities.
    *   Self-guided learning modules and quizzes.
    *   Offline reference guides, textbooks, and documentation.
    *   Direct launcher shortcut right on the desktop.
*   **Legacy BIOS & Modern UEFI Booting**: Fully hybrid bootable ISO utilizing advanced Isolinux, GRUB, and EFI partition parameters.

---

## Custom OS Architecture 📂

```
Agami_OS_Education/
├── .gitignore                   # Excludes large binaries/ISOs from Git
├── README.md                    # Project documentation
├── build_agami.py               # Main Python build orchestrator
├── logo.png                     # Official Agami OS Logo
├── wallpaper_4k.png             # Generated 4K custom desktop wallpaper
├── tools/                       # Downloaded native Windows utilities (Git-ignored)
│   ├── mksquashfs.exe           # SquashFS packer
│   ├── unsquashfs.exe         # SquashFS unpacker
│   └── xorriso.exe              # Bootable hybrid ISO generator
├── agami_hub/                   # Source for the Agami Education Hub
│   ├── index.html               # Main dashboard portal
│   ├── css/                     # Sleek premium styles
│   └── js/                      # Interactive logic & learning modules
└── build_files/                 # System configuration overrides
    ├── agami-init.sh            # Live OS boot initialization script
    ├── agami-init.desktop       # System autostart configuration entry
    └── Agami Education Hub.desktop # Desktop launcher for the Hub
```

---

## How It Works (Windows-Native Build Pipeline) 🛠️

Since the build is performed on Windows without virtualization, we use native Windows executables compiled for binary manipulation:

1.  **Deconstruction**: The build script extracts the official Debian GNOME Live ISO using `7-Zip` and unpacks the compressed root filesystem (`filesystem.squashfs`) using a Windows-native `unsquashfs.exe`.
2.  **Customization**:
    *   Injects the **Agami Education Hub** files into `/usr/share/agami-hub/`.
    *   Configures system skeletons `/etc/skel/` so that every logged-in user automatically receives the desktop shortcuts and custom backgrounds.
    *   Injects an autostart daemon `/etc/xdg/autostart/agami-init.desktop` that triggers a startup script `/usr/local/bin/agami-init.sh` upon booting to apply GNOME overrides (e.g., setting the wallpaper) dynamically inside the Linux environment.
3.  **Reconstruction**:
    *   Repacks the root filesystem back to high-compression SquashFS using `mksquashfs.exe`.
    *   Generates a fully bootable hybrid ISO using `xorriso.exe` with precise boot sector and EFI system partition arguments.

---

## Build Prerequisites 📋

*   **Operating System**: Windows 10 or 11 (64-bit).
*   **Python**: Version 3.10 or higher.
*   **7-Zip**: Installed at `C:\Program Files\7-Zip\` (used for fast extraction).
*   **Logo File**: Located in the project root as `logo.png`.

---

## Developer Guide: Run the Build ⚙️

To build the custom operating system image:

1.  Place your official logo as `logo.png` in the repository root.
2.  Open your Windows command prompt/PowerShell inside this directory.
3.  Run the build orchestration script:
    ```powershell
    python build_agami.py
    ```
4.  The script will automatically download the required toolchain, retrieve the official Debian live base, apply the modifications, and output `Agami_OS_Education.iso` in the workspace.

---

*Agami OS Education is an open-source initiative designed to bring beautiful, robust, and accessible educational environments to students globally.*
