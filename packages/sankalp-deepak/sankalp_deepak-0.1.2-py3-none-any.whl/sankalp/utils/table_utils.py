from rich import console, table


def render_table(
    data: list[list],
    headers: list[str],
    title: str = "",
    show_header: bool = True,
    show_lines: bool = True,
) -> None:
    """
    Render a table with the given data and headers.

    :param data: List of dictionaries containing the data to be displayed in the table.
    :param headers: List of strings representing the headers of the table.
    :param title: Title of the table.
    :param show_header: Whether to show the header row.
    :param show_lines: Whether to show lines between rows.
    :return: A string representation of the rendered table.
    """
    rich_table = table.Table(
        title=title, show_header=show_header, show_lines=show_lines
    )

    for header in headers:
        rich_table.add_column(header)

    for row in data:
        rich_table.add_row(*row)

    console.Console().print(rich_table)
