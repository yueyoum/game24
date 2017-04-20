# -*- coding: utf-8 -*-

import itertools
from operator import add, sub, mul, div

OPERATIONS = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': div,
}

PRIORITY = {
    '+': ['+', '-'],
    '-': ['+', '-'],
    '*': ['*', '/'],
    '/': ['*', '/'],
}


# 后缀表达式， 运算符在后面
# 比如中缀表达式 1 * ( 2 + 3 ) 对应的后缀表达式是 1 2 3 + *
# 后缀表达式的优点就是 不用借助括号， 表达式求值的顺序是确定的
# SuffixFormula 类用来表示一个后缀表达式
# 对其求值，转成中缀表达式，最重要的就是变换表达式，除去重复


class SuffixFormula(object):
    def __init__(self):
        # 每次压入一个元素，遇到 运算符 立即求值。
        # 这里最适合用stack数据结构，但用list模拟
        self.stack = []
        # sequence 仅仅是保存了原始序列
        self.sequence = []
        self.op_amount = 0
        # push进来的元素是否能组成一个合法的表达式
        self.invalid = True

    def push(self, item):
        # 把item压入stack, item 要么是 数字， 要么是操作符
        # 如果是操作符，那么立即将栈顶的两个元素出栈，
        # 再把根据此运算符计算出的结果，压栈
        # 返回bool值， False表示此次入栈的item 会导致这是一个非法的表达式

        """

        :rtype: bool
        """
        self.sequence.append(item)

        if not self.invalid:
            return False

        if item not in OPERATIONS:
            self.stack.append(item)
            return True

        # 遇到操作符，栈顶两元素出栈，并且将计算结果再入栈
        # 这里会遇到的错误情况： 前面不够两个元素，或者0作了除数
        try:
            n1 = self.stack.pop(-1)
            n2 = self.stack.pop(-1)
        except IndexError:
            self.invalid = False
            return False

        try:
            n3 = OPERATIONS[item](float(n2), n1)
        except ZeroDivisionError:
            self.invalid = False
            return False

        self.stack.append(n3)
        self.op_amount += 1
        return True

    def value(self):
        # 获取表达式的值，对于合法的表达式，在push的过程中已经完成了求值过程
        # 就是stack中唯一的元素
        """

        :rtype: int
        """
        return self.stack[0]

    @staticmethod
    def _find_sub_sequence_index(sequence, pos):
        # 找子表达式的起始位置， pos是此子表达式的 运算符
        # 这里要利用到表达式的特性： 一个合法的表达式序列中，数字的数量=运算符数量+1
        # 比如 12+3+4+
        # 第一个+，一个运算符，需要往前面找两个数字，刚好是 1 2
        # 第二个+，也需要往前面找两个数字，但找到一个数字后，又遇到一个运算符，
        # 此时还需要找 2+1-1 个数字

        if sequence[pos] not in OPERATIONS:
            raise ValueError("item at post is not operator")

        num_amount = 0
        op_amount = 0
        index = pos
        while index >= 0:
            if sequence[index] in OPERATIONS:
                op_amount += 1
            else:
                num_amount += 1

            if num_amount == op_amount + 1:
                return index

            index -= 1

        raise ValueError("can not find sub index")

    # 下面 _normalize 开头的方法是对 表达式序列 按照一定规则进行变换，从而达到去重的目的
    def _normalize_remove_brackets(self, sequence, op):
        # 去掉多余括号
        # 有这几个表达式：
        # 1. 1 + (2 + (3 - 4))  =>  1 2 3 4 - + +
        # 2. (1 + 2) + (3 - 4)  =>  1 2 + 3 4 - +
        # 3. 1 + 2 + 3 - 4      =>  1 2 + 3 + 4 -
        # 因为括号，导致后缀表达式不一样， 但中缀表达式实质上是一样的
        # 这样的情况会对下面的 交换 处理有干扰，
        # 所以去掉括号，统一处理成3 那种情况

        loop = True
        while loop:
            loop = False
            for index in range(3, len(sequence)):
                if sequence[index] != op:
                    continue

                # 前面的是 同等优先级的 运算符，才能这么处理
                if sequence[index - 1] not in PRIORITY[op]:
                    continue

                if sequence[index - 2] in OPERATIONS:
                    to_index = self._find_sub_sequence_index(sequence, index - 2)
                else:
                    to_index = index - 2

                sequence.pop(index)
                sequence.insert(to_index, op)
                loop = True
                # 因为后面的运算符放到前面去，可能导致前面的也可以去掉括号
                # 所以这里需要一遍一遍的遍历
                break

        return sequence

    def _normalize_exchange(self, sequence):
        # 对 '+', '*' 的 两边 进行交换
        # 有这几个表达式：
        # 1. 4 + 3 * (1 + 2)  =>  4 3 1 2 + * +
        # 2. 4 + 3 * (2 + 1)  =>  4 3 2 1 + * +
        # 3. 4 + (1 + 2) * 3  =>  4 1 2 + 3 * +
        # 4. 3 * (1 + 2) + 4  =>  3 1 2 + * 4 +
        # 虽然后缀表达式不相同，但中缀表达式确实重复
        # 这里就要变换后缀表达式，从而使得这三种写法的中缀表达式，都变换成一种。
        # 如何定位 两边的元素 及 交换规则
        # AB+, +前面是两个数字， 那么两边就是A 和 B，把小的放前面
        # ABC+D*, * 前面是数字和+, 那么 两边就是 D 和 +的子表达式，把数字D放在子表达式前面

        for index in range(2, len(sequence)):
            if sequence[index] == '+' or sequence[index] == '*':
                # changeable
                item1 = sequence[index - 2]
                item2 = sequence[index - 1]

                if item2 in OPERATIONS:
                    # item2 是运算符，对应这种情况 ? + *
                    sub_index_2 = self._find_sub_sequence_index(sequence, index - 1)
                    if sequence[sub_index_2 - 1] not in OPERATIONS:
                        # 对应这种情况 1 2 3 + *, 数字已经在子表达式前面了，不用交换
                        continue

                    # 对应这种情况 1 2 + 3 4 + *, 两个子表达式按照第一个数字大小决定是否需要交换
                    sub_index_1 = self._find_sub_sequence_index(sequence, sub_index_2 - 1)
                    if sequence[sub_index_2] >= sequence[sub_index_1]:
                        continue

                    # 把sub_index_2开始的子表达式放到前面去
                    sub_seq_2 = []
                    for _ in range(index - 1 - sub_index_2 + 1):
                        sub_seq_2.insert(0, sequence.pop(sub_index_2))

                    for s in sub_seq_2:
                        sequence.insert(sub_index_1, s)

                    continue

                if item1 not in OPERATIONS:
                    # item2, item1 都是数字，对应这种情况 1 2 +,把小的放前面
                    if item1 > item2:
                        sequence[index - 2], sequence[index - 1] = sequence[index - 1], sequence[index - 2]

                    continue

                # item2 是数字，item1 是运算符，对应这种情况 * 1 +
                # 这时候要找到*子表达式的起始位置，然后把1放过去
                sub_index = self._find_sub_sequence_index(sequence, index)
                sequence.pop(index - 1)
                sequence.insert(sub_index, item2)

        return sequence

    def _normalize_exchange_special(self, sequence, op):
        # 上面只是对 '+', '*' 等做的处理，
        # '-', '/' 的处理比较复杂，而且去掉括号后，还要改变其他运算符，本来就不是重复的，所以可以不处理
        # 但有一种特殊情况，需要处理
        # 1 - 2 - 3  =>  1 2 - 3 -
        # 1 - 3 - 2  =>  1 3 - 2 -
        # 这两种情况其实是一样，算作重复。 对于除法也一样。
        # 只对后面两个数字 按照大小排序处理

        for index in range(len(sequence)):
            try:
                a = sequence[index]
                b = sequence[index + 1]
                c = sequence[index + 2]
                d = sequence[index + 3]
                e = sequence[index + 4]
            except IndexError:
                break

            if a not in OPERATIONS and b not in OPERATIONS and c == op and d not in OPERATIONS and e == op:
                if d < b:
                    sequence[index+1] = d
                    sequence[index+3] = b

        return sequence

    def _normalize_same_op(self, sequence, op):
        # 相同的运算符，只有 '+' 或者 '*'
        # 1 + (2 + (3 + 4))  =>  1 2 3 4 + + +
        # (1 + 2) + (3 + 4)  =>  1 2 + 3 4 + +
        # 1 + 2 + 3 + 4      =>  1 2 + 3 + 4 +
        # 这几种情况是一样的，但上面的 exchange 还是把 后缀表达式处理成不同的。
        # 因此，这里直接简单的处理成第一种情况， 数字按照大小排序

        op_amount = 0
        for s in sequence:
            if s == op:
                op_amount += 1

        if op_amount != self.op_amount:
            return sequence

        for _ in range(op_amount):
            sequence.remove(op)

        sequence.sort()
        sequence.extend([op] * op_amount)
        return sequence

    def to_normalize(self):
        sequence = self.sequence[:]

        sequence = self._normalize_exchange(sequence)
        # sequence = self._normalize_remove_brackets(sequence, '+')
        # sequence = self._normalize_remove_brackets(sequence, '*')
        # sequence = self._normalize_exchange(sequence)
        sequence = self._normalize_same_op(sequence, '+')
        sequence = self._normalize_same_op(sequence, '*')
        sequence = self._normalize_exchange_special(sequence, '-')
        sequence = self._normalize_exchange_special(sequence, '/')

        return sequence

    def to_infix(self):
        # 返回 中缀表达式 字符串
        sequence = self.to_normalize()

        while True:
            if len(sequence) == 1:
                break

            for index in range(len(sequence)):
                if sequence[index] in OPERATIONS:
                    express = '({0} {1} {2})'.format(
                        sequence[index - 2], sequence[index], sequence[index - 1]
                    )

                    sequence.pop(index - 2)
                    sequence.pop(index - 2)
                    sequence.pop(index - 2)

                    sequence.insert(index - 2, express)
                    break

        return sequence[0][1:-1]


# 公式生成器，暴力枚举所有组合
class FormulaGenerator(object):
    def __init__(self, *numbers):
        self.numbers = numbers

    @staticmethod
    def _is_invalid_sequence(seq):
        number_amount = 0
        op_amount = 0
        for s in seq:
            if s in OPERATIONS:
                op_amount += 1
            else:
                number_amount += 1

            if op_amount >= number_amount:
                return False

        return True

    def __iter__(self):
        ops = itertools.product(['+', '-', '*', '/'], repeat=len(self.numbers) - 1)
        for op in ops:
            sequence = itertools.permutations(self.numbers + op)
            for seq in sequence:
                if self._is_invalid_sequence(seq):
                    yield seq


def find(target, *numbers):
    results = set()

    fg = FormulaGenerator(*numbers)
    for seq in fg:
        sf = SuffixFormula()

        for s in seq:
            if not sf.push(s):
                break

        # 上面把生成的公式序列放入 SuffixFormula 后
        # 如果这个序列不合法，就尝试下一个序列
        if not sf.invalid:
            continue

        # 序列是合法的公式，那么其值和 target 接近，就认为相等
        # 因为有除法，会有小数
        if abs(sf.value() - target) > 1e-3:
            continue

        # 如果是相同的公式，就会在这里过滤掉
        results.add(sf.to_infix())

    return list(results)
