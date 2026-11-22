#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# FILE:         docker_setup.sh
# AUTHOR:       Ella Moody <moodyellam@gmail.com> (Linux and Windows), Aiden Kimmerling <https://github.com/TheKing349> (macOS)
# CREATED:      07-02-2026
# LAST EDITED:  11-19-2026
# DESCRIPTION:  This script configures the HOST MACHINE to run the docker container
#               setup for this repository. Run it before composing the containers,
#               and in some cases run it anytime you restart your computer.
#               This script does NOT install docker, it assumes it is already installed.
# USAGE:        sudo ./scripts/docker_setup.sh [-l] [-w] [-m]
# DEPENDS:      bash, unzip
# LICENSE:      Apache 2.0
# -----------------------------------------------------------------------------

set -euo pipefail

# if [ "$EUID" -ne 0 ]; then
#   echo "[ERROR] Please run this script as root (with sudo)."
#   exit 1
# fi

LINUX=0
WSL=0
MAC=0
while getopts "lwm" flag; do
    case "${flag}" in
        l) LINUX=1 ; echo "[INFO] Setting up Linux host machine..." ;;
        w) WSL=1 ; echo "[INFO] Setting up WSL (Windows 11) host machine..." ;;
        m) MAC=1 ; echo "[INFO] Setting up macOS host machine..." ;;
    esac
done

if [[ $((LINUX + WSL + MAC)) > 1 ]]; then
    echo "[ERROR] Only one OS can be selected. Please only enter -l OR -w OR -m and not more than one."
    exit 1
fi

if [[ $LINUX == 1 ]]; then
    xhost + local:

    RULES_FILE=/etc/udev/rules.d/99-realsense-libusb.rules
    IIO_RULES_FILE=/etc/udev/rules.d/99-realsense-iio.rules
    RELOAD=0

    if [[ ! -f $RULES_FILE ]]; then
        sudo curl -fsSL \
            https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules \
            -o "$RULES_FILE" || { echo "[ERROR] Failed to download udev rules"; exit 1; }
        RELOAD=1
    fi

    # The upstream rules chmod the sysfs files but leave /dev/iio* as root-only,
    # which blocks the D435i IMU for non-root users (e.g. inside the container).
    if [[ ! -f $IIO_RULES_FILE ]]; then
        echo 'SUBSYSTEM=="iio", ATTRS{idVendor}=="8086", ATTRS{idProduct}=="0b3a", MODE="0666"' \
            | sudo tee "$IIO_RULES_FILE" > /dev/null
        RELOAD=1
    fi

    if [[ $RELOAD == 1 ]]; then
        sudo udevadm control --reload-rules
        sudo udevadm trigger
    fi
    
    echo "[SUCCESS] Linux is configured. This will need to be ran every time you restart your computer."
elif [[ $WSL == 1 ]]; then
    echo "[REQUEST] What is your windows username? Case sensitive. Press enter to continue."
    read -r USERNAME
    
    # Turns out the C_DRIVE location can change based on bash
    #   terminal emulator. These *should* be the only 2 options 
    if [ -d "/mnt/c" ]; then
        C_DRIVE="/mnt/c"
    elif [ -d "/c" ]; then
        C_DRIVE="/c"
    else
        echo "Error: Could not find Windows C: drive mount." >&2
        exit 1
    fi

    DIR="$C_DRIVE/Users/$USERNAME"

    # Unzip may not be installed in WSL by default
    if ! command -v unzip &> /dev/null; then
        echo "[INFO] Installing required program: unzip..."
        echo "[INFO] A password may be required to install"
        sudo apt install unzip
    fi

    echo "[INFO] Downloading and unzipping the custom kernel made by Aiden Kimmerling (thank you Aiden)..."
    
    curl -L https://github.com/TheKing349/WSL2-Linux-Kernel/releases/latest/download/vmlinux+modules.zip -o $DIR/Downloads/VMLinuxPlusModules.zip
    unzip -e $DIR/Downloads/VMLinuxPlusModules.zip -d $DIR/Downloads/VMLinuxPlusModules

    echo "[INFO] Creating a new directory and moving folder contents there..."
    mkdir -p "$DIR/wsl"
    mv $DIR/Downloads/VMLinuxPlusModules/modules.vhdx $DIR/wsl
    mv $DIR/Downloads/VMLinuxPlusModules/vmlinux $DIR/wsl

    echo "[INFO] Creating the wsl configuration file.."
    # This breaks if there's indentation just go with it
    # Needs double backslashes and each backslash needs an escape
cat << EOF > "$DIR/.wslconfig"
[wsl2]
kernel="C:\\\\Users\\\\$USERNAME\\\\wsl\\\\vmlinux"
kernelModules="C:\\\\Users\\\\$USERNAME\\\\wsl\\\\modules.vhdx"
EOF

    echo "[REQUEST] To load the custom kernel, you have to restart WSL. This script will shut it down for you, and then you can open a terminal and type wsl to start it again."
    echo "After restarting WSL, you can type uname -r into the WSL terminal and if the result is theking349-joystick, it was a success."
    echo "Press ENTER to proceed when you have read all the instructions, or CTRL+C to stop."
    read -r THROWAWAY

    wsl.exe --shutdown

elif [[ $MAC == 1 ]]; then
    function install_app_brew() {
        local cmd=$1

        echo "[INFO] $cmd not found. Installing using Homebrew..."

        if [ ! -d "/opt/homebrew/bin" ]; then
            echo "[ERROR] Homebrew not found. Cannot install $cmd. Install $cmd manually or install Homebrew."
            exit 2
        fi

        brew install --cask $cmd
    }

    echo "[INFO] Opening XQuartz"
    if ! open -Ra "XQuartz" &> /dev/null; then
        install_app_brew XQuartz
    fi

    # Allows connections from network clients in XQuartz
    defaults write org.xquartz.X11 nolisten_tcp -bool false
    open -a XQuartz

    # Allow only localhost connection to be accessible
    xhost +localhost

    echo "[INFO] Starting VirtualGL client"
    if [ ! -d "/opt/VirtualGL/bin" ]; then
        install_app_brew VirtualGL
    fi
    /opt/VirtualGL/bin/vglclient -ipv6 -detach

    echo "[SUCCESS] macOS is configured. This will need to be ran every time you restart your computer."
else
    echo "[ERROR] Please use either -l -w or -m for linux, windows, or mac setup."
fi