# -*- coding: utf-8 -*-

import sys

from game24 import find

expect_value = int(sys.argv[1])
input_amount = int(sys.argv[2])
input_numbers = []
for i in range(input_amount):
    input_numbers.append(int(sys.argv[i + 3]))

formulas = find(expect_value, *input_numbers)
if not formulas:
    print "无解"
else:
    for f in formulas:
        print f, "=", expect_value
