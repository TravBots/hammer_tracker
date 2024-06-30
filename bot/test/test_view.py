import sqlite3


def test_village_age_view():
    DB = "../databases/game_servers/am3.db"
    # Get all village_ids that have 1 insert_count in v_village_ages
    query = """
        SELECT village_id
        FROM v_village_ages
        WHERE insert_count = 1
    """
    conn = sqlite3.connect(DB)
    print(f"Running sql:\n{query}")
    cursor = conn.execute(query)

    desc = cursor.description
    column_names = [col[0] for col in desc]
    results = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    conn.close()

    for result in results:
        # Get all the rows for each village_id and assert that the count is 1
        query = f"""
            SELECT *
            FROM map_history
            WHERE village_id = {result['village_id']}
        """
        conn = sqlite3.connect(DB)
        print(f"Running sql:\n{query}")
        cursor = conn.execute(query)

        desc = cursor.description
        column_names = [col[0] for col in desc]
        rows = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        conn.close()

        print(f"Found {len(rows)} rows for village_id {result['village_id']}")
        assert len(rows) == 1


if __name__ == "__main__":
    test_village_age_view()
