import json
import os

import click
import requests
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY

USER_ID = os.environ.get("USER_ID", None)
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", None)
API_TOKEN = os.environ.get("API_TOKEN", None)


def prepare_request():
    """
    Method to prepare headers and args for request
    :return: Headers and body for the request
    """
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
    return headers, data


def get_all_transactions(ignore_donuts):
    """
    Gets all the transactions from the API
    :param ignore_donuts: if true, ignores all the transactions at krispy kreme and dunkin.
    :return: returns all the transactions as a list
    """
    headers, data = prepare_request()
    response = requests.post("https://2016.api.levelmoney.com/api/v2/core/get-all-transactions", data=json.dumps(data),
                             headers=headers)
    if response.status_code == 200:
        json_response = response.json()['transactions']
        filtered_json_response = []
        for transaction in json_response:
            transaction['transaction-time'] = datetime.strptime(transaction['transaction-time'],
                                                                "%Y-%m-%dT%H:%M:%S.%fZ")
            if ignore_donuts:
                if transaction['merchant'] == "Krispy Kreme Donuts" or transaction['merchant'] == "DUNKIN #336784":
                    continue
            filtered_json_response.append(transaction)
        return filtered_json_response
    else:
        click.echo("Something went wrong in downloading the transactions.")


def add_crystal_ball_transactions(all_transactions, ignore_donuts):
    """
    Gets the projected transactions for the current month (hardcoded as 01,2017)
    :param all_transactions: Previously downloaded transactions from all transactions API
    :param ignore_donuts: if true, ignores all the transactions at krispy kreme and dunkin.
    :return: Returns the list of all transactions with the newly downlaoded transactions appened to it
    """
    headers, data = prepare_request()
    data['month'] = 1
    data['year'] = 2017
    response = requests.post("https://2016.api.levelmoney.com/api/v2/core/projected-transactions-for-month",
                             data=json.dumps(data),
                             headers=headers)
    if response.status_code == 200:
        json_response = response.json()['transactions']
        for transaction in json_response:
            transaction['transaction-time'] = datetime.strptime(transaction['transaction-time'],
                                                                "%Y-%m-%dT%H:%M:%S.%fZ")
            if ignore_donuts:
                if transaction['merchant'] == "Krispy Kreme Donuts" or transaction['merchant'] == "DUNKIN #336784":
                    continue
            all_transactions.append(transaction)
    else:
        click.echo("unable to get crystal ball transactions.")
    return all_transactions


def get_income_and_expenditure_for_month(month, year, all_transactions):
    """
    Primary aggregator function which calculates the income and expenditure for a given month
    :param month: month for the transactions to be filtered on
    :param year: year for the transactions to be filtered on
    :param all_transactions: list of all the downloaded transactions
    :return: income and expenditure for the current month
    """
    income = expenditure = 0
    for transaction in all_transactions:
        # check for date
        transaction_date = transaction['transaction-time']
        if transaction_date.month == month and transaction_date.year == year:
            # date is within our year and month
            # check if it is income or expenditure
            if transaction['amount'] > 0:
                # transaction is an income if amount > 0
                income += round(float(transaction['amount'] / 10000), 2)
            else:
                # transaction is an expenditure
                expenditure += round(float((transaction['amount'] * -1) / 10000), 2)
    return {
        "income": income,
        "expenditure": expenditure
    }


@click.command()
@click.option('--ignore-donuts', is_flag=True, default=False)
@click.option('--crystal-ball', is_flag=True, default=False)
def transactions(ignore_donuts, crystal_ball):
    """
    Driver method.
    :param ignore_donuts: if true, ignores donut transactions
    :param crystal_ball: if true, gets the predicted transactions for current month and includes it in the average
    :return: prints the income and expenditure for every month and average for all the months
    """
    all_transactions = get_all_transactions(ignore_donuts)
    if crystal_ball:
        all_transactions = add_crystal_ball_transactions(all_transactions, ignore_donuts)
    start_date = datetime(2014, 10, 01)
    end_date = datetime(2017, 01, 31)
    all_transactions_for_averages = []
    for date in rrule(MONTHLY, dtstart=start_date, until=end_date):
        values_for_current_month = get_income_and_expenditure_for_month(date.month, date.year, all_transactions)
        print "%s: %s" % (date.strftime("%Y-%m-%d"), values_for_current_month)
        all_transactions_for_averages.append(values_for_current_month)
    print "Average income: %s" % round(
        float(sum(t['income'] for t in all_transactions_for_averages)) / len(all_transactions_for_averages), 2)
    print "Average expenditure: %s" % round(
        float(sum(t['expenditure'] for t in all_transactions_for_averages)) / len(all_transactions_for_averages), 2)


if __name__ == '__main__':
    transactions()
