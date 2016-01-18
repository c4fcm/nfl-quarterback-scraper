import requests, sys, logging, json, csv, collections
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
	# grab the basic info from the qb page
	qb_url = "http://en.wikipedia.org"+qb_link['href']
	qb_doc = BeautifulSoup(fetch_webpage_text(qb_url), BS_PARSER)
	qb_table = qb_doc.find('table',{ "class" : "vcard" })
	qb_img_url = ''	# try to grab the qb pic too
	if qb_table.find('img'):
		qb_img_url = qb_table.find('img')['src']
	qb_nfl_url = '' # try to grab their nfl page url
	for link in qb_table.find_all('a'):
		if link.has_attr('href'):
			if 'nfl.com' in link['href']:
				qb_nfl_url = link['href']
	stats = collections.OrderedDict()
	stats['division']=division
	stats['team']=team_name
	stats['team_wikipedia_url']=team_link
	stats['qb_name']=qb_link.text
	stats['qb_wikipedia_url']=qb_url
	stats['qb_image_url']='http:'+qb_img_url
	stats['qb_nfl_url']=qb_nfl_url
	# grab some details from their nfl page
	if len(qb_nfl_url)>0:
		qb_nfl_doc = BeautifulSoup(fetch_webpage_text(qb_nfl_url), BS_PARSER)
		latest_year_stats = qb_nfl_doc.find_all('table')[1].find_all('tr')[3].find_all('td')
		stats['games'] = latest_year_stats[2].text
		stats['games_started'] = latest_year_stats[3].text.strip()
		stats['completions'] = latest_year_stats[4].text
		stats['attempts'] = latest_year_stats[5].text
		stats['completion_pct'] = latest_year_stats[6].text
		stats['passing_yards'] = latest_year_stats[7].text
		stats['passing_avg_yards'] = latest_year_stats[8].text
		stats['passing_tds'] = latest_year_stats[9].text
		stats['interceptions'] = latest_year_stats[10].text
		stats['sacks'] = latest_year_stats[11].text
		stats['sack_yards'] = latest_year_stats[12].text
		stats['rating'] = latest_year_stats[13].text
		stats['rushing_attempts'] = latest_year_stats[14].text
		stats['rushing_yards'] = latest_year_stats[15].text
		stats['rusing_avg_yards'] = latest_year_stats[16].text
		stats['rusing_tds'] = latest_year_stats[17].text
		stats['fumbles'] = latest_year_stats[18].text
		stats['fumbles_lost'] = latest_year_stats[19].text
	else:
		logging.warning("    - no nfl url :-(")
	# stitch it all together and save
	starting_quarterbacks.append( stats )

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
	cols = starting_quarterbacks[0].keys()
	writer.writerow(cols)
	for qb in starting_quarterbacks:
		info = []
		for col_name in cols:
			if col_name in qb:
				info.append(qb[col_name])
			else:
				info.append("")
		writer.writerow(info)