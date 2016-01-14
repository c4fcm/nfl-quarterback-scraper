import requests, sys, logging, json, csv
from bs4 import BeautifulSoup
import cache

BS_PARSER = "html.parser"

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def fetch_webpage_text(url,use_cache=True):
	if use_cache and cache.contains(url):
		return cache.get(url)
	# cache miss, download it
	content = requests.get(url).text
	cache.put(url,content)
	return content

def add_qb(qb_link, division, team_name, team_link):
	logging.info("  "+qb_link.text)
	# try to grab the qb pic too
	qb_url = "http://en.wikipedia.org"+qb_link['href']
	qb_doc = BeautifulSoup(fetch_webpage_text(qb_url), BS_PARSER)
	qb_table = qb_doc.find('table')
	qb_img_url = ''
	if qb_table.find('img'):
		qb_img_url = qb_table.find('img')['src']
	qb_info = {
		'division': division,
		'team': team_name,
		'team_wikipedia_url': team_link,
		'qb_name': qb_link.text,
		'qb_wikipedia_url': qb_url,
		'qb_image_url': 'http:'+qb_img_url
	}
	starting_quarterbacks.append( qb_info )

# load the starting QB list and process it team by team
wikipedia_list_url = 'http://en.wikipedia.org/wiki/List_of_NFL_starting_quarterbacks'
doc = BeautifulSoup(fetch_webpage_text(wikipedia_list_url),BS_PARSER)
starting_quarterbacks = []
table = doc.findAll('table')[0]
for team_row in table.findAll('tr')[1:]:
	#logging.debug(team_row)
	team_columns = team_row.findAll('td')
	division = team_columns[0].text
	team_name = team_columns[1].findAll('a')[0].text
	team_link = "http://en.wikipedia.org"+team_columns[1].findAll('a')[0]['href']
	team_qb_list_link = "http://en.wikipedia.org"+team_columns[1].findAll('a')[1]['href']
	logging.info("Team: "+team_name)
	# grab the team page to get all starting qbs
	found_qb = False
	team_doc = BeautifulSoup(fetch_webpage_text(team_qb_list_link),BS_PARSER)
	table_index = 0
	if team_name in ['St. Louis Rams', 'Cleveland Browns', 'Indianapolis Colts', \
					 'Miami Dolphins', 'Minnesota Vikings']:
		table_index=1
	season_rows = team_doc.findAll('table')[table_index].findAll('tr')
	for season_row in season_rows:
		season_columns = season_row.findAll('td')
		if len(season_columns)<2:
			continue
		season_col_index = 0
		qb_col_index = 1
		if team_name in ['Oakland Raiders']:
			season_col_index = 1
			qb_col_index = 2
		if season_columns[season_col_index].text!='2015':
			continue
		# found the right row - now parse it
		for qb_link in season_columns[qb_col_index].findAll('a'):
			add_qb(qb_link, division, team_name, team_link)
			found_qb = True
		break
	if not found_qb:
		# use the one from the main list of starting qbs
		qb_link = team_columns[2].find('a')
		add_qb(qb_link, division, team_name, team_link)
	
with open("qb_list.json", "w") as json_file:
    json_file.write( json.dumps(starting_quarterbacks, indent=2) )

with open("qb_list.csv", "w") as csv_file:
	writer = csv.writer(csv_file)
	cols = ['division','team','team_wikipedia_url','qb_name','qb_wikipedia_url','qb_image_url']
	writer.writerow(cols)
	for qb in starting_quarterbacks:
		info = []
		for col_name in cols:
			info.append(qb[col_name])
		writer.writerow(info)