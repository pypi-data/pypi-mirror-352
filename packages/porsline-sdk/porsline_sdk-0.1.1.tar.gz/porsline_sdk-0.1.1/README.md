# Porsline SDK
A lightweight Python SDK to interact with Porsline forms and convert Jalali dates to Gregorian.

## Features
Fetch and parse form data from Porsline

Convert Jalali dates to Gregorian

Designed for integration with surveys

## Installation

`pip install porsline-sdk`

## Usage
````python
from porsline import Porsline

instance = Porsline(API_KEY)

all_forms = instance.get_forms()
form = instance.get_form(all_forms[0].id)
print(form.cols)
print(form.responses()) # To get all responses
print(form.responses('2025-05-19T10:32:16')) # to get from one point

````
