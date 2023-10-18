import click
import glob
import sqlite3


def _get_views() -> list:
    return glob.glob("game_servers/views/*.sql")


def _get_dbs() -> list:
    return glob.glob("game_servers/*.db")


@click.command
@click.option("--refresh-views", is_flag=True, help="Refresh all views")
def manage(refresh_views):
    dbs = _get_dbs()
    if refresh_views:
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


if __name__ == "__main__":
    manage()
