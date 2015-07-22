import os, re
import requests
from collections import defaultdict
from bs4 import BeautifulSoup

breeze_urls = defaultdict(list)
adwaita_urls = defaultdict(list)

def key(d):
	s = re.search(r'(\d+)x\d+', d)
	if s:
		return int(s.group(1))
	else:
		return d

for dicti, direc in [
	(breeze_urls,  'plasma-next-icons/Breeze'),
	(adwaita_urls, 'adwaita-icon-theme/Adwaita'),
]:
	for root, dirs, files in os.walk(direc):
		for name in files:
			if name.endswith('.svg') or name.endswith('.png'):
				if not key(root) == 256:
					path = os.path.relpath(os.path.realpath(os.path.join(root, name)), os.getcwd())
					dicti[name[:-4]].append(path)
					dicti[name[:-4]].sort(key=key)

r = requests.get('http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html', stream=True)
soup = BeautifulSoup(r.raw, 'html5lib')

for table in soup.find_all('table'):
	table.colgroup.insert(0, soup.new_tag('col'))
	table.colgroup.insert(0, soup.new_tag('col'))
	
	table.thead.tr.insert(0, soup.new_tag('td'))
	table.thead.tr.insert(0, soup.new_tag('td'))
	
	for row in table.tbody.find_all('tr'):
		icon = row.td.string
		
		breeze_td  = soup.new_tag('td')
		adwaita_td = soup.new_tag('td')
		for i in breeze_urls[icon]:
			breeze_td .append(soup.new_tag('img', src=i))
		for i in adwaita_urls[icon]:
			adwaita_td.append(soup.new_tag('img', src=i))
		
		row.insert(0, breeze_td)
		row.insert(0, adwaita_td)

with open('index.html', 'w') as f:
	f.write(soup.prettify())