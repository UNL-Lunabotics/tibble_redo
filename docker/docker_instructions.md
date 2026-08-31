- [Requirements](#requirements)
- [Recommended VSCode Extensions](#recommended-vscode-extensions)
- [Windows](#windows)
  - [WSL Install and Setup](#wsl-install-and-setup)
  - [USB Passthrough](#usb-passthrough)
  - [Docker Install and Setup](#docker-install-and-setup)
- [MacOS](#macos)
- [Linux](#linux)
- [IF YOU HAVE AN NVIDIA GPU YOU HAVE TO DO THIS](#if-you-have-an-nvidia-gpu-you-have-to-do-this)
- [Launch and Runtime](#launch-and-runtime)

# Requirements

In order for this repository to be able to run, any Docker or containerized setup needs the following:

1. USB passthrough (gamepads, cameras, sensors, etc)
2. GPU/hardware acceleration access
3. Display/GUI access
4. Full network access
5. Access to serial microcontroller writing

If you decide to come up with your own containerized solution, keep these requirements in mind. Note, some operating systems require extra work to get these requirements, and some operating systems can accomplish all of them just via the compose file. If the instructions in this document do not cover a requirement, assume it is automatically covered by compose.

# Recommended VSCode Extensions

- [Remote Development by Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
- [Container Tools by Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-containers)

Remote Development is a bundle of extensions that will allow you to interact with Docker and WSL in VSCode. Container Tools lets you more easily manage containers (starting, stopping, etc) and has better functionality with Docker Compose.

# Windows

Basically, the only way to get this to work is by using WSL. ROS2 is *technically* supported on Windows, but this project sure isn't. If you want to run it, either install all the libraries manually on bare metal WSL or utilize this docker setup to do so. It is recommended you use Docker (which will run on WSL).

## WSL Install and Setup

What is WSL? It stands for Windows Subsystem for Linux. It basically allows you to install an entire Linux operating system on your computer that you can access as a subsystem. Your primary operating system will still be Windows, you can just access Linux through a command line and develop in it as if it were a real Linux machine. This has it's limitations, but it should work enough for ROS2 development kinda sorta.

You can follow the [official Windows WSL install instructions](https://learn.microsoft.com/en-us/windows/wsl/install) at the link, but I'll repeat it here for convenience.

1. Open PowerShell in administrator mode
    - Press the Windows button on your keyboard or by pressing the menu in the taskbar
    - Type in PowerShell
    - Click on the Run as administrator option
2. Type in the command `wsl --install` to install WSL itself
3. Restart your computer
4. Open PowerShell again (admin mode not required)
5. Type in the command `wsl --list --online` to view the available Linux distributions
6. Type in the command `wsl --install --Ubuntu-24.04`
7. Type in your Unix username (doesn't really matter)
8. Type in your Unix password (remember this you will be typing it a lot, or write it down)
9. Close that PowerShell window and do not continue working in it or it'll break things
10. Type WSL in the windows start menu and open the app that looks like a penguin (this will be how you open WSL any time you want to)

Now that WSL is installed, you have to add an SSH key in order to be able to use GitHub.
1. Open WSL using the app NOT PowerShell (see above)
2. Set up a GitHub SSH key so you can pull/push in WSL
    - Type the command `ssh-keygen -t ed25519 -C "your_email@example.com"`
    - Press enter to accept default file location
    - Optionally enter a passphrase
    - Type the command `cat ~/.ssh/id_ed25519.pub`
    - Highlight the entire output, starting with ssh-ed25519 and ending with your email address, and copy it
    - Go to https://github.com/settings/keys
    - Click the New SSH key green button in the topish right
    - Put whatever title you want (ex. WSL_Ubuntu-24.04 or something)
    - Paste the contents of the cat command into the Key box
    - Click the Add SSH key at the bottom
3. Type the command `mkdir repos && cd repos`
4. Clone the repository via SSH
    - Go to the repository on github.com
    - Click the green button that says Code
    - Switch over to the SSH tab
    - Copy that
    - In the WSL terminal, type `git clone <whatyoucopied>`

## USB Passthrough

**WSL does not have access to any USB devices on your computer by default.** You have to manually link them. Follow these instructions to set up [USB Passthrough on WSL](https://unl-lunabotics.github.io/docs/Technical/Setup%20Dev%20Tools/Windows/Device-Passthrough-for-Windows.html). Otherwise, nothing connected to your computer by USB will be accessible by WSL.

You will have to manually add any USB you want through this process. This does not support hot plugging. **If you want your USB device to automatically attach to WSL any time it is plugged in,** use the command `usbipd attach --wsl --auto-attach --busid <BUSID>` instead of what the tutorial says to. Note: this is USB port sensitive and will not work unless the USB device is plugged into the same port every time.

## Docker Install and Setup

You can follow the official guide to [Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/#install-docker-desktop-on-windows). Docker Desktop is the dashboard app that lets you manage your Docker containers, while Docker Engine is the actual software that will create your containers. Installing Docker Desktop will install engine. For Windows, installing it is NOT optional.

After installation, open Docker Desktop
1. Navigate to Settings -> General -> Use the WSL 2 based engine should be checked
2. Navigate to Settings -> Resoures -> WSL Integration -> Enable integration with my default WSL distro should be checked to yes. If you have more than one distro you're using, make sure Ubuntu-24.04 one for ROS2 is enabled additionally

**Do not compose the container in Windows, ALWAYS compose it in WSL. The instructions for which are in [Launch and Runtime](#launch-and-runtime).** Run those commands in your WSL instance.

# MacOS

Currently, USB passthrough to a Docker container on MacOS is experimental and not really working. If you want to develop for this project with no USB passthrough, follow the [official Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/) instructions. This method has not been tested and may or may not actually work at all.

Instead of using Docker, it is recommended to use a virtual machine. Scripts and instructions for this have already been created by Aiden Kimmerling at https://unl-lunabotics.github.io/docs/Technical/Setup%20Dev%20Tools/macOS/.

**IF YOU USE MACOS, ADD THIS TO YOUR compose.override.yaml FILE**
```yaml
services:
  tibble_base:
    environment:
      - XDG_RUNTIME_DIR=/run/user/$(id -u)
      - DISPLAY=host.docker.internal:0
      - VGL_DISPLAY=egl
```

# Linux

To install docker engine (not desktop, desktop is not available on Linux), follow this guide: https://docs.docker.com/engine/install/ for your distribution.

**DO NOT FORGET TO DO THE [POST INSTALLATION](https://docs.docker.com/engine/install/linux-postinstall) STEPS.**

**Any time you restart your computer**, you will HAVE to do `xhost +local:` to give the container access to X11 displays or any GUI ran from the container will crash. There are ways to automate this, but I have not implemented any of them personally.

# IF YOU HAVE AN NVIDIA GPU YOU HAVE TO DO THIS

Nvidia GPUs are special little monsters that require special permissions in the docker compose. The normal compose will not work for you, and we can't add fixes into the normal compose because it'll break it for everyone not using Nvidia.

If you have Nvidia, create a file named `compose.override.yaml` (THIS NAME HAS TO MATCH THE COMPOSE FILE NAME JUST WITH .override. IN IT) in the docker/ directory. When this is present, it will merge with the existing compose automatically, and is ignored by git so it's like a .env override. In the file, paste the following:

```yaml
services:
  tibble_base:
    gpus: all
```

# Launch and Runtime

This project uses Docker Compose. If you want to read more, you can at the [Official Docker Compose](https://docs.docker.com/compose/) documentation, but basically, it's just how we specify the configuration of the container. The actual Dockerfile specifies how to build the container and the compose is the settings.

This project utilizes [compose profiles](https://docs.docker.com/compose/how-tos/profiles/), which means there are different container configurations already pre-written depending on what you want to do in the container. This project has two compose files (unless you added an override then there's also compose.override.yaml): `compose-base.yaml` and `compose.yaml`. The base compose contains all configurations that are universal to every profile, and compose-yaml contains the profiles (which extend the base). 

**There are two compose profiles and you HAVE to pick one one to use, there is no default.**
1. `wireless` assumes you are using two computers, onboard and groundstation, to do wireless remote control of the rover. It might have some configurable IPs you have to do but should work across a variety of network channels
2. `wired` assumes you are controlling the rover with a controller plugged into the ONBOARD computer. This setup still allows for two computers if you are SSH'd into onboard and the controller is still plugged into the onboard computer.

**To create the container and attach a terminal shell**, run the following commands from the repository root. Or, you can use Container Tools from [Recommended VSCode Extensions](#recommended-vscode-extensions), right click on `compose.yaml`, and select Compose Up - Select Services.
```bash
cd docker/ && docker compose --profile <PROFILE> up
# Wait for it to finish creating the container...
docker exec -it tibble_<PROFILE> bash
```

**To create the container and attach VSCode**, compose the container using the first command above, install Container Tools from [Recommended VSCode Extensions](#recommended-vscode-extensions). Open the crate icon in the left toolbar, right click on your tibble container, and select Attach Visual Studio Code. This also makes it easier to remove, stop, start, or otherwise manage containers. I personally recommend just using a terminal shell.