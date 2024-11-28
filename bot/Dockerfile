FROM python:3.11.1-slim-bullseye

ARG DISCORD_BOT_TOKEN

ADD . /bot
RUN rm /bot/config.ini
ADD setup.sh /bot

WORKDIR /bot

RUN chmod +x setup.sh
RUN ./setup.sh $DISCORD_BOT_TOKEN
RUN pip3 install -r requirements.txt

# Create a directory for the database and set permissions
RUN mkdir -p /databases/bot_servers && chmod 777 /databases/bot_servers

# Ensure proper permissions for the bot directory
RUN chmod -R 755 /bot

ENTRYPOINT ["python3"]