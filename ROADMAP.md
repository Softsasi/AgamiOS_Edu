# Agami OS Education: Software Installation Roadmap (v2)

This document contains the official software package installation roadmap for the next release (v2) of **Agami OS Education**, built by **Softsasi (www.softsasi.com)**.

## 🚀 Installation & Update Script

To install these educational and productivity tools inside the Debian live environment or during post-installation setup, execute the following commands:

```bash
# Update and upgrade the system first
sudo apt update && sudo apt upgrade -y

# Full LibreOffice suite (Writer, Calc, Impress, Draw, Math, Base)
sudo apt install -y libreoffice libreoffice-l10n-en-us libreoffice-help-en-us

# PDF viewer
sudo apt install -y evince

# eBook reader
sudo apt install -y calibre

# Note-taking with stylus support
sudo apt install -y xournalpp

# Install dependencies
sudo apt install -y curl apt-transport-https

# Add Brave GPG key
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg \
  https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg

# Add Brave repo
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] \
  https://brave-browser-apt-release.s3.brave.com/ stable main" | \
  sudo tee /etc/apt/sources.list.d/brave-browser-release.list

# Install Brave
sudo apt update && sudo apt install -y brave-browser

# GCompris - educational suite for kids
sudo apt install -y gcompris-qt

# Tux tools (math, typing, paint)
sudo apt install -y tuxmath tuxtype tuxpaint tuxpaint-stamps-default

# KDE Edu suite (science, geography, languages)
sudo apt install -y kalzium marble kstars kanagram kwordquiz

# Stellarium - planetarium simulator
sudo apt install -y stellarium

# Scratch - visual programming for beginners
sudo apt install -y scratch

# GeoGebra - geometry, algebra, calculus
sudo apt install -y geogebra

# wxMaxima - computer algebra system
sudo apt install -y wxmaxima

# Step - physics simulator
sudo apt install -y step

# Avogadro - molecular editor
sudo apt install -y avogadro

# Gnuplot - graphing tool
sudo apt install -y gnuplot

# Thonny - beginner Python IDE
sudo apt install -y thonny

# Geany - lightweight multi-language IDE
sudo apt install -y geany

# Arduino IDE
sudo apt install -y arduino

# BlueJ - Java learning environment
sudo apt install -y bluej

# GIMP - image editing
sudo apt install -y gimp

# Inkscape - vector graphics
sudo apt install -y inkscape

# Krita - digital painting
sudo apt install -y krita

# Kdenlive - video editing
sudo apt install -y kdenlive

# Audacity - audio editing
sudo apt install -y audacity

# MuseScore - music notation
sudo apt install -y musescore3

# Flatpak support (more apps from Flathub)
sudo apt install -y flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Timeshift - system snapshots/restore
sudo apt install -y timeshift

# Orca screen reader (accessibility)
sudo apt install -y orca

# Onboard - on-screen keyboard
sudo apt install -y onboard

# Redshift - blue light filter
sudo apt install -y redshift redshift-gtk

# Synaptic - GUI package manager
sudo apt install -y synaptic

# KeePassXC - password manager
sudo apt install -y keepassxc

# ClamAV - antivirus
sudo apt install -y clamav clamav-daemon clamtk

# UFW - simple firewall
sudo apt install -y ufw
sudo ufw enable

# Debian Edu project meta-packages (installs many edu tools at once)
sudo apt install -y education-mathematics education-science \
  education-language education-geography education-misc

# Final cleanup
sudo apt autoremove -y && sudo apt clean
```

---
**Agami OS Education** is built by **Softsasi** ([www.softsasi.com](https://www.softsasi.com)). For support, contact [support@agami.softsasi.com](mailto:support@agami.softsasi.com).
