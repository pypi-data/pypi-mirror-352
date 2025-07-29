#!/usr/bin/env python
# -*-coding:utf-8-*-

import random
import string

default_choice_string = string.printable


def random_string_generator(max_length=100,
                            choice_string=default_choice_string):
    """
    random string generator

    """
    data = []
    random_length = random.randint(1, max_length)
    for i in range(random_length):
        x = random.choice(choice_string)
        data.append(x)
    return ''.join(data)
