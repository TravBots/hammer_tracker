def rows_to_piped_strings(df, columns):
    # Calculate max widths for each column
    max_widths = [max([len(str(val)) for val in df[col]]) for col in columns]

    # Use max widths to format each row
    rows = [
        " | ".join([f"{str(val).ljust(width)}" for val, width in zip(row, max_widths)])
        for row in df[columns].values
    ]

    return "\t\t\t\n".join(rows)
