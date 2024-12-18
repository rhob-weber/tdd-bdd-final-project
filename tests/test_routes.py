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
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_routes.py:TestProductRoutes
"""
import os
import logging
from decimal import Decimal
from unittest import TestCase
from urllib.parse import quote_plus
from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ############################################################
    # Utility function to bulk create products
    ############################################################
    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    def _get_product(self, product_id: int) -> dict:
        """Utility method to get a product"""
        request_url = f"{BASE_URL}/{product_id}"
        response = self.client.get(request_url)
        if response.status_code == status.HTTP_200_OK:
            result = response.get_json()
        else:
            result = None
        return result

    ############################################################
    #  T E S T   C A S E S
    ############################################################
    def test_index(self):
        """It should return the index page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['message'], 'OK')

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

    def test_create_product_with_no_name(self):
        """It should not Create a Product without a name"""
        product = self._create_products()[0]
        new_product = product.serialize()
        del new_product["name"]
        logging.debug("Product no name: %s", new_product)
        response = self.client.post(BASE_URL, json=new_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no Content-Type"""
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with wrong Content-Type"""
        response = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_product(self):
        """It should read Product"""
        test_product = self._create_products()[0]
        request_url = f"{BASE_URL}/{test_product.id}"
        # logging.debug("Querying: %s", request_url)
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        got_product = response.get_json()
        logging.debug("Product got: %s", got_product)
        self.assertEqual(got_product["name"], test_product.name)
        self.assertEqual(got_product["description"], test_product.description)
        self.assertEqual(Decimal(got_product["price"]), test_product.price)
        self.assertEqual(got_product["available"], test_product.available)
        self.assertEqual(got_product["category"], test_product.category.name)

    def test_get_product_not_found(self):
        """It should handle an attempt to get an unknown id"""
        test_product = self._create_products()[0]
        request_url = f"{BASE_URL}/{test_product.id + 1}"
        logging.debug("Querying: %s", request_url)
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        got_product = response.get_json()
        logging.debug("Product got: %s", got_product)
        self.assertEqual(got_product, {})

    def test_update_product(self):
        """It should update a Product"""
        test_product = self._create_products()[0]
        request_url = f"{BASE_URL}/{test_product.id}"
        logging.debug("Updating: %s", test_product.id)
        updated_product = test_product.serialize()
        new_description = "Updated description"
        updated_product["description"] = new_description
        logging.debug("Querying: %s", request_url)
        response = self.client.put(request_url, json=updated_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        got_product = self._get_product(test_product.id)
        logging.debug("Product got: %s", got_product)
        self.assertEqual(got_product["name"], test_product.name)
        self.assertEqual(got_product["description"], new_description)
        self.assertEqual(Decimal(got_product["price"]), test_product.price)
        self.assertEqual(got_product["available"], test_product.available)
        self.assertEqual(got_product["category"], test_product.category.name)

    def test_update_product_with_invalid_data(self):
        """It should not update a Product with invalid data"""
        test_product = self._create_products()[0]
        request_url = f"{BASE_URL}/{test_product.id}"
        logging.debug("Updating: %s", test_product.id)
        updated_product = test_product.serialize()
        updated_product["available"] = "Not a boolean"
        logging.debug("Querying: %s", request_url)
        response = self.client.put(request_url, json=updated_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_not_found(self):
        """It should not update a Product with an unknown id"""
        test_product = self._create_products()[0]
        unknown_product_id = test_product.id + 1
        request_url = f"{BASE_URL}/{unknown_product_id}"
        logging.debug("Updating: %s", unknown_product_id)
        updated_product = test_product.serialize()
        updated_product["id"] = unknown_product_id
        logging.debug("Querying: %s", request_url)
        response = self.client.put(request_url, json=updated_product)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product(self):
        """It should delete a Product"""
        test_product = self._create_products()[0]
        request_url = f"{BASE_URL}/{test_product.id}"
        # logging.debug("Querying: %s", request_url)
        # Verify that the product exists
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        got_product = response.get_json()
        logging.debug("Product got: %s", got_product)
        response = self.client.delete(request_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify that the product does not exist
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_not_found(self):
        """It should not delete a Product that cannot be found"""
        test_product = self._create_products()[0]
        unknown_product_id = test_product.id + 1
        request_url = f"{BASE_URL}/{unknown_product_id}"
        response = self.client.delete(request_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_all(self):
        """It should list all products"""
        test_products = self._create_products(5)
        self.assertEqual(len(test_products), 5)
        request_url = BASE_URL
        logging.debug("Listing products")
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), len(test_products))
        for got_product in got_products:
            test_product = None
            for t_p in test_products:
                if t_p.id == got_product["id"]:
                    test_product = t_p
            self.assertIsNotNone(test_product)
            self.assertEqual(got_product["name"], test_product.name)
            self.assertEqual(got_product["description"], test_product.description)
            self.assertEqual(Decimal(got_product["price"]), test_product.price)
            self.assertEqual(got_product["available"], test_product.available)
            self.assertEqual(got_product["category"], test_product.category.name)

    def test_find_by_name(self):
        """It should find all products with this name"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_name = test_products[0].name
        request_url = f"{BASE_URL}?name={quote_plus(search_name)}"
        logging.debug("Finding products by name")
        num_expected = 0
        for product in test_products:
            if product.name == search_name:
                num_expected += 1
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), num_expected)
        for got_product in got_products:
            self.assertEqual(got_product["name"], search_name)

    def test_find_by_category(self):
        """It should find all products with this category"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_category = test_products[0].category
        request_url = f"{BASE_URL}?category={quote_plus(search_category.name)}"
        logging.debug("Finding products by category: %s", search_category.name)
        num_expected = 0
        for product in test_products:
            if product.category == search_category:
                num_expected += 1
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), num_expected)
        for got_product in got_products:
            self.assertEqual(got_product["category"], search_category.name)

    def test_find_by_invalid_category(self):
        """It should fail to find any products if the category is invalid"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_category_name = "never heard of it"
        request_url = f"{BASE_URL}?category={quote_plus(search_category_name)}"
        logging.debug("Finding products by invalid category: %s", search_category_name)
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_find_by_availability_true(self):
        """It should find all products with availability true"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_available = True
        request_url = f"{BASE_URL}?available={quote_plus(str(search_available))}"
        logging.debug("Finding products by availability")
        num_expected = 0
        for product in test_products:
            if product.available == search_available:
                num_expected += 1
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), num_expected)
        for got_product in got_products:
            self.assertEqual(got_product["available"], search_available)

    def test_find_by_availability_yes(self):
        """It should find all products with availability YES"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_available = True
        request_url = f"{BASE_URL}?available=yes"
        logging.debug("Finding products by availability")
        num_expected = 0
        for product in test_products:
            if product.available == search_available:
                num_expected += 1
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), num_expected)
        for got_product in got_products:
            self.assertEqual(got_product["available"], search_available)

    def test_find_by_availability_one(self):
        """It should find all products with availability 1"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_available = True
        request_url = f"{BASE_URL}?available=1"
        logging.debug("Finding products by availability")
        num_expected = 0
        for product in test_products:
            if product.available == search_available:
                num_expected += 1
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), num_expected)
        for got_product in got_products:
            self.assertEqual(got_product["available"], search_available)

    def test_find_by_availability_set(self):
        """It should find all products with availability set"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_available = True
        request_url = f"{BASE_URL}?available"
        logging.debug("Finding products by availability")
        num_expected = 0
        for product in test_products:
            if product.available == search_available:
                num_expected += 1
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), num_expected)
        for got_product in got_products:
            self.assertEqual(got_product["available"], search_available)

    def test_find_by_availability_false(self):
        """It should find all products with availability false"""
        test_products = self._create_products(10)
        self.assertEqual(len(test_products), 10)
        search_available = False
        request_url = f"{BASE_URL}?available={quote_plus(str(search_available))}"
        logging.debug("Finding products by availability")
        num_expected = 0
        for product in test_products:
            if product.available == search_available:
                num_expected += 1
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        got_products = response.get_json()
        self.assertEqual(len(got_products), num_expected)
        for got_product in got_products:
            self.assertEqual(got_product["available"], search_available)

    ######################################################################
    # Utility functions
    ######################################################################
    def get_product_count(self):
        """get the current number of products"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # logging.debug("data = %s", data)
        return len(data)
