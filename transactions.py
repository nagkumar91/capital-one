import json
import os

import click
import requests
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY

USER_ID = os.environ.get("USER_ID", None)
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", None)
API_TOKEN = os.environ.get("API_TOKEN", None)


def get_all_transactions():
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
        json_response = response.json()['transactions']
        for transaction in json_response:
            transaction['transaction-time'] = datetime.strptime(transaction['transaction-time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        return json_response
    else:
        click.echo("Something went wrong in downloading the transactions.")


def get_income_and_expenditure_for_month(month, year, all_transactions):
    income = expenditure = income_count = expenditure_count = 0
    for transaction in all_transactions:
        # check for date
        # transaction_date = datetime.strptime(transaction['transaction-time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        transaction_date = transaction['transaction-time']
        if transaction_date.month == month and transaction_date.year == year:
            # date is within our year and month
            # check if it is income or expenditure
            if transaction['amount'] > 0:
                # transaction is an income if amount > 0
                income_count += 1
                income += round(float(transaction['amount']/10000), 2)
            else:
                # transaction is an expenditure
                expenditure_count += 1
                expenditure += round(float((transaction['amount']*-1)/10000), 2)
    avg_income = 0
    avg_expenditure = 0
    if expenditure_count:
        avg_expenditure = round(float(expenditure)/expenditure_count, 2)
    if income_count:
        avg_income = round(float(income)/income_count, 2)
    return {
        "income": income,
        "expenditure": expenditure,
        "avg_expenditure": avg_expenditure,
        "avg_income": avg_income
    }


@click.command()
def transactions():
    all_transactions = get_all_transactions()
    start_date = datetime(2014, 10, 01)
    end_date = datetime(2017, 02, 01)
    for date in rrule(MONTHLY, dtstart=start_date, until=end_date):
        print "%s: %s" % (date.strftime("%Y-%m-%d"), get_income_and_expenditure_for_month(date.month, date.year, all_transactions))


if __name__ == '__main__':
    transactions()
