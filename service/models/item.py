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
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    name = db.Column(db.String(64))

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] Order[{self.order_id}]>"

    def __str__(self):
        return (
            f"{self.id}: {self.order_id}, {self.quantity}, {self.unit_price}"
        )
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_quantity_positive'),
        db.CheckConstraint('unit_price >= 0', name='check_price_non_negative')
    )

    def serialize(self) -> dict:
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "order_id": self.order_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.order_id = data.get("order_id")
            self.name = data.get("name")
            self.quantity = data["quantity"]
            self.unit_price = data["unit_price"]
        except AttributeError as error:
            raise DataValidationError(
                "Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data "
                + str(error)
            ) from error

        return self
