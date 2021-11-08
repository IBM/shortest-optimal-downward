#! /usr/bin/env python

from lab.parser import Parser


def fix_init(content, props):
    if "initial_h_value" in props:
        props["fixed_initial_h_value"] = float(props["initial_h_value"] / 10000.0)

def fix_cost(content, props):
    if "cost" in props:
        props["fixed_cost"] = float(props["cost"] // 10000)




parser = Parser()

parser.add_function(fix_init)
parser.add_function(fix_cost)

parser.parse()
