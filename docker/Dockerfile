# Things to keep in mind:
# 1. Every apt-get update makes the build process slower and creates a larger image
# 2. Each RUN command creates a new layer and increases image size

ARG ROS_DISTRO=jazzy
ARG UBUNTU_VER=24.04

# There are two images: ros:${ROS_DISTRO}-ros-base and osrf/ros:${ROS_DISTRO}-desktop
# For a full list of what packages each installs, go to https://www.ros.org/reps/rep-2001.html#jazzy-jalisco-may-2024-may-2029
FROM ros:${ROS_DISTRO}-ros-base


#################### ENV SETUP ####################
ARG USERNAME=ubuntu
ARG REPO_NAME=tibble_redo
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV PYTHONPATH="${PYTHONPATH}:/usr/local/lib"


#################### SYSTEM + DEV TOOLS ####################
# Cache the downloads to speed up rebuilds
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    # Core system
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    apt-transport-https \
    wget \
    sudo \
    udev \
    libusb-1.0-0 \
    libserial-dev \
    usbutils \
    # Build + Python
    build-essential \
    python3-pip \
    python3-venv \
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-rosdep \
    python3-argcomplete \
    bash-completion \
    pipx \
    python-is-python3 \
    libserial-dev \
    # GUI libs (some of these might be unnecessary, test it later TODO)
    libegl1-mesa-dev \
    libglu1-mesa-dev \
    libxv1 \
    libxtst6


#################### PLATFORMIO ####################
RUN pipx install platformio && pipx ensurepath


#################### USER SETUP ####################

# This needs to run before COPY so you can use the variables
RUN if ! id -u $USER_UID >/dev/null 2>&1; then \
    groupadd --gid $USER_GID $USERNAME && \
    useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Fedora host serial devices use GID 18 so add yourself just in case
RUN groupadd -g 18 hostserial || true && \
    usermod -aG hostserial $USERNAME


#################### ROS PACKAGES ####################
# The .dockerignore will only allow package.xml files to be copied over
# This is important because otherwise the layer would need to be rebuilt every time the source code changes
COPY --chown=${USERNAME}:${USERNAME} src/ /home/${USERNAME}/workspaces/${REPO_NAME}/src/

# Use rosdep to install dependencies instead of manually listing every single one
# This does mean that the package.xml of every ros2 package needs to be maintained and updated
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    rosdep update && \
    rosdep install \
    --from-paths /home/${USERNAME}/workspaces/${REPO_NAME}/src \
    --ignore-src \
    --rosdistro ${ROS_DISTRO} \
    -y


#################### CTRE PHOENIX ####################
RUN curl -s --compressed -o /usr/share/keyrings/ctr-pubkey.gpg "https://deb.ctr-electronics.com/ctr-pubkey.gpg" && \
    curl -s --compressed -o /etc/apt/sources.list.d/ctr2026.list "https://deb.ctr-electronics.com/ctr2026.list" && \
    sed -i 's/\[signed-by=/[arch=amd64,arm64 signed-by=/' /etc/apt/sources.list.d/ctr2026.list
# Cache for faster rebuilds
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends phoenix6

# Required for CTRE (the TalonFX motor API/SDK) to build correctly with colcon
RUN CTRE_LIB_PATH=$(dirname $(find /usr -name "libCTRE_Phoenix6.so" | head -n 1)) && \
    echo "Found Phoenix6 at: $CTRE_LIB_PATH" && \
    echo "$CTRE_LIB_PATH" > /etc/ld.so.conf.d/ctre.conf && \
    ldconfig


#################### VirtualGL ####################

# VirtualGL is required for MacOS to run GUI apps in a docker container
RUN wget -q -O- https://packagecloud.io/dcommander/virtualgl/gpgkey | \
    gpg --dearmor >/etc/apt/trusted.gpg.d/VirtualGL.gpg
RUN wget -O /etc/apt/sources.list.d/VirtualGL.list https://raw.githubusercontent.com/VirtualGL/repo/main/VirtualGL.list

RUN apt-get update && apt-get install -y --no-install-recommends virtualgl


#################### ROS ENV ####################

# This is required for SSHing into the container and having source set up
# It applies the source command system-wide to every user in the container
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" \
    > /etc/profile.d/ros2.sh


#################### USER ENV ####################
USER $USERNAME
WORKDIR /home/${USERNAME}/workspaces/${REPO_NAME}/

# This step sources the underlay and overlay so you can immediately run ros2 launch commands (if it's already built)
RUN printf "\nsource /opt/ros/${ROS_DISTRO}/setup.bash\n" >> ~/.bashrc && \
    printf "if [ -f home/${USERNAME}/workspaces/${REPO_NAME}/install/setup.bash ]; then source home/${USERNAME}/workspaces/${REPO_NAME}/install/setup.bash; fi\n" >> ~/.bashrc
