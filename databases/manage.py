import click
import glob
import sqlite3
from pathlib import Path
import os


def _get_views() -> list:
    return glob.glob("game_servers/views/*.sql")


def _get_dbs() -> list:
    return glob.glob("game_servers/*.db")


def _get_bot_servers() -> list:
    return glob.glob("bot_servers/*.db")


def _get_scripts() -> list:
    return sorted(glob.glob("scripts/*.sql"))


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


@manage.command(help="Execute a specific database script")
@click.argument("script_name")
def execute_script(script_name):
    dbs = _get_bot_servers()
    script_path = f"scripts/{script_name}"

    if not os.path.exists(script_path):
        print(f"Error: Script {script_path} not found")
        return

    print(f"Executing script {script_name}...")

    for db in dbs:
        print(f"Processing database: {db}")
        cnx = sqlite3.connect(db)

        try:
            with open(script_path, "r") as script_file:
                print(f"Executing script on {db}")
                cnx.executescript(script_file.read())
                print(f"Script executed successfully on {db}")
        except sqlite3.Error as e:
            print(f"Error executing script on {db}: {e}")
            cnx.rollback()
        finally:
            cnx.close()

    return


if __name__ == "__main__":
    manage()
