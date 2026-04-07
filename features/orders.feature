Feature: The orders service back-end
    As an eCommerce Manager
    I need a RESTful orders service
    So that I can manage orders for my customers

    Background:
        Given the following orders
            | customer_id | status  |
            | 99          | OPEN    |
            | 42          | SHIPPED |
            | 42          | OPEN    |
        And the order has the following items
            | name     | quantity | unit_price |
            | Dog Food | 2        | 12.99      |

     Scenario: Create a new order and add an item
        When I visit the "Home Page"
        And I set the "Customer ID" to "1001"
        And I select "Open" in the "Status" dropdown
        And I press the "Create" button
        Then I should see the message "Success: Order created"
        And I should see a value in the "ID" field

        When I set the item "Order ID" to the saved order id
        And I set the item "Name" to "Laptop"
        And I set the item "Quantity" to "2"
        And I set the item "Unit Price" to "999.99"
        And I press the "Add Item" button
        Then I should see the message "Success: Item added"
        And I should see a value in the item "ID" field
        And I should see "Laptop" in the item "Name" field
        And I should see "2" in the item "Quantity" field

    Scenario: Attempt to create an order with missing data
        When I visit the "Home Page"
        And I set the "Customer ID" to ""
        And I select "Open" in the "Status" dropdown
        And I press the "Create" button
        Then I should see the message "Error"
        And the "ID" field should be empty

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

    Scenario: Cancel an existing order
        Given an order exists with a cancellable status
        When I visit the "Home Page"
        And I set the "ID" to the saved order id
        And I press the "Cancel" button
        Then I should see "Canceled" in the "Status" dropdown

    Scenario: Cancel an already cancelled order
        Given an order exists that has already been cancelled
        When I visit the "Home Page"
        And I set the "ID" to the saved order id
        And I press the "Cancel" button
        Then I should see the message "already cancelled"
        
    Scenario: Search orders by Customer ID
        When I visit the "Home Page"
        And I set the "Customer ID" to "42"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see customer id "42" in the results
        And I should not see customer id "99" in the results

    Scenario: Search with no matching results
        When I visit the "Home Page"
        And I set the "Customer ID" to "999"
        And I press the "Search" button
        Then I should see the message "Success: 0 order(s) found"
        And I should not see customer id "42" in the results
        And I should not see customer id "99" in the results

    Scenario: List all orders
        When I visit the "Home Page"
        And I clear the "Customer ID" field
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see customer id "42" in the results
        And I should see customer id "99" in the results

    Scenario: List orders when none exist
        Given there are no orders
        When I visit the "Home Page"
        And I clear the "Customer ID" field
        And I press the "Search" button
        Then I should see the message "Success: 0 order(s) found"
        And I should not see customer id "42" in the results
        And I should not see customer id "99" in the results