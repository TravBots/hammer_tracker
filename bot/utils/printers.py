# from table2ascii import table2ascii as t2a, PresetStyle


def rows_to_piped_strings(df, columns):
    # Calculate max widths for each column
    max_widths = [max([len(str(val)) for val in df[col]]) for col in columns]

    # Use max widths to format each row
    rows = [
        " | ".join([f"{str(val).ljust(width)}" for val, width in zip(row, max_widths)])
        for row in df[columns].values
    ]

    return "\t\t\t\n".join(rows)


def asterisk_table(df, columns):
    # Determine the width of each column, accounting for the added padding spaces for column names
    col_widths = {}
    for col in columns:
        max_width = max(
            df[col].astype(str).apply(len).max(), len(col) + 2
        )  # +2 for the spaces on either side of the column name
        col_widths[col] = max_width

    # Function to generate a single row, centering the values
    def generate_row(items):
        return (
            "="
            + "=".join(
                item.center(col_widths[col]) for col, item in zip(columns, items)
            )
            + "="
        )

    # Generate table
    table = []

    # Add top border
    table.append("=" * (sum(col_widths.values()) + len(columns) + 1))

    # Add header, padding column names with a space on either side
    table.append(generate_row([" " + col + " " for col in columns]))

    # Add separator
    table.append("=" * (sum(col_widths.values()) + len(columns) + 1))

    # Add rows
    for _, row in df[columns].iterrows():
        table.append(generate_row(row.astype(str).tolist()))

    # Add bottom border
    table.append("=" * (sum(col_widths.values()) + len(columns) + 1))

    return "\n".join(table)

# TODO: Remove?
# def ascii_table(header, body):
#     return t2a(header=header, body=body, first_col_heading=True)
