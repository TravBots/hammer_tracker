FROM python:3.11.1-slim-bullseye

ARG DISCORD_BOT_TOKEN

WORKDIR /app

# Copy entire project
COPY . .

# Install make
RUN apt-get update && apt-get install -y make

# Setup environment and install dependencies
RUN make setup DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN

# Ensure proper permissions
RUN chmod -R 755 /app

# Set working directory to bot for running the application
WORKDIR /app/bot

ENTRYPOINT ["python3"]