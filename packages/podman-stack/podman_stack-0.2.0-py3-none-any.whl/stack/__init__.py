import logging
import typer
from podman_compose import PodmanCompose
from rich.logging import RichHandler

from stack.config import stack
from stack.systemd import service_app

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

app = typer.Typer()

app.add_typer(service_app, name='service')

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