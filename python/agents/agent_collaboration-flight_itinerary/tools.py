#!/usr/bin/env python
#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module contains the tools used in the collaborative planner workflow."""

import random


def get_weather(city: str) -> str:
    """Gets the weather for a given city."""
    # In a real scenario, this would call a weather API
    weathers = ["Sunny", "Cloudy", "Rainy", "Windy"]
    return f"The weather in {city} is currently {random.choice(weathers)}."


def convert_currency(
    amount: float, to_currency: str, from_currency: str
) -> str:
    """Converts an amount from one currency to another."""
    # In a real scenario, this would call a currency API
    conversion_rate = random.uniform(0.5, 2.0)
    converted_amount = amount * conversion_rate
    return f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}."


def book_flight(destination: str, date: str) -> str:
    """Books a flight to a given destination for a specific date."""
    return f"Flight to {destination} on {date} has been successfully booked."
