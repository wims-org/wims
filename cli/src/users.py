import typer

app = typer.Typer()

@app.command()
def create():
    print("not yet implemented")

@app.command()
def delete():
    print("not yet implemented")

if __name__ == "__main__":
    app()
