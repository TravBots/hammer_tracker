if [ ! -d databases ]; then
    mkdir databases
fi

if [ ! -f config.ini ]; then
    touch config.ini
    echo "[default]" >> config.ini
    echo "token =" $1  >> config.ini
    echo "database = databases/default.db" >> config.ini
    echo "" >> config.ini
    echo "[meta]" >> config.ini
    echo "database = databases/meta.db" >> config.ini
fi

