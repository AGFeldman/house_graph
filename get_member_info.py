#!/usr/bin/env python
"""
This module contains the query function and its many helper functions.
These functions can be used to scrape data from the Caltech undergrad directory,
get user input about which groups of undergraduates to consider, and return
membership information about the undergrads under consideration.
"""

import re
from urllib2 import urlopen
import xml.etree.cElementTree as ET
# html.fromstring returns Element objects from (possibly ill-formed) html
from lxml import html  

home_url = 'http://donut.caltech.edu'
# the search page for the Caltech undergrad directory
directory_url = home_url + '/directory/'
# the beginning of the url for searches
base_search_url = directory_url + 'index.php?state=search'

htmlcode = urlopen(directory_url).read()
# re looks for html code corresponding to drop-down selection
select_id_re = re.compile('<select id.*?</select>', re.DOTALL)
# list of the text of each drop-down selection
selection_list = select_id_re.findall(htmlcode)
# a dictionary of dictionaries describing possible search fields.
# category: dictionary between selection and value
selection_dics = {}

for selection in selection_list:
    root = html.fromstring(selection)
    id_ = root.attrib['id']
    # the current possible ids are 'houseid', 'group', 'optionid', 'buildingid'
    option_dic = {}
    for child in root:
        option_dic[child.text] = child.attrib['value']
    selection_dics[id_] = option_dic

# re that matches the section of html code that contains a list of names
namelist_re = re.compile(
        '<table.{0,300}?Name.*?Email.*?Graduation.*?</table>', re.DOTALL)

def get_raw_html_from_search(search):
    """Returns a string of the html code that comes from the search specified
    by SEARCH. The format of SEARCH is (selection_id, value).
    """
    url = ''.join([base_search_url, '&', search[0], '=', search[1]])
    return urlopen(url).read()

def get_html_from_search(search):
    """Uses get_raw_html_from_search to get a string of the html code that
    comes from the search specified by SEARCH, then returns the part
    of that html code that contains the list of names.
    """
    raw_html = get_raw_html_from_search(search)
    re_results = namelist_re.findall(raw_html)
    if len(re_results) > 0:
        return re_results[0]

houses = ['Avery', 'Blacker', 'Dabney', 'Fleming', 'Lloyd', 'Page',
        'Ricketts', 'Ruddock']

def find_house_in_text(line):
    """Given a LINE of text, searches to see if any of the houses' names
    appear in the line. If the house name does appear in the line, searches
    to see whether the word 'Full' also appears in the line (indicating full
    membership, as opposed to social membership). If there is a house
    membership in the line, returns a tuple (house, is_full_member).
    """
    for house in houses:
        if house in line:
            fullness = 'Full' in line
            if not fullness:
                if not 'Social' in line:
                    return
            return house, fullness

house_affiliations_re = re.compile('House Affiliations.*?</tr>',
        re.DOTALL)

def get_member_info(url):
    """Given a URL for a personal page on the directory, returns a list of 
    tuples detailing house memberships. (The tuples are detailed in the
    find_house_in_text function.)
    """
    members_houses = []
    text = urlopen(url).read()
    text = house_affiliations_re.findall(text)
    if len(text) > 0:
        text = text[0]
    else:
        return []
    for line in text.split('\n'):
        houseinfo = find_house_in_text(line)
        if houseinfo is not None:
            members_houses.append(houseinfo)
    return members_houses

def get_name_and_link(line):
    """Given an html snippet that looks something like
    <a href='/directory.etc/'>First Last Name</a, returns a tuple
    ('First Last Name', '/directory.etc/')
    """
    link_begin_tag = 'href=\''
    link_end_tag = '\'>'
    name_end_tag = '</a'
    link_begin_index = line.index(link_begin_tag) + len(link_begin_tag)
    link_end_index = line.index(link_end_tag)
    name_begin_index = link_end_index + len(link_end_tag)
    name_end_index = line.index(name_end_tag)
    link = line[link_begin_index : link_end_index]
    name = line[name_begin_index : name_end_index]
    return name, home_url + link

# re matches a line that contains an individual's name and link to personal
# page.
individual_a_re = re.compile('<a href=\'/dir.*?</a', re.DOTALL)

def get_names_links_from_search(search):
    """Returns a set of tuples (name, link_to_personal_page) resulting
    from the search specified by SEARCH"""
    processed_html = get_html_from_search(search)
    if processed_html is None:
        return set([])
    individual_line_list = individual_a_re.findall(processed_html)
    name_link_set = set([])
    for indiv in individual_line_list:
        name_link_set.add(get_name_and_link(indiv))
    return name_link_set
 
def names_memberships_from_names_links(name_link_set):
    """Given NAME_LINK_SET, a set of names and links to their corresponding
    personal pages, returns a list of tuples (name, membership_info).
    """
    name_membership_list = []
    for el in name_link_set:
        name = el[0]
        url = el[1]
        member_info = get_member_info(url)
        name_membership_list.append((name, member_info))
    return name_membership_list

# A dictionary {number that user can choose, corresponding url snippet}
choices_for_user = {}
display_for_user_list = []
num_to_selection = {}
count = 0
for group in selection_dics:
    display_for_user_list.append(group)
    for el in selection_dics[group]:
        choices_for_user[count] = (group, selection_dics[group][el])
        display_for_user_list.append(str(count) + '\t' + el)
        num_to_selection[count] = el
        count += 1
    display_for_user_list.append('')
display_for_user = '\n'.join(display_for_user_list)
with open('user_choices.txt', 'w') as file_:
    file_.write(display_for_user)

operators = set(['&', '|'])
delimiters = set(['(', ')'])
op_and_de = set.union(operators, delimiters)

def split_by_operator(input_):
    """Example: '(53&600&7|8)|10' ->
    ['(', '53', '&', '600', '&', '7', '|', '8', ')', '|', '10']
    """
    mylist = []
    most_recent = ''
    for c in input_:
        if c not in op_and_de:
            most_recent += c
        else:
            if most_recent != '':
                mylist.append(most_recent)
                most_recent = ''
            mylist.append(c)
    if most_recent != '':
        mylist.append(most_recent)
    return mylist

def sub_with_searches(mylist):
    """Substitutes numbers in mylist with the python code that gets name-link
    information from the search corresponding to the number. For example,
    ['1', '&', '2'] -> ['get_names_links_from_search(choices_for_user[1]', '&',
    'get_names_links_from_search(choices_for_user[2]].
    """
    for i in range(len(mylist)):
        if mylist[i] not in op_and_de:
            mylist[i] = 'get_names_links_from_search(choices_for_user['\
                         + mylist[i] + '])'

def eval_operator(mylist, op, expand_to):
    """Applies the correspondence between OP and the python code EXPAND_TO.
    For example, if MYLIST = ['1', '&', '2'], OP = '&', and EXPAND_TO =
    set.intersection, then we return ['(set.intersection(1,2))'].
    """
    while op in mylist:
        ind = mylist.index(op)
        right = mylist.pop(ind + 1)
        left = mylist.pop(ind - 1)
        ind -= 1
        joinlist = ['(', expand_to, '(', left, ',', right, '))']
        mylist[ind] = ''.join(joinlist)

def eval_without_parens(mylist):
    """Expands the & and | operators in MYLIST, using eval_operator."""
    eval_operator(mylist, '&', 'set.intersection')
    eval_operator(mylist, '|', 'set.union')
    assert len(mylist) == 1
    return '(' + mylist[0] + ')'

def list_rindex(thelist, findthis):
    """Returns the rightmost index of FINDTHIS in THELIST."""
    length = len(thelist)
    ind_of_reversed = list(reversed(thelist)).index(findthis)
    return length - 1 - ind_of_reversed

def full_parse(input_):
    """Fully parses string input such as '(43 & 47) & (16 | 30 | 31 | 32)' into
    executable python code that evaluates to a set of names corresponding to
    the input and the links to personal pages for those names.
    """
    input_ = input_.replace(' ', '')
    mylist = split_by_operator(input_)
    sub_with_searches(mylist)
    mylist.insert(0, '(')
    mylist.append(')')
    while ')' in mylist:
        end_ind = mylist.index(')')
        begin_ind = list_rindex(mylist[:end_ind], '(')
        mylist[end_ind] = eval_without_parens(mylist[begin_ind + 1 : end_ind])
        del mylist[begin_ind : end_ind]
    assert len(mylist) == 1
    return mylist[0]

def user_input_to_names_links(input_):
    """Parses a string such as '(43 & 47) & (16 | 30 | 31 | 32)' and evaluates
    it in order to return a set.
    """
    return eval(full_parse(input_))

def make_title(input_):
    """Makes returns a string with numbers replaced by their corresponding
    choices. For example, (43 & 47) -> (Dabney & Blacker).
    """
    input_ = input_.replace(' ', '')
    mylist = split_by_operator(input_)
    for i in range(len(mylist)):
        if mylist[i] not in op_and_de:
            mylist[i] = num_to_selection[int(mylist[i])]
    return ''.join(mylist)

def get_user_input():
    """Prompts to user to enter a set-theoretic description of the group that
    he or she wants to consider, and returns the user's input.
    """
    print display_for_user
    msg = 'Use set operations to describe the set of people you would like to'\
            ' consider.'\
            '\nFor example, if you would like to consider Mole-Darbs'\
            '\n(students in both Blacker and Dabney)'\
            '\nin the classes of 2017, 2016, 2015, and 2014, then enter'\
            '\n\'(43 & 47) & (16 | 30 | 31 | 32)\'.'\
            '\nThe decreasing precedence order is as follows: (), &, |.'\
            '\nEnter description: '
    input_ = raw_input(msg)
    return input_

def query(input_=None):
    """Prompts the user to describe a group, and returns the names and
    membership information corresponding to that group.
    """
    if input_ is None:
        input_ = get_user_input()
    names_links_set = user_input_to_names_links(input_)
    member_info = names_memberships_from_names_links(names_links_set)
    return member_info
