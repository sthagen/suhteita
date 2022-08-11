#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""CLI operations for relationships (Finnish: suhteita) maintained across distances as load test core."""
import sys
from typing import List, Union

import suhteita.suhteita as api


# pylint: disable=expression-not-assigned
def main(argv: Union[List[str], None] = None) -> int:
    """Delegate processing to functional module."""
    argv = sys.argv[1:] if argv is None else argv
    return api.main(argv)
