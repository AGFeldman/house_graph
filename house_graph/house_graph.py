import re
from urllib2 import urlopen
import xml.etree.cElementTree as ET
from lxml import html  # returns Element objects

# the search page for the Caltech undergrad directory
directory_url = 'http://donut.caltech.edu/directory/'

# the beginning of the url for searches
base_search_url = directory_url + 'index.php?state=search'

htmlcode = urlopen(directory_url).read()
# re looks for html code corresponding to drop-down selection
select_id_re = re.compile('<select id.*?</select>', re.DOTALL)
# list of the text of each drop-down selection
selection_list = select_id_re.findall(htmlcode)
# a dictionary of dictionaries.
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

def get_html_with_search(search_dic):
    '''Returns a string of the html code that comes from the search specified
    by SEARCH_DIC. The format of SEARCH_DIC is 'selection_id: value'.
    '''
    join_list = [base_search_url]
    for el in search_dic:
        join_list.append('&')
        join_list.append(el)
        join_list.append('=')
        join_list.append(search_dic[el])
    url = ''.join(join_list)
    return urlopen(url).read()

# print get_html_with_search({'houseid': selection_dics['houseid']['Blacker'], 'group': selection_dics['group']['ug-2016']})

# A dictionary {number that user can choose, corresponding url snippet}
choices_for_user = {}
count = 0
for group in selection_dics:
    print group
    print
    for el in selection_dics[group]:
        print count, '\t', el
        urlsnippet = ''.join(['&', group, '=', selection_dics[group][el]])
        choices_for_user[count] = urlsnippet
        count += 1
    print
    print

print choices_for_user

namelist_re = re.compile(
        '<tbody>.*?Name.*?Email.*?Graduation.*?Membership.*?</tdbody>',
         re.DOTALL)

house_affiliations_re = re.compile('House Affiliations.*?</tr>',
        re.DOTALL)

houses = ['Avery', 'Blacker', 'Dabney', 'Fleming', 'Lloyd', 'Page',
        'Ricketts', 'Ruddock']

def find_house_in_text(line):
    '''Given a LINE of text, searches to see if any of the houses' names
    appear in the line. If the house name does appear in the line, searches
    to see whether the word 'Full' also appears in the line (indicating full
    membership, as opposed to social membership). If there is a house
    membership in the line, returns a tuple (house, is_full_member).
    '''
    for house in houses:
        if house in line:
            fullness = 'Full' in line
            if not fullness:
                assert 'Social' in line
            return house, fullness

def get_member_info(url):
    '''Given a URL for a personal page on the directory, returns a list of 
    tuples detailing house memberships. (The tuples are detailed in the
    find_house_in_text function.)
    '''
    members_houses = []
    text = urlopen(url).read()
    text = house_affiliations_re.findall(text)[0]
    for line in text.split('\n'):
        houseinfo = find_house_in_text(line)
        if houseinfo is not None:
            members_houses.append(houseinfo)
    return members_houses

myroot = get_member_info('http://donut.caltech.edu/directory/index.php?state=details&inum=8651')

print myroot
