# Greystone Labs Loan Calculator

## Overview

The goal of this application is to provide a REST API for a Loan Amortization Calculator, as per the spec of the spec of Greystone Labs Code Challenge PDF.

## Setup

This application was developed using the following python version.
```
$ python -V
Python 3.9.2
```

Once your version is configured, setup the dependencies.
```
$ pip install -r requirements.txt
```

## Run

At this point, the application is ready to run.
```
$ uvicorn app:app
```

Startup will initialize a sqlite3 file `database.db`

The REST APIs will be available at `localhost:8000`

API docs are provided by `localhost:8000/docs`

## Testing

The application has one test which simulates full use of the service and uses every API endpoint.
```
$ pytest
```

Calculation results were manually confirmed against an online loan calculator:

https://www.calculator.net/loan-calculator.html?cloanamount=500000&cloanterm=30&cloantermmonth=0&cinterestrate=6&ccompound=monthly&cpayback=month&x=72&y=27#amortized-result
