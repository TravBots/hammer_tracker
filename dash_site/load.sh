ARCH=$(arch)

# Make sure the map.db file exists
if [ ! -f "../core/databases/map.db" ]; then
    echo "Creating map.db..."
    touch ../core/databases/map.db
fi;

# On a mac, $ARCH will be arm64. If so, use version of sqlite installed via homebrew
# On the server, $ARCH will be x86_64, so just use default sqlite
if [ "$ARCH" == "arm64" ]; then
    $(brew --prefix)/opt/sqlite/bin/sqlite3 ../core/databases/map.db < sql/replace_x_world.sql
    echo "Downloading map data..."
    curl -s https://ts3.x1.america.travian.com/map.sql -q > sql/map.sql
    echo "Loading map data..."
    $(brew --prefix)/opt/sqlite/bin/sqlite3 ../core/databases/map.db < sql/map.sql
    $(brew --prefix)/opt/sqlite/bin/sqlite3 ../core/databases/map.db < sql/insert_map_history.sql
    echo "Map history updated"
else
    sqlite3 ../core/databases/map.db < sql/replace_x_world.sql
    echo "Downloading map data..."
    curl -s https://ts3.x1.america.travian.com/map.sql -q > sql/map.sql
    echo "Loading map data..."
    sqlite3 ../core/databases/map.db < sql/map.sql
    sqlite3 ../core/databases/map.db < sql/insert_map_history.sql
    echo "Map history updated"
fi;
