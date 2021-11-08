#! /usr/bin/env python

from lab.parser import Parser


def fix_values(content, props):
    copy_val("initial_h_value", props)
    fix_val("cost", props)


def fix_val(key, props):
    if key in props:
        props["fixed_%s" % key] = int(props[key] // 10000)


def copy_val(key, props):
    if key in props:
        props["fixed_%s" % key] = props[key]





parser = Parser()

parser.add_function(fix_values)

parser.parse()
