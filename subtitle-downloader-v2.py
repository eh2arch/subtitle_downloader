#! /usr/bin/python
import urllib2
import urllib
import re
from bs4 import BeautifulSoup
import json
import webbrowser
import zipfile
import rarfile
import os.path
import os

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
	if f.endswith('.mkv') or f.endswith('.avi') or f.endswith('.3gp') or f.endswith('.mp4') or f.endswith('.flv') or f.endswith('.wmv') or f.endswith('.mov') or f.endswith('.mpg'):
		fileName, fileExtension = os.path.splitext(f)

		if fileName+".srt" in files:
			continue

		query = fileName.replace(".", " ").replace("BluRay","").replace("x264","").replace("YIFY","").replace("1080p","").replace("720p","").replace("BrRip","").replace("BRRip","").replace("AAC-ViSiON","").replace("AAC","").replace("DVDSCR","").replace("SCR","").replace("DVDRIP","").replace("CAMPRIP","").replace("HDTV","").replace("1CD","")

		user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
		headers={'User-Agent':user_agent}
		url = "https://google.co.in/search?"

		query = ' '.join(query.split())

		query = urllib.urlencode( {'q' : query } )

		request = urllib2.Request(url+query,None,headers)

		try:

			response = urllib2.urlopen(request).read()

		except:
			continue

		download_title = ''

		try:

			soup = BeautifulSoup(response,'html.parser')
			for child in soup.find_all("h3",attrs={'class':"r"}):
				title = child.a.get_text()
				if download_title == '':
					download_title = title
				if title.endswith('- IMDb'):
					download_title = title.replace('- IMDb','')
					break
				elif title.endswith('- Wikipedia, the free encyclopedia'):
					download_title = title.replace('- Wikipedia, the free encyclopedia','')
					break
		except:
			continue

		query = "\"" + download_title + '\" site:subscene.com'

		query = urllib.urlencode( {'q' : query } )

		request = urllib2.Request(url+query,None,headers)

		try:

			response = urllib2.urlopen(request).read()
		except:
			continue

		download_url = ''

		try:
			soup = BeautifulSoup(response,'html.parser')
			for child in soup.find_all("cite"):
				movie_link = child.get_text()
				if re.search('english\/',movie_link):
					download_url = movie_link
					break
		except:
			continue

		if download_url == '':
			continue


		try:
			website=urllib2.urlopen('http://'+download_url)
			html=website.read()
			soup = BeautifulSoup(html,'html.parser')
			for child in soup.find_all('div',attrs={'class':"download"}):
				get_url='http://subscene.com'+child.a['href']
				break
			urllib.urlretrieve (get_url, "subtitle")
			current_path = os.getcwd()
			q=''
			if zipfile.is_zipfile('subtitle')==True:
				zfile = zipfile.ZipFile('subtitle')
				for z in zfile.namelist():
					zfile.extract(z,current_path)
					q=z
			else:
				rf = rarfile.RarFile('subtitle')
				for f in rf.infolist():
				    rf.extract(f,current_path)
				    q=f.filename
			os.rename(q,fileName+'.srt')
			os.remove('subtitle',current_path)
		except:
			continue
