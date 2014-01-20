#!/usr/bin/env python
"""
This module makes DOT graphs using membership info queried with the
get_member_info module.
"""

import get_member_info as gmi
from shutil import copy2

min_memberships = 2
input_ = gmi.get_user_input()
outputname = raw_input('Name of output file? (Should end in .dot): ')
if outputname == '':
    outputname = 'output.dot'
include_single_members = raw_input('Include students who are members of only '\
        'one house? (y/n): ')
if include_single_members == 'y':
    min_memberships = 1
copy2('template.dot', outputname)
title = gmi.make_title(input_)
member_info = gmi.query(input_)

def get_dot_code_for_person(person):
    name = '\"' + person[0] + '\"'
    lines = []
    lines.append('    ' + name + ';\n')
    for membership in person[1]:
        if membership[1]:
            color = 'black'
        else:
            color = 'gray'
        lines.append(''.join(['    ', name, ' -- ', membership[0],
            '[color=', color, '];\n']))
    return lines

with open(outputname, 'a') as out:
    out.write('    label=\"' + title + '\";\n')
    out.write('    labelloc=top;\n')
    for person in member_info:
        if len(person[1]) >= min_memberships:
            lines = get_dot_code_for_person(person)
            for line in lines:
                out.write(line)
    out.write('}')
