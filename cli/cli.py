import typer
from src import items, users,scanner

app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(users.app, name="users")
app.add_typer(items.app, name="items")
app.add_typer(scanner.app, name="scanner")

if __name__ == "__main__":
    app()
