import sqlparse
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def pprint_query(query):
    console.print("\n[bold]SQL Query:[/bold]")
    # Format the SQL query
    formatted_query = sqlparse.format(str(query), reindent=True, keyword_case="upper", indent_width=2)
    # Apply syntax highlighting to the formatted query
    syntax = Syntax(formatted_query, "sql", theme="monokai", line_numbers=True)
    console.print(syntax)


def pprint_result_set(results):
    console.print("\n[bold]Query Results:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")

    # Convert results to a list to handle both SQLAlchemy and SQLModel result proxies
    results_list = list(results)

    if results_list:
        # Add columns dynamically based on the first result
        for key in results_list[0]._fields:
            table.add_column(key.capitalize(), style="cyan")

        # Add all results to the table
        for row in results_list:
            table.add_row(*[str(getattr(row, key)) for key in row._fields])

    console.print(table)
