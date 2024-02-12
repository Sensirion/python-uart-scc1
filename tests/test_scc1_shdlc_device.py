# -*- coding: utf-8 -*-
import pytest
import re


@pytest.mark.needs_hardware
def test_scc1_device(scc1_device):
    assert scc1_device is not None
    assert re.match("SCC1-([^@])*@COM.", str(scc1_device))
