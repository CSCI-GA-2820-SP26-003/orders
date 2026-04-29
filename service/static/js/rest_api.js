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
        $("#order_status").val("");
        $("#order_date_created").val("");
        $("#order_id").val("");
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
        if (msg.includes("error") || msg.includes("not found") ||
            msg.includes("405") || msg.includes("409") ||
            msg.includes("415") || msg.includes("400") ||
            msg.includes("conflict")) {
            bar.addClass("t-err");
        } else if (msg.includes("success") || msg.includes("deleted") ||
            msg.includes("created") || msg.includes("cancel")) {
            bar.addClass("t-ok");
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

    // Builds the HTML for the orders results table
    function build_order_table(orders) {
        let table = '<table><colgroup>';
        table += '<col class="col-chev"><col class="col-id"><col class="col-cust">';
        table += '<col class="col-status"><col class="col-items"><col class="col-date">';
        table += '</colgroup>';
        table += '<thead><tr>';
        table += '<th></th><th>ID</th><th>Customer</th>';
        table += '<th>Status</th><th>Items</th><th>Created</th>';
        table += '</tr></thead><tbody>';

        for (let i = 0; i < orders.length; i++) {
            let order = orders[i];
            let badgeClass = status_badge_class(order.status);
            let itemCount = order.items ? order.items.length : 0;

            table += `<tr class="order-row" data-index="${i}">`;
            table += `<td><span class="row-chevron"><svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg></span></td>`;
            table += `<td style="font-weight:600">${order.id}</td>`;
            table += `<td>${order.customer_id}</td>`;
            table += `<td><span class="${badgeClass}">${order.status}</span></td>`;
            table += `<td>${itemCount}</td>`;
            table += `<td>${format_date(order.date_created)}</td>`;
            table += `</tr>`;

            table += `<tr class="detail-row" data-index="${i}" style="display:none;">`;
            table += `<td colspan="6"><div class="detail-wrap"><div class="detail-inner">`;
            table += `<p class="items-label">Order Items</p>`;
            table += build_items_html(order.items);
            table += `</div></div></td></tr>`;
        }

        table += '</tbody></table>';
        return table;
    }

    // Builds the HTML for an order's items sub-table
    function build_items_html(items) {
        if (!items || items.length === 0) {
            return '<p class="no-items">No items in this order</p>';
        }
        let html = '<table class="items-table"><colgroup>';
        html += '<col style="width:20%"><col style="width:35%">';
        html += '<col style="width:15%"><col style="width:30%">';
        html += '</colgroup>';
        html += '<thead><tr><th>Item ID</th><th>Name</th><th>Qty</th><th>Unit Price</th></tr></thead>';
        html += '<tbody>';
        for (let i = 0; i < items.length; i++) {
            let item = items[i];
            let price = (item.unit_price != null) ? "$" + item.unit_price.toFixed(2) : "—";
            html += `<tr>`;
            html += `<td>${item.id}</td>`;
            html += `<td style="font-weight:600">${item.name}</td>`;
            html += `<td>${item.quantity}</td>`;
            html += `<td>${price}</td>`;
            html += `</tr>`;
        }
        html += '</tbody></table>';
        return html;
    }

    // ****************************************
    // Row toggle for expanding order items
    // (delegated so it survives table re-renders)
    // ****************************************
    $("#search_results").on("click", ".order-row", function () {
        let idx = $(this).data("index");
        $(this).toggleClass("expanded");
        let detailRow = $(`#search_results .detail-row[data-index='${idx}']`);
        if ($(this).hasClass("expanded")) {
            detailRow.show();
            detailRow.find(".detail-wrap").slideDown(200);
        } else {
            detailRow.find(".detail-wrap").slideUp(200, function () {
                detailRow.hide();
            });
        }
    });

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
    // Create an Order
    // #create-btn → POST /api/orders
    // ****************************************

    $("#create-btn").click(function () {
        let data = {
            "customer_id": parseInt($("#order_customer_id").val()),
            "status": $("#order_status").val() || "OPEN"
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/api/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res);
            $("#item_order_id").val(res.id);
            flash_message("Success: Order created (ID: " + res.id + ")");
        });

        ajax.fail(function (res) {
            if (res.responseJSON && res.responseJSON.message) {
                flash_message("Error: " + res.responseJSON.message);
            } else {
                flash_message("Error: Unable to create order");
            }
        });
    });

    // ****************************************
    // Retrieve an Order
    // #retrieve-btn → GET /api/orders/${order_id}
    // ****************************************
    $("#retrieve-btn").click(function () {
        let order_id = $("#order_id").val();

        if (!order_id) {
            flash_message("Error: Order ID is required for retrieve");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            update_form_data(res);

            // Show the retrieved order in the results area too
            $("#search_results").html(build_order_table([res]));
            update_result_count(1);

            $("#results_title").text("Order #" + res.id);
            document.querySelector('.res-card').scrollIntoView({ behavior: 'smooth' });
            flash_message("Success: Order retrieved");
        });

        ajax.fail(function (res) {
            clear_form_data();
            $("#order_id").val(order_id);

            let error_message = "Order not found";
            if (res.responseJSON && res.responseJSON.message) {
                error_message = res.responseJSON.message;
            }

            $("#search_results").html(`
                <div class="empty">
                    <div class="empty-icon">
                        <svg viewBox="0 0 24 24">
                            <circle cx="11" cy="11" r="8" />
                            <line x1="21" y1="21" x2="16.65" y2="16.65" />
                        </svg>
                    </div>
                    <p>Order not found</p>
                    <span>${error_message}</span>
                </div>
            `);
            update_result_count(0);
            flash_message("Error: " + error_message);
        });
    });



    // ****************************************
    // Update an Order
    // #update-btn → PUT /api/orders/${order_id}
    // ****************************************

    $("#update-btn").click(function () {
        let order_id = $("#order_id").val();
        if (!order_id) {
            flash_message("Error: Order ID is required for update");
            return;
        }

        let data = {
            "customer_id": parseInt($("#order_customer_id").val()),
            "status": $("#order_status").val() || "OPEN"
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/orders/${order_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res);
            flash_message("Success: Order updated");
        });

        ajax.fail(function (res) {
            flash_message("Error: " + res.responseJSON.message);
        });
    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {
        const order_id = $("#order_id").val();
        if (order_id) {
            $.ajax({
                url: `/api/orders/${order_id}`,
                type: 'DELETE',
                dataType: 'json',
                success: function (data) {
                    flash_message("Order successfully deleted!");
                    clear_form_data();
                },
                error: function (xhr, status, error) {
                    flash_message(`Error deleting order: ${error}`)
                }
            });
        }
        else {
            flash_message("Please provide an order id!");
        }
    })

    // ****************************************
    // List / Query Orders
    // #search-btn → GET /api/orders?customer_id=X
    // ****************************************

    $("#search-btn").click(function () {
        let customer_id = $("#order_customer_id").val();
        let status = $("#order_status").val();

        let params = [];
        if (customer_id) {
            params.push("customer_id=" + customer_id);
        }
        if (status) {
            params.push("status=" + status);
        }
        let queryString = params.join("&");

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders?${queryString}`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            $("#results_title").text("Orders");
            $("#search_results").html(build_order_table(res));
            update_result_count(res.length);
            flash_message("Success: " + res.length + " order(s) found");

            // // Bind row click to toggle detail
            // $("#search_results .order-row").click(function () {
            //     let idx = $(this).data("index");
            //     $(this).toggleClass("expanded");
            //     let detailRow = $(`#search_results .detail-row[data-index='${idx}']`);
            //     if ($(this).hasClass("expanded")) {
            //         detailRow.show();
            //         detailRow.find(".detail-wrap").slideDown(200);
            //     } else {
            //         detailRow.find(".detail-wrap").slideUp(200, function () {
            //             detailRow.hide();
            //         });
            //     }
            // });

            document.querySelector('.res-card').scrollIntoView({ behavior: 'smooth' });
        });

        ajax.fail(function (res) {
            let error_message = "Unable to search orders";
            if (res.responseJSON && res.responseJSON.message) {
                error_message = res.responseJSON.message;
            }
            flash_message("Error: " + error_message);
        });
    });

    // ****************************************
    // Cancel an Order (Action)
    // #cancel-btn → PUT /api/orders/${order_id}/cancel
    // ****************************************

    $("#cancel-btn").click(function () {
        let order_id = $("#order_id").val();
        if (!order_id) {
            flash_message("Error: Order ID is required for cancel");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/orders/${order_id}/cancel`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            update_form_data(res);
            flash_message("Success: Order cancelled");
        });

        ajax.fail(function (res) {
            let error_message = "Unable to cancel order";
            if (res.responseJSON && res.responseJSON.message) {
                error_message = res.responseJSON.message;
            }
            flash_message("Error: " + error_message);
        });
    });

    // ****************************************
    // Add an Item to an Order
    // #add-item-btn → POST /api/orders/${order_id}/items
    // ****************************************

    $("#add-item-btn").click(function () {
        let order_id = $("#item_order_id").val();
        if (!order_id) {
            flash_message("Error: Order ID is required to add an item");
            return;
        }

        let data = {
            "name": $("#item_name").val(),
            "quantity": parseInt($("#item_quantity").val()),
            "unit_price": parseFloat($("#item_unit_price").val())
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: `/api/orders/${order_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_item_form_data(res);
            flash_message("Success: Item added (ID: " + res.id + ")");
        });

        ajax.fail(function (res) {
            if (res.responseJSON && res.responseJSON.message) {
                flash_message("Error: " + res.responseJSON.message);
            } else {
                flash_message("Error: Unable to add item");
            }
        });
    });

    // ****************************************
    // Retrieve an Item from an Order
    // #retrieve-item-btn → GET /api/orders/${order_id}/items/${item_id}
    // ****************************************

    $("#retrieve-item-btn").click(function () {
        let order_id = $("#item_order_id").val();
        let item_id = $("#item_id").val();
        if (!order_id || !item_id) {
            flash_message("Error: Order ID and Item ID are required for retrieve");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            update_item_form_data(res);
            flash_message("Success: Item retrieved");
        });

        ajax.fail(function (res) {
            clear_item_form_data();
            let error_message = "Item not found";
            if (res.responseJSON && res.responseJSON.message) {
                error_message = res.responseJSON.message;
            }
            flash_message("Error: " + error_message);
        });
    });

    // ****************************************
    // Update an Item in an Order
    // #update-item-btn → PUT /api/orders/${order_id}/items/${item_id}
    // ****************************************

    $("#update-item-btn").click(function () {
        let order_id = $("#item_order_id").val();
        let item_id = $("#item_id").val();
        if (!order_id || !item_id) {
            flash_message("Error: Order ID and Item ID are required for update");
            return;
        }

        let data = {
            "name": $("#item_name").val(),
            "quantity": parseInt($("#item_quantity").val()),
            "unit_price": parseFloat($("#item_unit_price").val())
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_item_form_data(res);
            flash_message("Success: Item updated");
        });

        ajax.fail(function (res) {
            flash_message("Error: " + res.responseJSON.message);
        });
    });

    // ****************************************
    // Delete an Item from an Order
    // ****************************************

    $("#delete-item-btn").click(function () {
        const order_id = $("#item_order_id").val();
        const item_id = $("#item_id").val();
        if (order_id && item_id) {
            $.ajax({
                url: `/api/orders/${order_id}/items/${item_id}`,
                type: 'DELETE',
                dataType: 'json',
                success: function (data) {
                    flash_message("Item successfully deleted!");
                    clear_item_form_data();
                },
                error: function (xhr, status, error) {
                    flash_message(`Error deleting item: ${error}`);
                }
            });
        }
        else if (!order_id && !item_id) {
            flash_message("Please provide an order id and item id!");
        }
        else if (!order_id) {
            flash_message("Please provide an order id!");
        }
        else {
            flash_message("Please provide an item id!");
        }
    })

    // ****************************************
    // List Items in an Order
    // #list-items-btn → GET /api/orders/${order_id}/items
    // ****************************************

    $("#list-items-btn").click(function () {
        let order_id = $("#item_order_id").val();
        if (!order_id) {
            flash_message("Error: Order ID is required to list items");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}/items`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            let html = build_items_html(res);
            $("#search_results").html(
                '<div style="padding: 20px 24px;">' +
                html +
                '</div>'
            );
            update_result_count(res.length);
            $("#results_title").text("Items for Order #" + order_id);
            document.querySelector('.res-card').scrollIntoView({ behavior: 'smooth' });
            flash_message("Success: " + res.length + " item(s) found");
        });

        ajax.fail(function (res) {
            let error_message = "Unable to list items";
            if (res.responseJSON && res.responseJSON.message) {
                error_message = res.responseJSON.message;
            }
            flash_message("Error: " + error_message);
        });
    });

})
