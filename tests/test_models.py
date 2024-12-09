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

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
import json
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################


class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a product from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        new_product = Product.find(product.id)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_update_a_product(self):
        """It should update a product in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        logger.info('Old product is: %s', json.dumps(product.serialize()))
        product.update()
        products = Product.all()
        new_product = Product.find(product.id)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_delete_a_product(self):
        """It should delete a product from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        ProductFactory.create_batch(5)
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """It should find a product by name in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        ProductFactory.create_batch(5)
        products = Product.all()
        self.assertEqual(len(products), 5)
        search_product = products[0]
        expected_num_products = 0
        for product in products:
            if product.name == search_product.name:
                expected_num_products += 1
        self.assertNotEqual(expected_num_products, 0)
        found_products = Product.find_by_name(search_product.name)
        self.assertEqual(found_products.count(), expected_num_products)
        for product in found_products:
            self.assertEqual(product.name, search_product.name)

    def test_find_product_by_availability(self):
        """It should find a product by availability in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        ProductFactory.create_batch(10)
        products = Product.all()
        self.assertEqual(len(products), 10)
        search_product = products[0]
        expected_num_products = 0
        for product in products:
            if product.available == search_product.available:
                expected_num_products += 1
        self.assertNotEqual(expected_num_products, 0)
        found_products = Product.find_by_availability(search_product.available)
        self.assertEqual(found_products.count(), expected_num_products)
        for product in found_products:
            self.assertEqual(product.available, search_product.available)

    def test_find_product_by_category(self):
        """It should find a product by category in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        ProductFactory.create_batch(10)
        products = Product.all()
        self.assertEqual(len(products), 10)
        search_product = products[0]
        expected_num_products = 0
        for product in products:
            if product.category == search_product.category:
                expected_num_products += 1
        self.assertNotEqual(expected_num_products, 0)
        found_products = Product.find_by_category(search_product.category)
        self.assertEqual(found_products.count(), expected_num_products)
        for product in found_products:
            self.assertEqual(product.category, search_product.category)

    def test_find_product_by_price(self):
        """It should find a product by price in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        ProductFactory.create_batch(10)
        products = Product.all()
        self.assertEqual(len(products), 10)
        search_product = products[0]
        expected_num_products = 0
        for product in products:
            if product.price == search_product.price:
                expected_num_products += 1
        self.assertNotEqual(expected_num_products, 0)
        found_products = Product.find_by_price(search_product.price)
        self.assertEqual(found_products.count(), expected_num_products)
        for product in found_products:
            self.assertEqual(product.price, search_product.price)

    def test_find_product_by_string_price(self):
        """It should find a product by a price string with trailing whitespace in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        ProductFactory.create_batch(10)
        products = Product.all()
        self.assertEqual(len(products), 10)
        search_product = products[0]
        expected_num_products = 0
        for product in products:
            if product.price == search_product.price:
                expected_num_products += 1
        self.assertNotEqual(expected_num_products, 0)
        found_products = Product.find_by_price(str(search_product.price) + " ")
        self.assertEqual(found_products.count(), expected_num_products)
        for product in found_products:
            self.assertEqual(product.price, search_product.price)

    def test_serialize_and_deserialize(self):
        """It should be possible to serialize and deserialize an object"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        original_product = products[0]
        self.assertIsNotNone(original_product.id)
        serialized_product = original_product.serialize()
        blank_product = Product()
        deserialized_product = blank_product.deserialize( serialized_product )
        self.assertEqual(original_product.id, deserialized_product.id)
        self.assertEqual(original_product.name, deserialized_product.name)
        self.assertEqual(original_product.description, deserialized_product.description)
        self.assertEqual(original_product.category, deserialized_product.category)
        self.assertEqual(original_product.price, deserialized_product.price)

    def test_update_with_no_id(self):
        """It should not be possible to update an object with no id to the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        product = products[0]
        self.assertIsNotNone(product.id)
        actual_err = None
        try:
            product.id = None
            product.update()
        except BaseException as err:
            actual_err = err
        self.assertIsNotNone(actual_err)
        self.assertTrue(isinstance(actual_err, DataValidationError))
        self.assertEqual(str(actual_err), "Update called with empty ID field")

    def test_deserialize_available_not_bool(self):
        """It should not be possible to deserialize a dictionary with a non-bool available"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        original_product = products[0]
        self.assertIsNotNone(original_product.available)
        serialized_product = original_product.serialize()
        serialized_product["available"] = "Not a bool"
        blank_product = Product()
        actual_err = None
        try:
            deserialized_product = blank_product.deserialize( serialized_product )
        except BaseException as err:
            actual_err = err
        self.assertIsNotNone(actual_err)
        self.assertTrue(isinstance(actual_err, DataValidationError))
        self.assertEqual(str(actual_err), "Invalid type for boolean [available]: <class 'str'>")

    def test_deserialize_category_not_valid(self):
        """It should not be possible to deserialize a dictionary with an invalid category"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        original_product = products[0]
        self.assertIsNotNone(original_product.category)
        serialized_product = original_product.serialize()
        serialized_product["category"] = "Not a category I have heard of"
        blank_product = Product()
        actual_err = None
        try:
            deserialized_product = blank_product.deserialize( serialized_product )
        except BaseException as err:
            actual_err = err
        self.assertIsNotNone(actual_err)
        self.assertTrue(isinstance(actual_err, DataValidationError))
        self.assertEqual(str(actual_err), "Invalid attribute: Not a category I have heard of")

    def test_deserialize_empty_dictionary(self):
        """It should not be possible to deserialize an empty dictionary"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        original_product = products[0]
        self.assertIsNotNone(original_product.category)
        serialized_product = {}
        blank_product = Product()
        actual_err = None
        try:
            deserialized_product = blank_product.deserialize( serialized_product )
        except BaseException as err:
            actual_err = err
        self.assertIsNotNone(actual_err)
        self.assertTrue(isinstance(actual_err, DataValidationError))
        self.assertEqual(str(actual_err), "Invalid product: missing id")

    def test_deserialize_invalid_dictionary(self):
        """It should not be possible to deserialize an invalid dictionary"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        original_product = products[0]
        self.assertIsNotNone(original_product.category)
        serialized_product = "Not a dictionary"
        blank_product = Product()
        actual_err = None
        try:
            deserialized_product = blank_product.deserialize( serialized_product )
        except BaseException as err:
            actual_err = err
        self.assertIsNotNone(actual_err)
        self.assertTrue(isinstance(actual_err, DataValidationError))
        self.assertEqual(str(actual_err), "Invalid product: body of request contained bad or no data string indices must be integers")
