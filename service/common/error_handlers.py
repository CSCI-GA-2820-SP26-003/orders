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
Module: error_handlers

Flask-RESTX automatically converts HTTP exceptions (400, 404, 405, 415, 500)
into JSON responses for routes registered via @api.route(...). Therefore this
module only registers handlers for cases Flask-RESTX does NOT cover:

  - DataValidationError: a custom exception raised by the models layer
  - 404 Not Found: for URLs that do not match any registered route
    (Flask handles these before Flask-RESTX sees them)
  - 405 Method Not Allowed: for valid URLs hit with the wrong HTTP method
    (also handled by Flask before reaching Flask-RESTX)

Do not add handlers for standard HTTPException codes raised inside RESTX
routes — they are redundant.
"""
from flask import jsonify
from flask import current_app as app  # Import Flask application
from werkzeug.exceptions import NotFound, MethodNotAllowed
from service.models import DataValidationError
from service.routes import api
from . import status


######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles Value Errors from bad data"""
    message = str(error)
    app.logger.warning(message)
    return {
        "status": status.HTTP_400_BAD_REQUEST,
        "error": "Bad Request",
        "message": message,
    }, status.HTTP_400_BAD_REQUEST


@app.errorhandler(NotFound)
def not_found(error):
    """Handles 404 Not Found errors with a JSON response"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_404_NOT_FOUND,
            error="Not Found",
            message=message,
        ),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(MethodNotAllowed)
def method_not_allowed(error):
    """Handles 405 Method Not Allowed errors with a JSON response"""
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method Not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )
