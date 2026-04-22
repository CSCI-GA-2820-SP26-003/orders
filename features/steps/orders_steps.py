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
Order Steps

Steps file for orders.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60
ITEM_PREFIX = "item_"


######################################################################
#  B A C K G R O U N D   S E T U P   ( R E S T   A P I )
######################################################################


@given("the following orders")
def step_impl(context):
    """Seed orders via the REST API from a Gherkin table"""
    for row in context.table:
        res = requests.post(
            f"{context.base_url}/api/orders",
            json={"customer_id": row["customer_id"], "status": row["status"]},
        )
        assert res.status_code == HTTP_201_CREATED
        context.order_id = res.json()["id"]


@given("the order has the following items")
def step_impl(context):
    """Add items to the saved order via the REST API from a Gherkin table"""
    for row in context.table:
        res = requests.post(
            f"{context.base_url}/api/orders/{context.order_id}/items",
            json={
                "name": row["name"],
                "quantity": int(row["quantity"]),
                "unit_price": float(row["unit_price"]),
            },
        )
        assert res.status_code == HTTP_201_CREATED
        context.item_id = res.json()["id"]


######################################################################
#  D Y N A M I C   I D   S T E P S
######################################################################


@when('I set the "{field}" to the saved order id')
def step_impl(context, field):
    """Paste the runtime order ID into an order form field"""
    element_id = "order_" + field.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(str(context.order_id))


@when('I set the item "{field}" to the saved order id')
def step_impl(context, field):
    """Paste the runtime order ID into an item form field"""
    element_id = ITEM_PREFIX + field.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(str(context.order_id))


@when('I set the item "{field}" to the saved item id')
def step_impl(context, field):
    """Paste the runtime item ID into an item form field"""
    element_id = ITEM_PREFIX + field.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(str(context.item_id))


######################################################################
#  I T E M   F O R M   I N T E R A C T I O N S
######################################################################


@when('I set the item "{field}" to "{value}"')
def step_impl(context, field, value):
    """Type a value into an item form field"""
    element_id = ITEM_PREFIX + field.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(value)


@then('I should see "{value}" in the item "{field}" field')
def step_impl(context, value, field):
    """Assert that an item form field contains the expected value"""
    element_id = ITEM_PREFIX + field.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), value
        )
    )
    assert found


######################################################################
#  O R D E R   F O R M   H E L P E R S
######################################################################


@when('I clear the "{field}" field')
def step_impl(context, field):
    """Clear an order form field to simulate removing required data"""
    element_id = "order_" + field.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()


######################################################################
#  C A N C E L   O R D E R   S T E P S
######################################################################


@given("an order exists with a cancellable status")
def step_impl(context):
    """Create an order that can be cancelled"""
    res = requests.post(
        f"{context.base_url}/api/orders",
        json={"customer_id": 42, "status": "OPEN"},
    )
    assert res.status_code == HTTP_201_CREATED
    context.order_id = res.json()["id"]


@given("an order exists that has already been cancelled")
def step_impl(context):
    """Create an order and cancel it once for setup"""
    res = requests.post(
        f"{context.base_url}/api/orders",
        json={"customer_id": 42, "status": "OPEN"},
    )
    assert res.status_code == HTTP_201_CREATED
    context.order_id = res.json()["id"]

    cancel_res = requests.put(f"{context.base_url}/api/orders/{context.order_id}/cancel")
    assert cancel_res.status_code == HTTP_200_OK


@then('the order status should change to "{expected_status}"')
def step_impl(context, expected_status):
    """Verify the order status in the dropdown after cancellation"""
    status_element = context.driver.find_element(By.ID, "order_status")
    selected_status = status_element.get_attribute("value").lower()
    normalized_selected = selected_status.replace("canceled", "cancelled")
    normalized_expected = expected_status.lower().strip()
    assert normalized_selected == normalized_expected


@then("I should see an error message indicating the order cannot be cancelled again")
def step_impl(context):
    """Verify user-friendly message for duplicate cancel attempts"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), "already cancelled"
        )
    )
    assert found
