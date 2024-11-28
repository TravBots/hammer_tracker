FROM python:3.11.1-slim-bullseye

ARG DISCORD_BOT_TOKEN

ADD . /bot

# Uncomment this line if you are running locally
# RUN rm /bot/config.ini

WORKDIR /bot

# Install make
RUN apt-get update && apt-get install -y make

RUN make setup DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN
RUN pip3 install -r requirements.txt

# Create a directory for the database and set permissions
RUN mkdir -p /databases/bot_servers && chmod 777 /databases/bot_servers

# Ensure proper permissions for the bot directory
RUN chmod -R 755 /bot

ENTRYPOINT ["python3"]