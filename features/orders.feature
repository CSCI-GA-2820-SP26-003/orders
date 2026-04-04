Feature: Update an Order via the Web UI
    As an eCommerce Manager
    I need to update existing orders and items through the web interface
    So that I can correct or modify order and item information

    Background:
        Given the following orders
            | customer_id | status |
            | 42          | OPEN   |
        And the order has the following items
            | name     | quantity | unit_price |
            | Dog Food | 2        | 12.99      |

    Scenario: Update an existing order
        When I visit the "Home Page"
        And I set the "ID" to the saved order id
        And I set the "Customer ID" to "99"
        And I select "Shipped" in the "Status" dropdown
        And I press the "Update" button
        Then I should see the message "Success: Order updated"
        And I should see "99" in the "Customer ID" field
        And I should see "Shipped" in the "Status" dropdown

    Scenario: Update an item in an order
        When I visit the "Home Page"
        And I set the item "Order ID" to the saved order id
        And I set the item "ID" to the saved item id
        And I set the item "Name" to "Premium Dog Food"
        And I set the item "Quantity" to "5"
        And I set the item "Unit Price" to "15.99"
        And I press the "Update Item" button
        Then I should see the message "Success: Item updated"
        And I should see "Premium Dog Food" in the item "Name" field
        And I should see "5" in the item "Quantity" field

    Scenario: Update an order with invalid data
        When I visit the "Home Page"
        And I set the "ID" to the saved order id
        And I clear the "Customer ID" field
        And I press the "Update" button
        Then I should see the message "Error"

    Scenario: Delete an order
        When I visit the "Home Page"
        And I set the "ID" to the saved order id
        And I press the "Delete" button
        Then I should see the message "Order successfully deleted!"
    
    Scenario: Delete an existing item
        When I visit the "Home Page"
        And I set the item "Order ID" to the saved order id
        And I set the item "ID" to the saved item id
        And I press the "Delete Item" button
        Then I should see the message "Item successfully deleted!"

    Scenario: Delete a nonexistent item
        When I visit the "Home Page"
        And I set the item "Order ID" to the saved order id
        And I set the item "ID" to "99999"
        And I press the "Delete Item" button
        Then I should see the message "Error"
