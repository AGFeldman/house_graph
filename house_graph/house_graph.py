import re
from urllib2 import urlopen
import xml.etree.cElementTree as ET

# the search page for the Caltech undergrad directory
directory_url = 'http://donut.caltech.edu/directory/'

# the beginning of the url for searches
base_search_rul = directory_url + 'index.php?state=search'

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

print selection_dics['houseid']
