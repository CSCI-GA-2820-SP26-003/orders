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
TestErrorHandlers Test Suite

Verifies that the service returns JSON error responses (not HTML) for all
HTTP error conditions, including those handled by Flask-RESTX, those raised
by custom exceptions (DataValidationError), and those raised by Flask itself
for unmatched routes and disallowed methods.
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order
from tests.factories import OrderFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestErrorHandlers(TestCase):
    """Error Handler Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
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
        db.session.query(Order).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _assert_json_error(self, resp, expected_status):
        """Helper: assert the response is a JSON error with expected status"""
        self.assertEqual(resp.status_code, expected_status)
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("application/json", resp.content_type)
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertIn("message", data)

    def _create_order(self):
        """Create a single Order via the API and return its id"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.get_json()["id"]

    ######################################################################
    #  E R R O R   H A N D L E R   T E S T   C A S E S
    ######################################################################

    def test_malformed_json_returns_400_json(self):
        """It should return 400 JSON when the request body is malformed JSON"""
        resp = self.client.post(
            BASE_URL,
            data="{not valid json",
            content_type="application/json",
        )
        self._assert_json_error(resp, status.HTTP_400_BAD_REQUEST)

    def test_missing_content_type_returns_415_json(self):
        """It should return 415 JSON when no Content-Type header is sent"""
        resp = self.client.post(BASE_URL, data="{}")
        self._assert_json_error(resp, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_wrong_content_type_returns_415_json(self):
        """It should return 415 JSON when Content-Type is not application/json"""
        resp = self.client.post(BASE_URL, data="{}", content_type="text/plain")
        self._assert_json_error(resp, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_not_found_resource_returns_404_json(self):
        """It should return 404 JSON when the requested resource does not exist"""
        resp = self.client.get(f"{BASE_URL}/999999", content_type="application/json")
        self._assert_json_error(resp, status.HTTP_404_NOT_FOUND)

    def test_unknown_route_returns_404_json(self):
        """It should return 404 JSON for an unknown route under the API"""
        resp = self.client.get("/api/this-route-does-not-exist")
        self._assert_json_error(resp, status.HTTP_404_NOT_FOUND)

    def test_data_validation_error_returns_400_json(self):
        """It should return 400 JSON when DataValidationError is raised"""
        # Missing customer_id triggers DataValidationError in Order.deserialize
        payload = {"items": []}
        resp = self.client.post(BASE_URL, json=payload, content_type="application/json")
        self._assert_json_error(resp, status.HTTP_400_BAD_REQUEST)

    def test_invalid_id_format_returns_400_json(self):
        """It should return 400 JSON when an ID path parameter is not an integer"""
        resp = self.client.get(f"{BASE_URL}/abc/items", content_type="application/json")
        self._assert_json_error(resp, status.HTTP_400_BAD_REQUEST)

    def test_invalid_item_data_returns_400_json(self):
        """It should return 400 JSON when item data fails validation"""
        order_id = self._create_order()
        resp = self.client.post(
            f"{BASE_URL}/{order_id}/items",
            json={"name": "", "quantity": 0},
            content_type="application/json",
        )
        self._assert_json_error(resp, status.HTTP_400_BAD_REQUEST)

    def test_empty_body_with_json_content_type_returns_400_json(self):
        """It should return 400 JSON when body is empty with JSON content type"""
        resp = self.client.post(BASE_URL, data="", content_type="application/json")
        self._assert_json_error(resp, status.HTTP_400_BAD_REQUEST)

    def test_method_not_allowed_returns_405_json(self):
        """It should return 405 JSON when an HTTP method is not allowed"""
        # /health is GET-only; POST should yield 405
        resp = self.client.post("/health")
        self._assert_json_error(resp, status.HTTP_405_METHOD_NOT_ALLOWED)
