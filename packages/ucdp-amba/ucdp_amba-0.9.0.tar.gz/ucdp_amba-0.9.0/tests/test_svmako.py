#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Test sv.mako."""

import os
from unittest import mock

import ucdp as u
from test2ref import assert_refdata


def test_ahb2apb(tmp_path):
    """AHB2APB Module."""
    top = u.load("ucdp_amba.ucdp_ahb2apb")
    with mock.patch.dict(os.environ, {"PRJROOT": str(tmp_path)}):
        u.generate(top.mod, "hdl")
    assert_refdata(test_ahb2apb, tmp_path)


def test_ahb_ml(tmp_path):
    """AHB Multilayer Module."""
    top = u.load("ucdp_amba.ucdp_ahb_ml")
    with mock.patch.dict(os.environ, {"PRJROOT": str(tmp_path)}):
        u.generate(top.mod, "hdl")
    assert_refdata(test_ahb_ml, tmp_path)


def test_apb2mem(tmp_path):
    """APB2MEM Module."""
    top = u.load("ucdp_amba.ucdp_apb2mem")
    with mock.patch.dict(os.environ, {"PRJROOT": str(tmp_path)}):
        u.generate(top.mod, "hdl")
    assert_refdata(test_apb2mem, tmp_path)


def test_ahb2ahb(tmp_path):
    """AHB2AHB Module."""
    top = u.load("ucdp_amba.ucdp_ahb2ahb")
    with mock.patch.dict(os.environ, {"PRJROOT": str(tmp_path)}):
        u.generate(top.mod, "hdl")
    assert_refdata(test_ahb2ahb, tmp_path)
