######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
Order Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Order
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields
from service.models import Order, Item, OrderStatus
from service.common import status  # HTTP Status Codes


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Order Demo REST API Service",
    description="This is a sample server Orders store server.",
    default="orders",
    default_label="Order operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/api/orders", methods=["POST"])
def create_orders():
    """
    Creates an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to create an Order")
    check_content_type("application/json")

    # We will need to check if customer exists before creating the order
    # customer = Customer.find(customer_id)
    # if not customer:
    #     abort(status.HTTP_404_NOT_FOUND, f"Customer with id '{customer_id}' was not found.")

    # Create the order
    order = Order()
    order.deserialize(request.get_json())
    order.create()

    # Create a message to return
    message = order.serialize()

    location_url = url_for("get_order", order_id=order.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# LIST ALL ORDERS / QUERY ORDERS BY CUSTOMER ID
######################################################################


@app.route("/api/orders", methods=["GET"])
def list_orders():
    """
    Retrieve a list of Orders
    This endpoint will return all Orders unless a query string parameter
    is provided to filter results. Supported query parameters:
      - customer_id: filters orders belonging to a specific customer
      - status: filters orders by lifecycle state

    If no query string is provided, all orders are returned.
    If no orders match the filter, an empty list is returned with 200 OK.
    """
    app.logger.info("Request to list all Orders")

    customer_id = request.args.get("customer_id")
    status_param = request.args.get("status")

    query = Order.query

    if customer_id:
        query = query.filter(Order.customer_id == customer_id)

    if status_param:
        normalized_status = status_param.strip().upper()

        # Support issue wording "cancelled" while model uses "CANCELED"
        if normalized_status == "CANCELLED":
            normalized_status = "CANCELED"

        try:
            order_status = OrderStatus(normalized_status)
        except ValueError:
            return jsonify([]), status.HTTP_200_OK

        query = query.filter(Order.status == order_status)

    orders = query.all()
    results = [order.serialize() for order in orders]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ AN ORDER
######################################################################


@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Retrieve a single Order
    This endpoint will return an Order based on its id
    """
    app.logger.info("Request to retrieve an Order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ORDER
######################################################################
@app.route("/api/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order

    This endpoint will delete an Order based the id specified in the path
    """
    app.logger.info("Request to delete order with id: %s", order_id)

    # Retrieve the order to delete and delete it if it exists
    order = Order.find(order_id)
    if order:
        order.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  S W A G G E R   D A T A   M O D E L S   F O R   I T E M S
######################################################################

# Request body for adding / updating an Item
create_item_model = api.model(
    "ItemCreate",
    {
        "name": fields.String(required=True, description="The name of the Item"),
        "quantity": fields.Integer(
            required=True, description="Quantity of the Item (must be > 0)"
        ),
        "unit_price": fields.Float(
            required=False, description="Unit price of the Item (must be >= 0)"
        ),
        "order_id": fields.Integer(
            required=False,
            description="The Order id this Item belongs to "
            "(set from URL when creating)",
        ),
    },
)

# Full Item including the server-assigned id
item_model = api.inherit(
    "Item",
    create_item_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique id assigned internally by service",
        ),
    },
)


######################################################################
#  PATH: /api/orders/<order_id>/items
######################################################################
@api.route("/orders/<order_id>/items", strict_slashes=False)
@api.param("order_id", "The Order identifier")
class ItemCollection(Resource):
    """Handles interactions with the Items collection of an Order"""

    # ------------------------------------------------------------------
    # LIST ALL ITEMS IN AN ORDER
    # ------------------------------------------------------------------
    @api.doc("list_order_items")
    @api.response(200, "List of Items returned")
    @api.response(400, "Invalid order_id")
    @api.response(404, "Order not found")
    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """List all Items in an Order"""
        app.logger.info("Request to list Items for Order %s", order_id)
        try:
            order_id = int(order_id)
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Invalid ID: order_id must be an integer.",
            )

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        return [item.serialize() for item in order.items], status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD AN ITEM TO AN ORDER
    # ------------------------------------------------------------------
    @api.doc("add_order_item")
    @api.response(201, "Item created or quantity updated")
    @api.response(400, "Invalid item data")
    @api.response(404, "Order not found")
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """
        Add an Item to an Order
        If an Item with the same name already exists in the Order, increment its quantity.
        """
        app.logger.info("Request to add Item to Order %s", order_id)
        check_content_type("application/json")

        try:
            order_id = int(order_id)
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Invalid ID: order_id must be an integer.",
            )

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        data = request.get_json(silent=True)
        name = data.get("name") if data else None
        quantity = data.get("quantity") if data else None
        unit_price = data.get("unit_price") if data else None
        validate_item(data, name, quantity, unit_price)
        name = name.strip()
        quantity = int(quantity)

        existing = None
        for it in order.items:
            if getattr(it, "name", None) == name:
                existing = it
                break

        if existing:
            existing.quantity += quantity
            existing.update()
            return existing.serialize(), status.HTTP_201_CREATED

        item = Item()
        item.order_id = order.id
        item.name = name
        item.quantity = quantity
        item.unit_price = unit_price
        item.create()
        return item.serialize(), status.HTTP_201_CREATED


######################################################################
#  PATH: /api/orders/<order_id>/items/<item_id>
######################################################################
@api.route("/orders/<order_id>/items/<item_id>")
@api.param("order_id", "The Order identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """Handles interactions with a single Item in an Order"""

    # ------------------------------------------------------------------
    # READ AN ITEM FROM AN ORDER
    # ------------------------------------------------------------------
    @api.doc("get_order_item")
    @api.response(200, "Item returned")
    @api.response(400, "Invalid order_id or item_id")
    @api.response(404, "Order or Item not found")
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """Retrieve a single Item from an Order"""
        app.logger.info("Request to retrieve Item %s from Order %s", item_id, order_id)
        try:
            order_id = int(order_id)
            item_id = int(item_id)
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Invalid ID: order_id and item_id must be integers.",
            )

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        item = Item.find(item_id)
        if not item or item.order_id != order.id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in Order '{order_id}'.",
            )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("update_order_item")
    @api.response(200, "Item updated")
    @api.response(400, "Invalid order_id or item_id")
    @api.response(404, "Order or Item not found")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """Update an Item in an Order"""
        app.logger.info("Updating Item %s for Order %s", item_id, order_id)
        check_content_type("application/json")

        try:
            order_id = int(order_id)
            item_id = int(item_id)
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Invalid ID: order_id and item_id must be integers.",
            )

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        item = Item.find(item_id)
        if not item or item.order_id != order_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
            )

        item.deserialize(request.get_json())
        item.id = item_id
        item.order_id = order_id
        item.update()

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM FROM AN ORDER
    # ------------------------------------------------------------------
    @api.doc("delete_order_item")
    @api.response(204, "Item deleted")
    @api.response(400, "Invalid order_id or item_id")
    @api.response(404, "Order or Item not found")
    def delete(self, order_id, item_id):
        """Delete an Item from an Order"""
        app.logger.info("Request to delete Item %s from Order %s", item_id, order_id)

        try:
            order_id = int(order_id)
            item_id = int(item_id)
            if order_id <= 0 or item_id <= 0:
                raise ValueError
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Invalid ID: item_id, order_id must be positive integer.",
            )

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        item = Item.find(item_id)
        if not item or item.order_id != order_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' in Order '{order_id}' could not be found.",
            )

        item.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
# ADD AN ITEM TO AN ORDER
######################################################################


def validate_item(data, name, quantity, unit_price):
    """Helper function to validate order data"""
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, "Request body must be JSON.")

    if "name" not in data or "quantity" not in data:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Missing required fields: name and quantity are required.",
        )

    if not isinstance(name, str) or not name.strip():
        abort(status.HTTP_400_BAD_REQUEST, "name must be a non-empty string.")

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        abort(status.HTTP_400_BAD_REQUEST, "quantity must be an integer.")

    if unit_price is not None:
        try:
            unit_price = float(unit_price)
        except (ValueError, TypeError):
            abort(status.HTTP_400_BAD_REQUEST, "unit_price must be a float")

    if quantity <= 0:
        abort(status.HTTP_400_BAD_REQUEST, "quantity must be a positive integer.")


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################


@app.route("/api/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order

    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Update from the json in the body of the request
    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


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
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )


######################################################################
# CANCEL AN ORDER
######################################################################
@app.route("/api/orders/<order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    """
    Cancel an Order
    This endpoint will cancel an Order by setting its status to CANCELED
    """
    app.logger.info("Request to cancel Order %s", order_id)
    try:
        order_id = int(order_id)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid ID: order_id must be an integer.")

    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    if order.status == OrderStatus.CANCELED:
        abort(
            status.HTTP_409_CONFLICT,
            f"Order with id '{order_id}' is already cancelled.",
        )

    order.status = OrderStatus.CANCELED
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


# Codecov baseline trigger
