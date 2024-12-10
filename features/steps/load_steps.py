######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Product Steps

Steps file for products.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

@given('the following products')
def step_impl(context):
    """ Delete all Products and load new ones """
    #
    # List all of the products and delete them one by one
    #
    rest_endpoint = f"{context.base_url}/products"
    context.resp = requests.get(rest_endpoint)
    assert(context.resp.status_code == HTTP_200_OK)
    for product in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{product['id']}")
        assert(context.resp.status_code == HTTP_204_NO_CONTENT)

    #
    # load the database with new products
    #
    for row in context.table:
        # | name       | description     | price   | available | category   |
        # | Hat        | A red fedora    | 59.95   | True      | CLOTHS     |
        # | Shoes      | Blue shoes      | 120.50  | False     | CLOTHS     |
        # | Big Mac    | 1/4 lb burger   | 5.99    | True      | FOOD       |
        # | Sheets     | Full bed sheets | 87.00   | True      | HOUSEWARES |
        products = [
            {
                "name": "Hat",
                "description": "A red fedora",
                "price": 59.95,
                "available": True,
                "category": Category.CLOTHS,
            },
            {
                "name": "Shoes",
                "description": "Blue shoes",
                "price": 120.50.
                "available": False,
                "category": Category.CLOTHS,
            },
            {
                "name": "Big Mac",
                "description": "1/4 lb burger",
                "price": 5.99.
                "available": True,
                "category": Category.FOOD,
            },
            {
                "name": "Sheets",
                "description": "Full bed sheets",
                "price": 87.00.
                "available": True,
                "category": Category.HOUSEWARES,
            },
        ]
        #
        # ADD YOUR CODE HERE TO CREATE PRODUCTS VIA THE REST API
        #
