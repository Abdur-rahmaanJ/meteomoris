import click

@click.group()
def cli():
    pass

@cli.command()
def dashboard():
    print('---')

if __name__ == '__main__':
    cli(obj={})