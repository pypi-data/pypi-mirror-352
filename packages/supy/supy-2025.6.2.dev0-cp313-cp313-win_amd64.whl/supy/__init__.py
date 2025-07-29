###########################################################################
# SuPy: SUEWS that speaks Python
# Authors:
# Ting Sun, ting.sun@reading.ac.uk
# History:
# 20 Jan 2018: first alpha release
# 01 Feb 2018: performance improvement
# 03 Feb 2018: improvement in output processing
# 08 Mar 2018: pypi packaging
# 01 Jan 2019: public release
# 22 May 2019: restructure of module layout
# 02 Oct 2019: logger restructured
###########################################################################


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'supy.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

# core functions
from ._supy_module import (
    init_supy,
    load_SampleData,
    load_sample_data,
    load_forcing_grid,
    load_config_from_df,
    run_supy,
    save_supy,
    check_forcing,
    check_state,
    init_config,
    run_supy_sample,
    resample_output,
)

# debug utilities
from ._post import (
    pack_dts_state_selective,
    inspect_dts_structure,
    dict_structure,
)

# utilities
from . import util

# data model
from . import data_model

# version info
from ._version import show_version, __version__

from .cmd import SUEWS

# module docs
__doc__ = """
supy - SUEWS that speaks Python
===============================

**SuPy** is a Python-enhanced urban climate model with SUEWS as its computation core.

"""
