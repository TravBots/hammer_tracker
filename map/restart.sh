kill -HUP `ps -C gunicorn fch -o pid | head -n 1`
