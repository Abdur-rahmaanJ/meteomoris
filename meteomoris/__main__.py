import click
from meteomoris import *

@click.group()
def cli():
    pass


@cli.command()
def dashboard():
    print("---")

@cli.command(help="Week forecast")
def forecast():
    get_weekforecast(print=True)

@cli.command(help="Sunrise (Mauritius)")
def sunrisemu():
    get_sunrisemu(print=True)

@cli.command(help="Sunrise (Rodrigues)")
def sunriserodr():
    get_sunriserodr(print=True)

@cli.command(help="Sunrise (Rodrigues)")
def message():
    get_main_message(print=True)

def main():
    cli(obj={})

if __name__ == "__main__":
    main()
