# -*- coding: utf-8 -*-

"""
This file contains channels, gas modes and product specifications used by multiple SLF products
"""
from __future__ import annotations

from collections import OrderedDict
from enum import Enum

from sensirion_uart_scc1.scc1_exceptions import Scc1InvalidProductId


class SlfMode(Enum):
    LIQUI_0 = 'Liquid 0'
    LIQUI_1 = 'Liquid 1'
    LIQUI_2 = 'Liquid 2'
    LIQUI_3 = 'Liquid 3'
    LIQUI_4 = 'Liquid 4'
    LIQUI_5 = 'Liquid 5'
    LIQUI_6 = 'Liquid 6'
    LIQUI_7 = 'Liquid 7'
    LIQUI_8 = 'Liquid 8'


class SlfMeasurementCommand(object):
    MEASUREMENT_COMMANDS = {
        SlfMode.LIQUI_0: 0x3603,
        SlfMode.LIQUI_1: 0x3608,
        SlfMode.LIQUI_2: 0x3615,
        SlfMode.LIQUI_3: 0x361E,
        SlfMode.LIQUI_4: 0x3624,
        SlfMode.LIQUI_5: 0x362F,
        SlfMode.LIQUI_6: 0x3632,
        SlfMode.LIQUI_7: 0x3639,
        SlfMode.LIQUI_8: 0x3646,
    }

    @staticmethod
    def from_mode(mode):
        return SlfMeasurementCommand.MEASUREMENT_COMMANDS[mode]


#: Product id to product name mapping for SLF3x family
SLF3x_PRODUCT_NAME = {
    0x070302: 'SLF3S_1300',
    0x070303: 'SLF3S_600',
    0x070304: 'SLF3C_1300F',
    0x070305: 'SLF3S_4000B',
}

#: Product id to product name mapping for LD20 family
LD20_PRODUCT_NAME = {
    0x070102: 'LD20_2600B',
    0x070103: 'LD20-0600L'
}

SLF3x_PRODUCT_IDS = list(SLF3x_PRODUCT_NAME.keys())

LD20_2600B_PRODUCT_IDS = list(LD20_PRODUCT_NAME.keys())


class SlfProduct(Enum):
    SLF3x = 'SLF3x'
    LD20 = 'LD20-2600B',

    @staticmethod
    def from_product_id(product_id: int) -> SlfProduct:
        if product_id in SLF3x_PRODUCT_IDS:
            return SlfProduct.SLF3x
        elif product_id in LD20_2600B_PRODUCT_IDS:
            return SlfProduct.LD20
        raise Scc1InvalidProductId(product_id)


class SlfProductName:
    @staticmethod
    def from_product(product: SlfProduct, product_id: int) -> str:
        if product is SlfProduct.SLF3x:
            return SLF3x_PRODUCT_NAME.get(product_id, 'SLF3x')
        elif product is SlfProduct.LD20:
            return LD20_PRODUCT_NAME.get(product_id, 'LD20')
        raise Scc1InvalidProductId(product_id)


class SlfLiquiConfig(object):
    def __init__(self, config):
        """
        :param config: A dictionary of form mode: name, where mode is one of
                       `~sensirion_uart_scc1.drivers.slf_common.SlfMode`
        """
        self._liqui_config = config
        self._supported_liquids = list(config.keys())

    @property
    def supported_liqui_modes(self):
        return self._supported_liquids

    def liqui_mode_name(self, mode):
        return self._liqui_config[mode]


SLF_PRODUCT_LIQUI_MAP = {
    SlfProduct.SLF3x: SlfLiquiConfig(OrderedDict({
        SlfMode.LIQUI_1: 'Water',
        SlfMode.LIQUI_2: 'Isopropyl alcohol',
    })),
    SlfProduct.LD20: SlfLiquiConfig(OrderedDict({
        SlfMode.LIQUI_1: 'Water',
    }))
}

FLOW_UNIT_PREFIX = {
    3: 'n',
    4: 'u',
    5: 'm',
    6: 'c',
    7: 'd',
    8: '',  # 1
    9: '',  # 10
    10: 'h',
    11: 'k',
    12: 'M',
    13: 'G'
}

FLOW_UNIT_TIME_BASE = {
    0: '',
    1: 'us',
    2: 'ms',
    3: 's',
    4: 'min',
    5: 'h',
    6: 'day'
}

FLOW_UNIT_VOLUME = {
    0: 'nl',  # norm liter
    1: 'sl',  # standard liter
    8: 'l',  # liter (typ: liquid flow)
    9: 'g',  # gram (typ: liquid flow)
}


def get_flow_unit_label(flow_unit_raw: int) -> str:
    prefix = FLOW_UNIT_PREFIX.get(flow_unit_raw & 0xF, '')
    time_base = FLOW_UNIT_TIME_BASE.get((flow_unit_raw >> 4) & 0xF, '')
    volume = FLOW_UNIT_VOLUME.get((flow_unit_raw >> 8) & 0xF, '')
    return f'{prefix}{volume}/{time_base}'
