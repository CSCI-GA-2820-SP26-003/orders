# lab-github-actions

[![Build Status](https://github.com/CSCI-GA-2820-SP26-003/orders/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP26-003/orders/actions)

[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP26-003/orders/graph/badge.svg?token=1QJGFVMZA4)](https://codecov.io/gh/CSCI-GA-2820-SP26-003/orders)

# NYU Devops Orders Microservice

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This project implements an `orders` microservice that exposes several different operations and endpoints
for use within an ecommerce platform. 

## Overview

The Orders Service is a RESTful microservice for managing orders and their line items. It is built with Flask + Flask-RESTX, SQLAlchemy, and PostgreSQL, and ships with a web UI and auto-generated Swagger documentation at `/apidocs`.

## API Endpoints

All endpoints are prefixed with `/api`. Interactive Swagger documentation is available at `/apidocs`.

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders` | Create a new order |
| GET | `/api/orders` | List all orders |
| GET | `/api/orders/{order_id}` | Retrieve a single order |
| PUT | `/api/orders/{order_id}` | Update an existing order |
| DELETE | `/api/orders/{order_id}` | Delete an order |

### Order Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/api/orders/{order_id}/cancel` | Cancel an order (sets status to CANCELED) |

### Order Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders/{order_id}/items` | Add an item to an order |
| GET | `/api/orders/{order_id}/items` | List all items in an order |
| GET | `/api/orders/{order_id}/items/{item_id}` | Retrieve a specific item |
| PUT | `/api/orders/{order_id}/items/{item_id}` | Update an item |
| DELETE | `/api/orders/{order_id}/items/{item_id}` | Delete an item |

### Health & Docs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| GET | `/apidocs` | Swagger / OpenAPI documentation |

### Query Parameters

| Endpoint | Parameter | Description |
|----------|-----------|-------------|
| GET `/api/orders` | `customer_id` | Filter orders by customer ID |
| GET `/api/orders` | `status` | Filter by status (`OPEN`, `SHIPPED`, `DELIVERED`, `CANCELED`) |

### Cancel Order Example

```bash
# Cancel an open order
curl -X PUT http://localhost:8080/api/orders/1/cancel
# Response: 200 OK — order cancelled
# Response: 409 Conflict — order is already cancelled
# Response: 404 Not Found — order does not exist
```

### Query Orders Example

```bash
# Get all orders for a specific customer
curl http://localhost:8080/api/orders?customer_id=User0001

# Filter by customer and status
curl "http://localhost:8080/api/orders?customer_id=User0001&status=OPEN"
```

## How To Run

1. Clone this repository
2. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VS Code extension
3. Open the project with `code .` and reopen in the dev container when prompted
4. Run `make test` to run the test suite
5. Run `make run` to start the Flask server on port 8080
6. Open `http://localhost:8080` to use the web UI, or send requests to the API directly

If you change the schema, run `flask db-create` to drop and recreate the tables (`db.create_all()` does not alter existing tables).

## Authors

- Divi Kapoor
- Jingrui (Jackson) Feng
- Borui Zhang
- Junqi Mao
- Spenser Laier

## Contents

The project contains the following:

```text
.gitignore               - this will ignore vagrant and other metadata files
.flaskenv                - Environment variables to configure Flask
.gitattributes           - File to fix Windows CRLF issues
.devcontainer/           - Folder with support for VSCode Remote Containers
.github/workflows/       - GitHub Actions CI configuration
.tekton/                 - Tekton CD pipeline, tasks, and EventListener
dot-env-example          - copy to .env to use environment variables
Pipfile / Pipfile.lock   - Python dependencies managed by pipenv
Dockerfile               - Container image definition
Makefile                 - Common development commands

features/                - Behave BDD scenarios and step definitions
├── environment.py
├── orders.feature
└── steps/
    ├── orders_steps.py
    └── web_steps.py

k8s/                     - Kubernetes / OpenShift manifests
├── deployment.yaml
├── service.yaml
├── route.yaml
├── ingress.yaml
└── postgresql/

service/                 - service python package
├── __init__.py
├── config.py
├── routes.py            - Flask-RESTX route definitions
├── common/
│   ├── cli_commands.py
│   ├── error_handlers.py
│   ├── log_handlers.py
│   └── status.py
├── models/
│   ├── __init__.py
│   ├── item.py
│   ├── order.py
│   └── persistent_base.py
└── static/              - Web UI (HTML, CSS, JS)
    ├── index.html
    ├── css/
    └── js/

tests/                   - test cases package
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
