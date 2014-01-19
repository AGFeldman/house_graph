import re
from urllib2 import urlopen
from HTMLParser import HTMLParser
import xml.etree.ElementTree as ET

directory_url = 'http://donut.caltech.edu/directory/'

html = urlopen(directory_url).read()
option_source = html[html.index('<form'):html.index('</form')]
select_id_re = re.compile('<select id.*?</select>', re.DOTALL)
category_list = select_id_re.findall(option_source)
root = ET.fromstring(category_list[0])
id_ = root.attrib['id']
option_dic = {}
for child in root:
    option_dic[child.text] = child.attrib['value']
print option_dic
