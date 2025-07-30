from typing import Optional

import typer
from typing_extensions import Annotated

from frogml_storage.cli._login_cli import login as prompt_login

app = typer.Typer(add_completion=False)


@app.command("login")
def login(
    url: Annotated[Optional[str], typer.Option(help="Artifactory base url")] = None,
    username: Annotated[Optional[str], typer.Option(help="The user's username")] = None,
    password: Annotated[Optional[str], typer.Option(help="The user's password")] = None,
    token: Annotated[
        Optional[str], typer.Option(help="Access token to authenticate")
    ] = None,
    anonymous: Annotated[
        bool, typer.Option(help="Run login as anonymous user")
    ] = False,
    interactive: Annotated[
        bool, typer.Option(help="Login with interactive flow")
    ] = False,
) -> None:
    # url_value = url if url is not None else ""
    prompt_login(url, username, password, token, anonymous, interactive)


@app.callback()
def callback():
    pass


def main():
    app()


if __name__ == "__main__":
    main()
