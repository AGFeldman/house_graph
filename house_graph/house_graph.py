import re
from urllib2 import urlopen
import xml.etree.cElementTree as ET

# the search page for the Caltech undergrad directory
directory_url = 'http://donut.caltech.edu/directory/'

# the beginning of the url for searches
base_search_url = directory_url + 'index.php?state=search'

html = urlopen(directory_url).read()
# re looks for html code corresponding to drop-down selection
select_id_re = re.compile('<select id.*?</select>', re.DOTALL)
# list of the text of each drop-down selection
selection_list = select_id_re.findall(html)
# a dictionary of dictionaries.
# category: dictionary between selection and value
selection_dics = {}

for selection in selection_list:
    # we have to replace '&' with 'and' so that we can work with well-formed XML
    root = ET.XML(selection.replace('&', 'and'))
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

print get_html_with_search({'houseid': selection_dics['houseid']['Blacker'], 'group': selection_dics['group']['ug-2016']})
