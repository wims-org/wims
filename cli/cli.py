import typer
from src import items, users

app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(users.app, name="users")
app.add_typer(items.app, name="items")

if __name__ == "__main__":
    app()
