#!/usr/bin/env python3

import os, re
from functools import reduce

from urllib.request import urlopen
from collections import defaultdict
from bs4 import BeautifulSoup

iconsets = [
	('Breeze',  defaultdict(list), 'plasma-next-icons/Breeze'),
	('Adwaita', defaultdict(list), 'adwaita-icon-theme/Adwaita'),
	('Adwaita-symbolic', defaultdict(list), 'adwaita-icon-theme/Adwaita'),
]

def key(d):
	s = re.search(r'(\d+)x\d+', d)
	if s:
		return int(s.group(1))
	else:
		return d

sym_re = re.compile(r'([\w+-]+)-symbolic((?:-rtl)?)\.\w+')

for set_name, icons, direc in iconsets:
	for root, dirs, files in os.walk(direc):
		for name in files:
			if not (name.endswith('.svg') or name.endswith('.png')):
				continue
			if key(root) == 256:
				continue
			sym_match = sym_re.fullmatch(name)
			if set_name.endswith('-symbolic') != bool(sym_match):
				continue
			
			if sym_match is not None:
				sname = ''.join(sym_match.group(1, 2))
			else:
				sname = name[:-len('.svg')]
			
			path = os.path.relpath(os.path.realpath(os.path.join(root, name)), os.getcwd())
			icons[sname].append(path)
			icons[sname].sort(key=key)

with urlopen('http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html') as r:
	soup = BeautifulSoup(r, 'html5lib')

standard_icons = set()
for table in soup.find_all('table'):
	for name, _, _ in iconsets:
		table.colgroup.insert(0, soup.new_tag('col'))
		
		header = soup.new_tag('td')
		header.string = name
		table.thead.tr.insert(0, header)
	
	for row in table.tbody.find_all('tr'):
		icon = row.td.string
		standard_icons.add(icon)
		
		for _, icons, _ in iconsets:
			td  = soup.new_tag('td')
			for i in icons[icon]:
				td.append(soup.new_tag('img', src=i))
			
			row.insert(0, td)

nonstandard_icons = set()
for _, urls, _ in iconsets:
	nonstandard_icons |= set(urls.keys()) - standard_icons

h2 = soup.new_tag('h2')
h2.string = 'Nonstandard icons'
soup.append(h2)

t = soup.new_tag('table')
for icon in sorted(nonstandard_icons):
	tr = soup.new_tag('tr')
	for _, iconset, _ in iconsets:
		td = soup.new_tag('td')
		for i in iconset[icon]:
			td.append(soup.new_tag('img', src=i))
		tr.insert(0, td)
	
	td = soup.new_tag('td')
	td.string = icon
	tr.append(td)
	
	t.append(tr)

soup.append(t)

with open('index.html', 'w') as f:
	f.write(soup.prettify())
