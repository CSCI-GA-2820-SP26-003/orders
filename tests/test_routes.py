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
TestOrder API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order, Item
from tests.factories import OrderFactory
from tests.factories import ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            order = OrderFactory()
            resp = self.client.post(
                BASE_URL, json=order.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders

    ######################################################################
    #  C R E A T E   O R D E R   T E S T   C A S E S
    ######################################################################

    def test_create_order(self):
        """It should Create a new Order"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(
            new_order["customer_id"],
            order.customer_id,
            "Customer ID does not match",
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(
            new_order["customer_id"],
            order.customer_id,
            "Customer ID does not match",
        )

    def test_create_order_no_data(self):
        """It should not Create an Order with missing data"""
        resp = self.client.post(BASE_URL, json={}, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_no_content_type(self):
        """It should not Create an Order with no content type"""
        resp = self.client.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order_missing_customer_id(self):
        """It should not Create an Order without a customer_id"""
        order = OrderFactory()
        new_order = order.serialize()
        del new_order["customer_id"]
        resp = self.client.post(
            BASE_URL, json=new_order, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: Uncomment when customer validation is implemented
    # def test_create_order_customer_not_found(self):
    #     """It should not Create an Order if the customer does not exist"""
    #     order = OrderFactory()
    #     new_order = order.serialize()
    #     new_order["customer_id"] = 0
    #     resp = self.client.post(
    #         BASE_URL, json=new_order, content_type="application/json"
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  R E A D   O R D E R   T E S T   C A S E S
    ######################################################################

    def test_get_order(self):
        """It should GET a single Order by its id"""
        order = self._create_orders(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(
            new_order["customer_id"],
            order.customer_id,
            "Customer ID does not match",
        )

    def test_get_order_not_found(self):
        """It should not GET an Order that is not found"""
        resp = self.client.get(f"{BASE_URL}/0", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  R E A D   O R D E R   I T E M   T E S T   C A S E S
    ######################################################################

    def test_get_order_item(self):
        """It should GET an Item from an Order"""
        order = OrderFactory()
        item = ItemFactory()
        order_data = order.serialize()
        order_data["items"] = [item.serialize()]
        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()
        order_id = new_order["id"]
        item_id = new_order["items"][0]["id"]

        resp = self.client.get(
            f"{BASE_URL}/{order_id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["order_id"], order_id)

    def test_get_order_item_order_not_found(self):
        """It should not GET an Item from a non-existing Order"""
        resp = self.client.get(f"{BASE_URL}/0/items/1", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_item_not_found(self):
        """It should not GET a non-existing Item from an Order"""
        order = self._create_orders(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/0",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_item_invalid_order_id(self):
        """It should return 400 for an invalid order_id"""
        resp = self.client.get(
            f"{BASE_URL}/abc/items/1", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_item_invalid_item_id(self):
        """It should return 400 for an invalid item_id"""
        resp = self.client.get(
            f"{BASE_URL}/1/items/abc", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  U P D A T E   O R D E R   T E S T   C A S E S
    ######################################################################

    def test_update_order(self):
        """It should update an existing Order"""
        # create an Order to update
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the Order
        new_order = resp.get_json()
        new_order_id = new_order["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["id"], new_order_id)


    def test_update_order_not_found_returns_404(self):
        """PUT /orders/<id> should 404 when the order does not exist"""
        payload = {
            "customer_id": 1,
            "items": [],
        }
        resp = self.client.put(f"{BASE_URL}/999999", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
