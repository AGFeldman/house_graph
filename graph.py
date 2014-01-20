#!/usr/bin/env python
"""
This module makes DOT graphs using membership info queried with the
get_member_info module.
"""

import get_member_info as gmi
from itertools import combinations
from shutil import copy2

input_ = gmi.get_user_input()
outputname = raw_input('Name of output file? (Should end in .dot): ')
if outputname == '':
    outputname = 'output.dot'
copy2('template.dot', outputname)
title = gmi.make_title(input_)
member_info = gmi.query(input_)

def dot_code_from_combo(combo):
    """Given a combination ((houseA, is_full_memberA),
    (houseB, is_full_memberB)), returns a line of .dot code that draws the 
    appropriate line between houseA and houseB. If is_full_memberA and
    is_full_memberB, then a black line with no arrows should be drawn.
    If is_full_memberA but not is_full_memberB, then there should be a gray
    arrow from houseA to houseB, with a dot as the arrow tail. Similarly
    if not is_full_memberA but is_full_memberB. If not is_full_memberA
    and not is_full_memberB, then there should be a chocolate-colored line
    with no arrows drawn.
    """
    numfull = 0
    if combo[0][1]:
        numfull += 1
        house1 = combo[0][0]
        house2 = combo[1][0]
    else:
        house1 = combo[1][0]
        house2 = combo[0][0]
    if combo[1][1]:
        numfull += 1
    dir_ = 'both'
    if numfull == 2:
        color = 'black'
        arrowhead = 'none'
        arrowtail = 'none'
    elif numfull == 1:
        color = 'gray'
        arrowhead = 'normal'
        arrowtail = 'dot'
    else:
        color = 'chocolate'
        arrowhead = 'none'
        arrowtail = 'none'
    code = ''.join(['    ', house1, ' -> ', house2, '[dir=', dir_, 
        ' arrowhead=', arrowhead, ' arrowtail=', arrowtail, ', color=',
        color, '];'])
    return code

with open(outputname, 'a') as out:
    out.write('label=\"' + title + '\";')
    out.write('labelloc=top')
    for person in member_info:
        memberships = person[1]
        combos = list(combinations(memberships, 2))
        for combo in combos:
            out.write(dot_code_from_combo(combo))
    out.write('}')


