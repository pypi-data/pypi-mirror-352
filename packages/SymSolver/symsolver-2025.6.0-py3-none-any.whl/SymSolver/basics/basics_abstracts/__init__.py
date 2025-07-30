"""
Package Purpose: abstract objects which need basics objects to be defined,
but which are also required in the definition of other basic objects.

Commonly, the required objects are just tools from basics_tools.

For example, AbstractProduct requires get_summands() to define its distributive property.

This file:
Imports the main important objects throughout this subpackage.
"""

from .abstract_products import AbstractProduct