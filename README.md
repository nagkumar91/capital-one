# Capital one coding challenge

This repo contains a script that gets the data from capital one's API and aggregates the transactions by month with 2 additional features.

#### Steps to run:
0. Setup a virtual environment & activate it (suggested)
1. Clone the repo
```
git clone git@github.com:nagkumar91/capital-one.git
```
2. install all the requirements
```
pip install -r requirements.txt
```
3. Run the script with help to see the options
```
python transactions.py --help
```
4. Run the script with appropriate option(s)
5. You can also set up the args for the API from the environment instead of typing it in everytime.
```
export USER_ID=<value for user id without enclosing brackets>
export AUTH_TOKEN=<value for user id without enclosing brackets>
export API_TOKEN=<value for user id without enclosing brackets>
```