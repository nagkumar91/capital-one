import click
import os


@click.command()
def intialize():
    """Initializes the connection to mongodb and downloads the data"""
    click.echo("Checking if pymongo is installed")
    try:
        import pymongo
        click.echo("pymongo found")
    except:
        click.echo("Pymongo not installed.")
        return



if __name__ == '__main__':
    intialize()
