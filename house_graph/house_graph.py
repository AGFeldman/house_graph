import re
from urllib2 import urlopen

directory_url = 'http://donut.caltech.edu/directory/'

html = urlopen(directory_url).read()
option_source = html[html.index('<form'):html.index('</form')]
option_re = re.compile('<option.*</option>')
option_list = option_re.findall(option_source)
for option in option_list:
    print option
