# -*- coding: utf-8 -*-

class Scc1InvalidProductId(ValueError):
    """Indicates a product id that is not supported"""

    def __init__(self, product_id: int) -> None:
        super().__init__(f'The {product_id} is not valid!')


class Scc1NotSupportedException(ValueError):
    """Indicates a feature that is not (yet) supported."""


class Scc1InvalidDataReceived(IOError):
    """Indicates the reception of invalid data from the device"""
