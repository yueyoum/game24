# -*- coding: utf-8 -*-

import sys

from game24 import find

expect_value = int(sys.argv[1])
input_numbers = []
for i in range(2, len(sys.argv)):
    input_numbers.append(int(sys.argv[i]))

formulas = find(expect_value, *input_numbers)
if not formulas:
    print "no results"
else:
    for f in formulas:
        print f, "=", expect_value
