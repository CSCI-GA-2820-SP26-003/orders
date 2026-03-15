# lab-github-actions

[![Build Status](https://github.com/CSCI-GA-2820-SP26-003/orders/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP26-003/orders/actions)

[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP26-003/orders/graph/badge.svg?token=1QJGFVMZA4)](https://codecov.io/gh/CSCI-GA-2820-SP26-003/orders)

# NYU Devops Orders Microservice

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This project implements an `orders` microservice that exposes several different operations and endpoints
for use within an ecommerce platform. 

## Overview

The `/service` folder contains relevant models (currently `order.py` and `item.py`), 
as well as a `routes.py` file implementing specific endpoints.

The `/tests` folder contains testing-related code for both the models and routes.

## How To Run
1. Clone this repository into a local directory
2. Ensure that the devcontainers vs code extension is installed, and run `code .` to open the project (`code` may need to be added to `$PATH`)
3. Run `make test` to run tests
4. Run `make run` to run the flask server
5. Navigate to your browser at `http://localhost:8080` to submit requests to the api

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
