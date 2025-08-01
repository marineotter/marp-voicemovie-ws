FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    gnupg \
    ca-certificates \
    git \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome for marp-cli
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Japanese fonts for better text rendering
RUN apt-get update && \
    apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-takao-gothic \
    fonts-takao-mincho \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# add user "devcontainer" with sudo privileges
RUN useradd -m -s /bin/bash devcontainer && \
    echo "devcontainer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

# Set the user to "devcontainer"
USER devcontainer

# Install node.js
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
ENV NVM_DIR="/home/devcontainer/.nvm"
ENV NODE_VERSION="22.17.1"
RUN . "$NVM_DIR/nvm.sh" && \
    nvm install "$NODE_VERSION" && \
    nvm use "$NODE_VERSION" && \
    nvm alias default "$NODE_VERSION" && \
    nvm cache clear
ENV PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"

# Install marp-cli and verify it works with Chrome
RUN npx -y @marp-team/marp-cli@latest --help && \
    google-chrome --version

# Install Python dependencies
RUN pip3 install --break-system-packages --user requests
RUN pip3 install --break-system-packages --user moviepy opencv-python pillow

# Create scripts directory and copy Python scripts
USER root
RUN mkdir -p /scripts && chmod 755 /scripts
COPY marp_note_to_voice.py /scripts/marp_note_to_voice.py
COPY convert_to_movie.py /scripts/convert_to_movie.py
RUN chmod +x /scripts/*.py

# Switch back to devcontainer user
USER devcontainer
