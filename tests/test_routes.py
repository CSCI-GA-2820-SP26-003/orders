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
from service.models import db, Order
from tests.factories import OrderFactory
from tests.factories import ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
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
                BASE_URL, json=order.serialize(),
                content_type="application/json"
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
        resp = self.client.post(
            BASE_URL, json={}, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_no_content_type(self):
        """It should not Create an Order with no content type"""
        resp = self.client.post(BASE_URL)
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order_missing_customer_id(self):
        """It should not Create an Order without a customer_id"""
        order = OrderFactory()
        new_order = order.serialize()
        del new_order["customer_id"]
        resp = self.client.post(
            BASE_URL, json=new_order, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # We will need to uncomment when customer validation is implemented
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
        resp = self.client.get(
            f"{BASE_URL}/0", content_type="application/json")
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
        resp = self.client.get(f"{BASE_URL}/0/items/1",
                               content_type="application/json")
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

    def test_delete_order(self):
        """It should Delete an Order"""
        # get the id of an order
        order = self._create_orders(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.client.get(f"{BASE_URL}/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  L I S T   O R D E R   I T E M S   T E S T   C A S E S
    ######################################################################

    def test_list_order_items(self):
        """It should GET all Items from an Order"""
        order = OrderFactory()
        items = [ItemFactory() for _ in range(3)]
        order_data = order.serialize()
        order_data["items"] = [item.serialize() for item in items]
        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.get_json()["id"]

        resp = self.client.get(
            f"{BASE_URL}/{order_id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_list_order_items_empty(self):
        """It should return an empty list for an Order with no Items"""
        order = OrderFactory()
        order_data = order.serialize()
        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.get_json()["id"]

        resp = self.client.get(
            f"{BASE_URL}/{order_id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_list_order_items_order_not_found(self):
        """It should not list Items for a non-existing Order"""
        resp = self.client.get(f"{BASE_URL}/0/items",
                               content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_all_orders(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        resp = self.client.get(f"{BASE_URL}",
                               content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_list_order_items_invalid_order_id(self):
        """It should return 400 for an invalid order_id"""
        resp = self.client.get(f"{BASE_URL}/abc/items",
                               content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_order_items_contains_correct_data(self):
        """It should return Items with correct fields"""
        order = OrderFactory()
        item = ItemFactory()
        order_data = order.serialize()
        order_data["items"] = [item.serialize()]
        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.get_json()["id"]

        resp = self.client.get(
            f"{BASE_URL}/{order_id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("quantity", data[0])
        self.assertIn("unit_price", data[0])
        self.assertIn("order_id", data[0])
        self.assertEqual(data[0]["order_id"], order_id)

    def test_list_order_items_only_returns_items_for_that_order(self):
        """It should only return Items belonging to the specified Order"""
        # Create two orders each with one item
        order1 = OrderFactory()
        item1 = ItemFactory()
        order1_data = order1.serialize()
        order1_data["items"] = [item1.serialize()]
        resp = self.client.post(
            BASE_URL, json=order1_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order1_id = resp.get_json()["id"]

        order2 = OrderFactory()
        item2 = ItemFactory()
        order2_data = order2.serialize()
        order2_data["items"] = [item2.serialize()]
        resp = self.client.post(
            BASE_URL, json=order2_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # List items for order1 only
        resp = self.client.get(
            f"{BASE_URL}/{order1_id}/items",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        for item in data:
            self.assertEqual(item["order_id"], order1_id)

    ######################################################################
    #  A D D   O R D E R   I T E M   T E S T   C A S E S
    ######################################################################

    def test_add_order_item(self):
        """It should ADD an Item to an Order"""
        order = OrderFactory()
        order_data = order.serialize()
        order_data["items"] = []

        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()
        order_id = new_order["id"]

        item = ItemFactory()
        item_data = item.serialize()

        item_data["name"] = "xxx"
        item_data["quantity"] = 2
        item_data["unit_price"] = 0

        # POST /orders/{order_id}/items
        resp = self.client.post(
            f"{BASE_URL}/{order_id}/items",
            json={"name": item_data["name"],
                  "quantity": item_data["quantity"]},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()

        self.assertIn("name", data)
        self.assertEqual(data["order_id"], order_id)
        self.assertEqual(data["name"], item_data["name"])
        self.assertEqual(data["quantity"], item_data["quantity"])

    def test_add_order_item_existing_product_updates_quantity(self):
        """It should UPDATE quantity when adding the same name again"""
        order = OrderFactory()
        item = ItemFactory()
        order_data = order.serialize()

        name = "widget-2002"
        first_qty = 2
        item_data = item.serialize()
        item_data["name"] = name
        item_data["quantity"] = first_qty

        order_data["items"] = [item_data]
        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()
        order_id = new_order["id"]

        add_qty = 3
        resp = self.client.post(
            f"{BASE_URL}/{order_id}/items",
            json={"name": name, "quantity": add_qty},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        updated = resp.get_json()

        self.assertEqual(updated["order_id"], order_id)
        self.assertEqual(updated["name"], name)
        self.assertEqual(updated["quantity"], first_qty + add_qty)

        resp = self.client.get(
            f"{BASE_URL}/{order_id}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order_json = resp.get_json()
        same_product_items = [
            it for it in order_json.get("items", []) if it.get("name") == name
        ]
        self.assertEqual(len(same_product_items), 1)

    def test_add_order_item_order_not_found(self):
        """It should not ADD an Item to a non-existing Order"""
        resp = self.client.post(
            f"{BASE_URL}/0/items",
            json={"name": "poultry", "quantity": 2},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_order_item_missing_name(self):
        """It should return 400 for missing name"""
        order = self._create_orders(1)[0]
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json={"quantity": 2},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_order_item_invalid_quantity(self):
        """It should return 400 for invalid quantity"""
        order = self._create_orders(1)[0]

        # quantity <= 0
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json={"name": "poultry", "quantity": 0},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # quantity not an integer
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json={"name": "poultry", "quantity": "abc"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_order_item_invalid_order_id(self):
        """It should return 400 for an invalid order_id"""
        resp = self.client.post(
            f"{BASE_URL}/abc/items",
            json={"name": "poultry", "quantity": 2},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

######################################################################
    #  U P D A T E   O R D E R   I T E M   T E S T   C A S E S
######################################################################

    def test_update_item(self):
        """It should Update an item on an order"""
        # create a known item
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["name"], "XXXX")

    def test_update_item_not_found(self):
        """It should return 404 when updating a non-existent item"""
        # Create a known order
        order = self._create_orders(1)[0]

        # Create update data
        item = ItemFactory()

        # Attempt to update an item that doesn't exist
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/items/99999",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_order_not_found(self):
        """It should return 404 when updating items in a non-existent order"""

        # Create update data
        item = ItemFactory()

        # Attempt to update an item that doesn't exist
        resp = self.client.put(
            f"{BASE_URL}/99999/items/99999",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  D E L E T E   O R D E R   I T E M   T E S T   C A S E S
    ######################################################################

    def test_delete_order_item(self):
        """It should DELETE an Item from an Order"""

        order = OrderFactory()
        item = ItemFactory()

        order_data = order.serialize()
        item_data = item.serialize()

        order_data["items"] = [item_data]

        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()
        order_id = new_order["id"]

        # Grab item_id from created order response
        self.assertIn("items", new_order)
        self.assertGreaterEqual(len(new_order["items"]), 1)
        item_id = new_order["items"][0]["id"]

        # DELETE /orders/{order_id}/items/{item_id}
        resp = self.client.delete(
            f"{BASE_URL}/{order_id}/items/{item_id}",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Verify item removed: GET order and ensure item_id not in items
        resp = self.client.get(
            f"{BASE_URL}/{order_id}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order_json = resp.get_json()
        remaining_ids = [it.get("id") for it in order_json.get("items", [])]
        self.assertNotIn(item_id, remaining_ids)

    def test_delete_order_item_invalid_order_id(self):
        """It should return 400 for an invalid order_id"""

        resp = self.client.delete(
            f"{BASE_URL}/abc/items/1",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.delete(
            f"{BASE_URL}/0/items/1",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_order_item_invalid_item_id(self):
        """It should return 400 for an invalid item_id"""
        order = self._create_orders(1)[0]

        resp = self.client.delete(
            f"{BASE_URL}/{order.id}/items/abc",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.delete(
            f"{BASE_URL}/{order.id}/items/0",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_order_item_order_not_found(self):
        """It should return 404 when deleting an Item
        from a non-existing Order"""
        resp = self.client.delete(
            f"{BASE_URL}/999999/items/1",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_item_not_found_in_order(self):
        """It should return 404 when the Item does not exist
        within the specified Order"""
        # Create an order with one item
        order = OrderFactory()
        item = ItemFactory()

        order_data = order.serialize()
        item_data = item.serialize()
        order_data["items"] = [item_data]

        resp = self.client.post(
            BASE_URL, json=order_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()
        order_id = new_order["id"]

        resp = self.client.delete(
            f"{BASE_URL}/{order_id}/items/999999",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_item_exists_but_in_other_order(self):
        """It should return 404 when the Item exists but not in this Order"""
        # Create order A with item
        order_a = OrderFactory()
        item = ItemFactory()
        order_a_data = order_a.serialize()
        item_data = item.serialize()
        order_a_data["items"] = [item_data]

        resp = self.client.post(
            BASE_URL, json=order_a_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_a_json = resp.get_json()
        item_id = order_a_json["items"][0]["id"]

        # Create order B (empty)
        order_b = OrderFactory()
        order_b_data = order_b.serialize()
        order_b_data["items"] = []
        resp = self.client.post(
            BASE_URL, json=order_b_data, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_b_id = resp.get_json()["id"]

        # Try deleting item from order B -> should be 404
        resp = self.client.delete(
            f"{BASE_URL}/{order_b_id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
