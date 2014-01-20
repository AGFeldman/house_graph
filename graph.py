from get_member_info import query
from itertools import combinations

member_info = query()

for person in member_info:
    memberships = person[1]
    combos = list(combinations(memberships, 2))
    print combos
