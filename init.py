import json
import os

import click
import requests
USER_ID = os.environ.get("USER_ID", None)
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", None)
API_TOKEN = os.environ.get("API_TOKEN", None)


def download_and_insert(transactions):
    if USER_ID:
        user_id = USER_ID
    else:
        user_id = click.prompt("Enter the user id for API")
    if AUTH_TOKEN:
        auth_token = AUTH_TOKEN
    else:
        auth_token = click.prompt("Enter the auth token for API")
    if API_TOKEN:
        api_token = API_TOKEN
    else:
        api_token = click.prompt("Enter the api token")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "args": {
            "uid": int(user_id),
            "token": auth_token,
            "api-token": api_token,
            "json-strict-mode": False,
            "json-verbose-mode": False
        }
    }
    response = requests.post("https://2016.api.levelmoney.com/api/v2/core/get-all-transactions", data=json.dumps(data),
                             headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        click.echo("Response received from API")
        if json_response['error'] == 'no-error':
            for row in json_response['transactions']:
                id = transactions.insert_one(row).inserted_id
        click.echo("Inserted %s documents" % transactions.count())
    else:
        click.echo("Something went wrong. Please check tokens and try again.")


@click.command()
@click.option('--mongo-port', default=27017, type=int)
@click.option('--mongo-host', default="localhost")
@click.option('--mongo-db-name', default="capital_one")
def intialize(mongo_port, mongo_host, mongo_db_name):
    """Initializes the connection to mongodb and downloads the data"""
    click.echo("Checking if pymongo is installed")
    try:
        import pymongo
        from pymongo import MongoClient
        click.echo("pymongo found")
    except:
        click.echo("Pymongo not installed.")
        return
    click.echo("Checking connection to mongo")
    try:
        client = MongoClient(mongo_host, mongo_port, serverSelectionTimeoutMS=1)
        client.server_info()
    except:
        click.echo("Mongo not running on given parameters")
        return
    click.echo("Connected to mongo")
    db = client[mongo_db_name]
    transactions = db.transactions
    if transactions.count() == 0:
        click.echo("Table is empty. Downloading form API")
        download_and_insert(transactions)
    else:
        click.echo("Setup looks good.")


if __name__ == '__main__':
    intialize()
