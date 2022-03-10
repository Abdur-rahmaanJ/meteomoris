import click


@click.group()
def cli():
    pass


@cli.command()
def dashboard():
    print("---")


def main():
    cli(obj={})

if __name__ == "__main__":
    main()
