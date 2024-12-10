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
        payload = {
            "name": row["name"],
            "description": row["description"],
            "price": row["price"],
            "category": row["category"],
            "available": row["available"] in ['True', 'true', '1'],
        }
        response = self.client.post(rest_endpoint, json=payload)
        assert(response.status_code == status.HTTP_201_CREATED)

@when(u'I press the "Create" button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I press the "Create" button')


@then(u'I should see the message "Success"')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see the message "Success"')


@when(u'I press the "Clear" button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I press the "Clear" button')


@when(u'I press the "Retrieve" button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I press the "Retrieve" button')


@when(u'I press the "Search" button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I press the "Search" button')


@when(u'I set the "Price" field to "69.98"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I set the "Price" field to "69.98"')


@when(u'I press the "Update" button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I press the "Update" button')


@when(u'I press the "Delete" button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I press the "Delete" button')


@then(u'I should see the message "Failed"')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see the message "Failed"')


@then(u'I should see "Hat" in the results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see "Hat" in the results')


@then(u'I should see "Shoes" in the results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see "Shoes" in the results')


@then(u'I should see "Big Mac" in the results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see "Big Mac" in the results')


@then(u'I should see "Sheets" in the results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see "Sheets" in the results')


@when(u'I set the "Availability" dropdown to "False"')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I set the "Availability" dropdown to "False"')
