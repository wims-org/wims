import typer
import requests


app = typer.Typer()


@app.command()
def create():
    print("not yet implemented")

@app.command()
def delete():
    print("not yet implemented")

@app.command()
def search(query: str):
    payload = {"query": {"term": query}}
    r = requests.post('http://localhost:5005/items/search', json=payload)
    print(r)

if __name__ == "__main__":
    app()
