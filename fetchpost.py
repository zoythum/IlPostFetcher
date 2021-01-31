# getting the data
import requests
from urllib.request import urlopen
from lxml import etree

from rich.console import Console
from rich.table import Column, Table
import os
import datetime
import json


def generate_tables():
	url = 'https://www.ilpost.it'
	headers = {'Content-Type': 'text/html',}
	response = requests.get(url, headers=headers)
	html = response.text

	cwd = os.getcwd()

	with open(cwd + '/post_html', 'w') as f:
	    f.write(html)

	response = urlopen('file://' + cwd + '/post_html')
	htmlparser = etree.HTMLParser()
	tree = etree.parse(response, htmlparser)

	flashes = tree.xpath('//div[starts-with(@class, "widget flashes_hp")]//li//h6/text()')
	flashes_links = tree.xpath('//div[starts-with(@class, "widget flashes_hp")]//li//a/@href')
	articles_titles = tree.xpath('//article//div[@class="entry-content"]//h2/a/text()')[:5]
	articles_links = tree.xpath('//article//p/a/@href')[:5]
	articles_content = tree.xpath('//article//p/a/@title')[:5]


	console = Console()
	flash_table = Table(show_header=True, header_style="bold red")
	flash_table.add_column("Flashes")
	for index in range(len(flashes)):
		flash_table.add_row("[link={}]{}[/link]".format(flashes_links[index], flashes[index]))

	console.print(flash_table)

	articles_table = Table(show_header=True, header_style="bold red")
	articles_table.add_column("Title")
	articles_table.add_column("Content")


	for index in range(len(articles_titles)):
		articles_table.add_row("[link={}]{}[/link]".format(articles_links[index], articles_titles[index]), articles_content[index])

	console.print(articles_table)

	os.remove(cwd + "/post_html")

def should_fetch(delta, lastfetch):
	try:
		
		lastime = datetime.datetime.strptime(lastfetch, '%Y-%m-%d %H:%M:%S.%f')
		current = datetime.datetime.now()
		
		diff = current-lastime

		if ((diff.total_seconds()//3600) > delta):
			return True
		else:
			return False

	except ValueError:
		return True
	

def main():
	with open("settings.json", "r") as f:
		data = json.load(f)

	if should_fetch(data['timedelta'], data['lastfetch']):
		generate_tables()
		data['lastfetch'] = str(datetime.datetime.now())
		with open("settings.json", "w") as f:
			json.dump(data, f)


if __name__ == '__main__':
	main()