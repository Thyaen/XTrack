FROM ros:humble-ros-base

# Install Python3, pip, rclpy & Build-Tools
RUN apt-get update && \
    apt-get install -y \
      python3-pip \
      ros-humble-rclpy \
      ros-humble-std-msgs \
      python3-opencv \
      jq \
      && pip3 install --upgrade pip

# Set working directory
WORKDIR /usr/src/app
x
# Copy and install Python requirements (ohne rclpy)
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN pip3 install gevent gevent-websocket


# Copy application code
COPY . .

# Build Tailwind CSS
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.3/tailwindcss-linux-x64 \
  && mv tailwindcss-linux-x64 tailwindcss && chmod +x tailwindcss

# Expose Flask port
EXPOSE 5000

# Launch the Flask app
CMD ["python3", "app.py"]
