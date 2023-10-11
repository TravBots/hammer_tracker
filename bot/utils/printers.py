def rows_to_piped_strings(df, columns):
    rows = [" | ".join(map(str, row)) for row in df[columns].values]
    return "\n".join(rows)


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
