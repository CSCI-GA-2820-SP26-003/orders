$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_customer_id").val(res.customer_id);
        $("#order_status").val(res.status);
        $("#order_date_created").val(res.date_created);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_customer_id").val("");
        $("#order_status").val("OPEN");
        $("#order_date_created").val("");
    }

    // Updates the item form with data from the response
    function update_item_form_data(res) {
        $("#item_order_id").val(res.order_id);
        $("#item_id").val(res.id);
        $("#item_name").val(res.name);
        $("#item_quantity").val(res.quantity);
        $("#item_unit_price").val(res.unit_price);
    }

    // Clears all item form fields
    function clear_item_form_data() {
        $("#item_id").val("");
        $("#item_name").val("");
        $("#item_quantity").val("");
        $("#item_unit_price").val("");
    }

    // Updates the flash message area with toast styling
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);

        let bar = $("#toast_bar");
        bar.removeClass("t-ok t-err");

        let msg = message.toLowerCase();
        if (msg.includes("success") || msg.includes("deleted") ||
            msg.includes("created") || msg.includes("cancel")) {
            bar.addClass("t-ok");
        } else if (msg.includes("error") || msg.includes("not found") ||
            msg.includes("405") || msg.includes("409") ||
            msg.includes("415") || msg.includes("400") ||
            msg.includes("conflict")) {
            bar.addClass("t-err");
        }
    }

    // Updates the result count badge
    function update_result_count(count) {
        let label = count === 1 ? "1 result" : count + " results";
        $("#results_count").text(label);
    }

    // Returns the CSS class for a status badge
    function status_badge_class(s) {
        switch (s) {
            case "OPEN": return "badge badge-open";
            case "SHIPPED": return "badge badge-shipped";
            case "DELIVERED": return "badge badge-delivered";
            case "CANCELED": return "badge badge-canceled";
            default: return "badge";
        }
    }

    // Formats an ISO date string to a readable format
    function format_date(iso) {
        if (!iso) return "—";
        let d = new Date(iso);
        return d.toLocaleDateString("en-US", {
            year: "numeric", month: "short", day: "numeric"
        });
    }

    // Builds the HTML for an order's items sub-table
    function build_items_html(items) {
        if (!items || items.length === 0) {
            return '<p class="no-items">No items in this order</p>';
        }
        let html = '<table class="items-table">';
        html += '<thead><tr><th>Item ID</th><th>Name</th><th>Qty</th><th>Unit Price</th></tr></thead>';
        html += '<tbody>';
        for (let i = 0; i < items.length; i++) {
            let item = items[i];
            html += `<tr>`;
            html += `<td>${item.id}</td>`;
            html += `<td style="font-weight:600">${item.name}</td>`;
            html += `<td>${item.quantity}</td>`;
            html += `<td>$${item.unit_price.toFixed(2)}</td>`;
            html += `</tr>`;
        }
        html += '</tbody></table>';
        return html;
    }

    // ****************************************
    // Clear the order form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        clear_form_data()
        // Reset toast
        $("#toast_bar").removeClass("t-ok t-err");
        $("#flash_message").text("Ready");
    });

    // ****************************************
    // Clear the item form
    // ****************************************

    $("#clear-item-btn").click(function () {
        $("#item_order_id").val("");
        clear_item_form_data();
        // Reset toast
        $("#toast_bar").removeClass("t-ok t-err");
        $("#flash_message").text("Ready");
    });

    // ****************************************
    // TODO: Create an Order
    // #create-btn → POST /orders
    // ****************************************

    // ****************************************
    // TODO: Retrieve an Order
    // #retrieve-btn → GET /orders/${order_id}
    // ****************************************

    // ****************************************
    // TODO: Update an Order
    // #update-btn → PUT /orders/${order_id}
    // ****************************************

    // ****************************************
    // TODO: Delete an Order
    // #delete-btn → DELETE /orders/${order_id}
    // ****************************************

    // ****************************************
    // TODO: List / Query Orders
    // #search-btn → GET /orders?customer_id=X&status=Y
    // List = no filters, Query = with filters
    // Both handled in one click handler
    // Each order row should have a chevron + hidden detail row
    // that expands on click to show items via build_items_html()
    // See test_ui_mock.js for the reference implementation
    // ****************************************

    // ****************************************
    // TODO: Cancel an Order (Action)
    // #cancel-btn → PUT /orders/${order_id}/cancel
    // ****************************************

    // ****************************************
    // TODO: Add an Item to an Order
    // #add-item-btn → POST /orders/${order_id}/items
    // ****************************************

    // ****************************************
    // TODO: Retrieve an Item from an Order
    // #retrieve-item-btn → GET /orders/${order_id}/items/${item_id}
    // ****************************************

    // ****************************************
    // TODO: Update an Item in an Order
    // #update-item-btn → PUT /orders/${order_id}/items/${item_id}
    // ****************************************

    // ****************************************
    // TODO: Delete an Item from an Order
    // #delete-item-btn → DELETE /orders/${order_id}/items/${item_id}
    // ****************************************

    // ****************************************
    // TODO: List Items in an Order
    // #list-items-btn → GET /orders/${order_id}/items
    // ****************************************

})