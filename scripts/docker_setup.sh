#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# FILE:         docker_setup.sh
# AUTHOR:       Ella Moody <moodyellam@gmail.com>
# CREATED:      07-02-2026
# LAST EDITED:  07-02-2026
# DESCRIPTION:  This script configures the HOST MACHINE to run the docker container
#               setup for this repository. Run it before composing the containers,
#               and in some cases run it anytime you restart your computer.
#               This script does NOT install docker, it assumes it is already installed.
# USAGE:        ./scripts/docker_setup.sh [-l] [-w] [-m]
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
        m) MAC=1 ; echo "[INFO] Setting up MacOS host machine..." ;;
    esac
done

if [[ $((LINUX + WSL + MAC)) > 1 ]]; then
    echo "[ERROR] Only one OS can be selected. Please only enter -l OR -w OR -m and not more than one."
    exit 1
fi

if [[ $LINUX == 1 ]]; then
    xhost+ local:
    echo "[SUCCESS] Linux is configured. This will need to be ran every time you restart your computer."
elif [[ $WSL == 1 ]]; then
    echo "hi wsl"
    echo "[REQUEST] What is your windows username? Case sensitive. Press enter to continue."
    read -r USERNAME

    DIR="/mnt/c/Users/$USERNAME"

    echo "[INFO] Downloading and unzipping the custom kernel made by Aiden Kimmerling (thank you Aiden)..."
    wget https://github.com/TheKing349/WSL2-Linux-Kernel/releases/latest/download/vmlinux+modules.zip -O $DIR/Downloads/VMLinuxPlusModules.zip
    unzip -e $DIR/Downloads/VMLinuxPlusModules.zip -d $DIR/Downloads/VMLinuxPlusModules

    echo "[INFO] Creating a new directory and moving folder contents there..."
    mkdir -p "/mnt/c/Users/$USERNAME/wsl"
    mv $DIR/Downloads/VMLinuxPlusModules/modules.vhdx $DIR/wsl
    mv $DIR/Downloads/VMLinuxPlusModules/vmlinux $DIR/wsl

    echo "[INFO] Creating the wsl configuration file.."
    # This breaks if there's indentation just go with it
cat << EOF > "$DIR/wsl/.wsl.config"
[wsl2]
kernel=C:\\Users\\$USERNAME\\wsl\\vmlinux
kernelModules=C:\\Users\\$USERNAME\\wsl\\modules.vhdx
EOF

    echo "[REQUEST] To load the custom kernel, you have to restart WSL. This script will shut it down for you, and then you can open a terminal and type wsl to start it again."
    echo "After restarting WSL, you can type uname -r into the WSL terminal and if the result is theking349-joystick, it was a success."
    echo "Press ENTER to proceed when you have read all the instructions, or CTRL+C to stop."
    read -r THROWAWAY

    wsl.exe --shutdown

elif [[ $MAC == 1 ]]; then
    echo "hi mac"
fi