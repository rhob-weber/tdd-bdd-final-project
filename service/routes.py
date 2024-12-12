######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product, Category, DataValidationError
from service.common import status  # HTTP Status Codes
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    #
    # Uncomment this line of code once you implement READ A PRODUCT
    #
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """
    List all Products
    This endpoint will get all Products
    """
    app.logger.info("Request to Get Products...")
    search_name = request.args.get("name")
    search_category = request.args.get("category")
    search_available = request.args.get("available")
    if search_name:
        products = Product.find_by_name(search_name)
    elif search_category:
        try:
            category_value = Category[search_category]
        except KeyError:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid category: {search_category}")
        products = Product.find_by_category(category_value)
    elif search_available or search_available == "":
        available_value = search_available.lower() in ["true", "yes", "1", ""]
        products = Product.find_by_availability(available_value)
    else:
        products = Product.all()

    results = [product.serialize() for product in products]

    return results, status.HTTP_200_OK


######################################################################
# R E A D   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Get a Product
    This endpoint will get a Product with the requested id
    """
    app.logger.info("Request to Get a Product...")

    app.logger.info("Processing: %s", product_id)
    product = Product.find(product_id)
    location_url = url_for("get_products", product_id=product_id, _external=True)
    if product is not None:
        status_code = status.HTTP_200_OK
        message = product.serialize()
    else:
        status_code = status.HTTP_404_NOT_FOUND
        message = {}

    return jsonify(message), status_code, {"Location": location_url}


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product
    This endpoint will update the Product with the requested id
    """
    app.logger.info("Request to Update a Product...")
    app.logger.info("Processing: %s", product_id)

    check_content_type("application/json")
    data = request.get_json()
    app.logger.info("Processing PUT: %s", data)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    try:
        product.deserialize(data)
    except DataValidationError as err:
        abort(status.HTTP_400_BAD_REQUEST, str(err))

    product.id = product_id
    product.update()
    status_code = status.HTTP_200_OK
    message = product.serialize()

    location_url = url_for("update_products", product_id=product_id, _external=True)

    return jsonify(message), status_code, {"Location": location_url}


######################################################################
# D E L E T E   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """
    Delete a Product
    This endpoint will delete the Product with the requested id
    """
    app.logger.info("Request to Delete a Product...")
    app.logger.info("Processing: DELETE %s", product_id)

    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    product.delete()
    status_code = status.HTTP_204_NO_CONTENT

    location_url = url_for("delete_products", product_id=product_id, _external=True)

    return "", status_code, {"Location": location_url}
