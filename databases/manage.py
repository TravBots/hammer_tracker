import click
import glob
import sqlite3
from pathlib import Path
import os


def _get_views() -> list:
    return glob.glob("game_servers/views/*.sql")


def _get_dbs() -> list:
    return glob.glob("game_servers/*.db")


@click.group()
def manage():
    pass


@manage.command(help="Refresh all views")
def refresh_views():
    dbs = _get_dbs()

    print("Refreshing views...")
    views = _get_views()

    for db in dbs:
        cnx = sqlite3.connect(db)
        print(f"Opened {db}")
        for view_path in views:
            print(f"Executing {view_path}")
            with open(view_path, "r") as view:
                cnx.executescript(view.read())
        cnx.close()

    return


@manage.command(help="Copy production db to dev")
@click.argument("username")
def copy_prod_db(username):
    dbs = _get_dbs()
    backup_dir = Path("game_servers/backup/")

    print("First checking backup directory...")
    if backup_dir.exists():
        print("Backup directory exists, clearing")
        for file in backup_dir.glob("*.db"):
            file.unlink()
        print("Backup directory cleared")
    else:
        print("Backup directory does not exist, creating")
        backup_dir.mkdir(parents=True, exist_ok=True)
        print("Backup directory created")

    print("Backing up development dbs...")
    for db in dbs:
        backup_path = str(backup_dir) + "/" + db.split("/")[-1]
        print(f"Backing up {db} to path {backup_path}")
        Path(db).replace(backup_path)

    print("Copying production dbs to development...")
    command = f"scp {username}@5.161.229.151:'/projects/hammer_tracker/databases/game_servers/*.db' ./game_servers"
    print(f"Running command: {command}")
    os.system(command)
    print("Copy completed successfully!")


@manage.command(help="Initialize analytics database")
def init_analytics():
    """Initialize the analytics database"""
    print("Initializing analytics database...")

    analytics_path = Path("analytics")
    if not analytics_path.exists():
        print("Creating analytics directory")
        analytics_path.mkdir(parents=True, exist_ok=True)

    db_path = analytics_path / "analytics.db"

    try:
        with open("sql/create_table_analytics.sql", "r") as f:
            create_table_sql = f.read()

        print(f"Creating analytics database at {db_path}")
        with sqlite3.connect(db_path) as conn:
            conn.executescript(create_table_sql)
            conn.commit()
        print("Analytics database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize analytics database: {e}")
        raise


if __name__ == "__main__":
    manage()
