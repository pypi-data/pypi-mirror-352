import os
import click


@click.command(
    name="muv-pip-install",
    context_settings={"help_option_names": ["--help", "-h"]},
)
@click.argument("names", nargs=-1, required=True)
def muv_pip_install(names):
    for name in names:
        url = f"https://gitee.com/mpypi/{name}.git"
        command = f"uv pip install git+{url}"
        os.system(command)
