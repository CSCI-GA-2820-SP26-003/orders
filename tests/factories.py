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
# cspell:ignore userid postalcode
"""
Test Factory to make fake objects for testing
"""
from factory import Factory, SubFactory, Sequence, Faker, post_generation
from service.models import Item, Order


class OrderFactory(Factory):
    """Creates fake Orders"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Order

    id = Sequence(lambda n: n)
    customer_id = Sequence(lambda n: f"User{n:04d}")
    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Item

    id = Sequence(lambda n: n)
    name = Faker("word")
    quantity = Faker("pyint", min_value=1, max_value=20)
    unit_price = Faker("pyfloat", min_value=1, max_value=500, right_digits=2)
    order = SubFactory(OrderFactory)
