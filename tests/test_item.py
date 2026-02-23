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
# pylint: disable=duplicate-code

"""
Test cases for Item Model
"""

import logging
import os
from unittest import TestCase
from wsgi import app
from service.models import Order, Item, db
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        A D D R E S S   M O D E L   T E S T   C A S E S
######################################################################
class TestItem(TestCase):
    """Item Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_order_item(self):
        """It should Create an order with an item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.items[0].name, item.name)

        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].name, item2.name)

    def test_delete_order_item(self):
        """It should Delete an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        item = order.items[0]
        item.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.items), 0)

    def test_serialize_an_item(self):
        """It should serialize an Item"""
        item = ItemFactory()
        serial_item = item.serialize()
        self.assertEqual(serial_item["id"], item.id)
        self.assertEqual(serial_item["name"], item.name)
        self.assertEqual(serial_item["quantity"], item.quantity)
        self.assertEqual(serial_item["unit_price"], item.unit_price)

    def test_deserialize_an_item(self):
        """It should deserialize an Item"""
        item = ItemFactory()
        item.create()
        new_item = Item()
        new_item.deserialize(item.serialize())
        self.assertEqual(new_item.name, item.name)
        self.assertEqual(new_item.quantity, item.quantity)
        self.assertEqual(new_item.unit_price, item.unit_price)
