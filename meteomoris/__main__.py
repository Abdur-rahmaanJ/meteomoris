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


@cli.command(help="Moonphase")
def moonphase():
    get_moonphase(print=True)

@cli.command(help="Message of the day")
@click.option("--links", is_flag=True, show_default=True, default=False, help="Show message links")
def message(links):
    get_main_message(print_=True, links=links)

def main():
    cli(obj={})

if __name__ == "__main__":
    main()
