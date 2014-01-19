import re
from urllib2 import urlopen
import xml.etree.cElementTree as ET
from lxml import html  # returns Element objects

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

namelist_re = re.compile(
        '<table.{0,300}?Name.*?Email.*?Graduation.*?</table>', re.DOTALL)

def get_raw_html_from_search(search_dic):
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

def get_html_from_search(search_dic):
    '''Uses get_raw_html_from_search to get a string of the html code that
    comes from the search specified by SEARCH_DIC, then returns the part
    of that html code that contains the list of names.
    '''
    raw_html = get_raw_html_from_search(search_dic)
    # print raw_html
    return namelist_re.findall(raw_html)[0]

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

def get_name_and_link(line):
    '''Given an html snippet that looks something like
    <a href='/directory.etc/'>First Last Name</a, returns a tuple
    ('First Last Name', '/directory.etc/')
    '''
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

individual_a_re = re.compile('<a href=\'/dir.*?</a')

def get_names_links_from_search(search_dic):
    '''Returns a set of tuples (name, link_to_personal_page) resulting
    from the search specified by SEARCH_DIC'''
    processed_html = get_html_from_search(search_dic)
    individual_line_list = individual_a_re.findall(processed_html)
    name_link_set = set([])
    for indiv in individual_line_list:
        name_link_set.add(get_name_and_link(indiv))
    return name_link_set
 
def get_names_links_from_many_searches(search_dics):
    '''Returns a set of tuples (name, link_to_personal_page) resulting
    from all of the searches specified in SEARCH_DICS, a list of
    dictionaries that specify searches.
    '''
    name_link_set = set([])
    for search_dic in search_dics:
        name_link_set.update(get_names_links_from_search(search_dic))
    return name_link_set

searches = [{'houseid': selection_dics['houseid']['Blacker'],
            'group': selection_dics['group']['ug-2016']},
           {'houseid': selection_dics['houseid']['Dabney'],
            'group': selection_dics['group']['ug-2016']}]

search_results = get_names_links_from_many_searches(searches)
print search_results

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

# print choices_for_user

house_affiliations_re = re.compile('House Affiliations.*?</tr>',
        re.DOTALL)

houses = ['Avery', 'Blacker', 'Dabney', 'Fleming', 'Lloyd', 'Page',
        'Ricketts', 'Ruddock']

myroot = get_member_info('http://donut.caltech.edu/directory/index.php?state=details&inum=8651')

print myroot
