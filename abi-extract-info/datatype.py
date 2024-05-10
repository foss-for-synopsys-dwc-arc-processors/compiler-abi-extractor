# Copyright 2025-present, Synopsys, Inc.
# All rights reserved.
#
# This source code is licensed under the GPL-3.0 license found in
# the LICENSE file in the root directory of this source tree.

from lib.comp import compilation
from lib.prec import pre_condition
from lib.bash import bash

pre_condition ("test -e tests/datatype_gen.py")
pre_condition ("test -d tmp/")
pre_condition ("which python3")

bash ("python3 tests/datatype_gen.py > tmp/datatype.c")
compilation (
    cc="gcc", 
    cflags="-O2",
    _input="tmp/datatype.c",
    output="tmp/datatype.x"
  )
