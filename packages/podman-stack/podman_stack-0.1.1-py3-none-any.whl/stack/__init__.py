import typer
from podman_compose import PodmanCompose

from stack.config import stack

app = typer.Typer()
compose = PodmanCompose()

@app.command()
def up(stack_name: str):
    with stack(stack_name):
        compose.run('up -d')

@app.command()
def recreate(stack_name: str):
    with stack(stack_name):
        compose.run('up -d --force-recreate')

@app.command()
def down(stack_name: str):
    with stack(stack_name):
        compose.run('down')