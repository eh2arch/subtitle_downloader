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
	if f.endswith('.mkv') or f.endswith('.avi') or f.endswith('.3gp') or f.endswith('.mp4') or f.endswith('.flv'):
		fileName, fileExtension = os.path.splitext(f)
		
		if fileName+".srt" in files:
			continue
		else:
			print f
		query = fileName.replace(".", " ").replace("BluRay","").replace("x264","").replace("YIFY","").replace("720p","").replace("BrRip","").replace("BRRip","").replace("AAC-ViSiON","").replace("AAC","").replace("DVDSCR","").replace("DVDRIP","").replace("CAMPRIP","")
		
		query = ' '.join(query.split())

		query = urllib.urlencode( {'q' : query } )
	
		url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&"
		
		response = urllib2.urlopen (url + query ).read()

		data = json.loads ( response )

		print data 

		results = data [ 'responseData' ] [ 'results' ]

		download_title = ''
		for result in results:
		    if 'titleNoFormatting' in result:
			    title = result['titleNoFormatting']
			    if title.endswith('- IMDb'):
				download_title = title.replace('- IMDb','')
				break
			    elif title.endswith('- Wikipedia, the free encyclopedia'):
				download_title = title.replace('- Wikipedia, the free encyclopedia','')
				break

		print download_title + "\n\n\n\n"

		query = "\"" + download_title + '\" site:subscene.com'

		query = urllib.urlencode( {'q' : query } )

		response = urllib2.urlopen (url + query ).read()

		data = json.loads ( response )

		results = data [ 'responseData' ] [ 'results' ]

		download_url = ''

		for result in results:
		    if 'url' in result:
			    url = result['url']
			    if re.search('english',url):
				download_url = url
				break
		if download_url == '':
			continue

		print download_url + "\n\n\n\n\n"

		website=urllib2.urlopen(download_url)
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
