# lab-github-actions

[![Build Status](https://github.com/CSCI-GA-2820-SP26-003/orders/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP26-003/orders/actions)

[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP26-003/orders/graph/badge.svg?token=1QJGFVMZA4)](https://codecov.io/gh/CSCI-GA-2820-SP26-003/orders)

# NYU Devops Orders Microservice

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This project implements an `orders` microservice that exposes several different operations and endpoints
for use within an ecommerce platform. 

## Overview

The Orders Service is a RESTful microservice for managing orders and their line items. It is built with Flask, SQLAlchemy, and PostgreSQL.

## API Endpoints

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create a new order |
| GET | `/orders` | List all orders |
| GET | `/orders/{order_id}` | Retrieve a single order |
| PUT | `/orders/{order_id}` | Update an existing order |
| DELETE | `/orders/{order_id}` | Delete an order |

### Order Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/orders/{order_id}/cancel` | Cancel an order (sets status to CANCELED) |

### Order Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders/{order_id}/items` | Add an item to an order |
| GET | `/orders/{order_id}/items` | List all items in an order |
| GET | `/orders/{order_id}/items/{item_id}` | Retrieve a specific item |
| PUT | `/orders/{order_id}/items/{item_id}` | Update an item |
| DELETE | `/orders/{order_id}/items/{item_id}` | Delete an item |

### Query Parameters

| Endpoint | Parameter | Description |
|----------|-----------|-------------|
| GET `/orders` | `customer_id` | Filter orders by customer ID |

### Cancel Order Example
```bash
# Cancel an open order
curl -X PUT http://localhost:8080/orders/1/cancel

# Response: 200 OK — order cancelled
# Response: 409 Conflict — order is already cancelled
# Response: 404 Not Found — order does not exist
```

### Query Orders Example
```bash
# Get all orders for a specific customer
curl http://localhost:8080/orders?customer_id=User0001
```

## How To Run

1. Clone this repository
2. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VS Code extension
3. Open the project with `code .` and reopen in the dev container when prompted
4. Run `make test` to run the test suite
5. Run `make run` to start the Flask server
6. Send requests to `http://localhost:8080`

## Authors
- Divi Kapoor
- Jingrui (Jackson) Feng
- Borui Zhang
- Junqi Mao
- Spenser Laier

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py
├── common
│   ├── cli_commands.py
│   ├── error_handlers.py
│   ├── log_handlers.py
│   └── status.py
├── config.py
├── models
│   ├── __init__.py
│   ├── item.py
│   ├── order.py
│   └── persistent_base.py
└── routes.py

tests/                     - test cases package
├── __init__.py
├── factories.py
├── test_cli_commands.py
├── test_item.py
├── test_order.py
└── test_routes.py
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
