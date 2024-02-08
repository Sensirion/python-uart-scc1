#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test_import():
    try:
        import sensirion_uart_scc1  # noqa: F401
        assert True
    except ImportError:
        assert False
