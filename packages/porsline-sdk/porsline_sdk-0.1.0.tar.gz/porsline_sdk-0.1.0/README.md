# Porsline SDK
A lightweight Python SDK to interact with Porsline forms and convert Jalali dates to Gregorian.

## Features
Fetch and parse form data from Porsline

Convert Jalali dates to Gregorian

Designed for integration with surveys

## Installation

`pip install porsline-sdk`

## Usage
````
from porsline.client import PorslineClient

client = PorslineClient(api_key="your_api_key")
form = client.get_form("form_id")
print(form.cols)
````
