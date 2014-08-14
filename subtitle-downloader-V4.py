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
import hashlib
import urlparse


#this hash function receives the name of the file and returns the hash code
def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()


for root, dirs, files in os.walk(os.getcwd()):
	for f in files:
		if f.endswith('.mkv') or f.endswith('.avi') or f.endswith('.3gp') or f.endswith('.mp4') or f.endswith('.flv') or f.endswith('.wmv') or f.endswith('.mov') or f.endswith('.mpg'):
			fileName, fileExtension = os.path.splitext(f)

			if fileName+".srt" in files:
				continue

			print "Processing for "+fileName

			try:
				user_agent = 'SubDB/1.0 (subtitle_downloader_v2/1.0; https://github.com/eh2arch/subtitle_downloader_v2)'
				headers={'User-Agent':user_agent}
				url = 'http://api.thesubdb.com/?action=download&language=en'
				request = urllib2.Request(url+'&hash='+get_hash(root+os.sep+f),None,headers)
				response_whole = urllib2.urlopen(request)
				response = response_whole.read()
				if len(response) > 0 :
					sub = open (root+os.sep+fileName + ".srt","wb")
					sub.write(response)
					continue
			except:
				q=2
			query = fileName.lower().replace(".", " ").replace("-"," ").replace("_"," ").replace("[", " ").replace("]", " ").replace("bluray","").replace("x264","").replace("yify","").replace("1080p","").replace("720p","").replace("axxo","").replace("xvid","").replace("bdrip","").replace("brrip","").replace("aac-vision","").replace("aac","").replace("dvdscr","").replace("scr","").replace("dvdrip","").replace("camrip","").replace("hdtv","").replace("1cd","").replace("mp3","").replace("audio","").replace("hindi","").replace("dual","").replace("subs","")
			query = ' '.join(query.split()[0:5])

			user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
			headers={'User-Agent':user_agent}
			url = "https://google.co.in/search?"

			query = ' '.join(query.split())

			query_url = urllib.urlencode( {'q' : query } )

			request = urllib2.Request(url+query_url,None,headers)

			try:

				response = urllib2.urlopen(request).read()

			except:
				print "Failed to get subtitles for movie"
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
				download_title = query

			download_title = download_title.replace('(film)','')

			query = "\"" + download_title + '\" site:subscene.com'

			query = urllib.urlencode( {'q' : query } )

			request = urllib2.Request(url+query,None,headers)

			try:

				response = urllib2.urlopen(request).read()
			except:
				print "Failed to get subtitles for movie"
				continue

			download_url = ''

			try:
				soup = BeautifulSoup(response,'html.parser')
				for child in soup.find_all("cite"):
					movie_link = child.get_text()
					if (not re.search('\.{3}',movie_link)) and re.search('english\/\d*$',movie_link):
						download_url = 'http://'+movie_link
						break
				if download_url == '':
					for child in soup.find_all("h3",attrs={'class':'r'}):
						google_url = "https://google.com" + child.a['href']
						movie_link = urlparse.parse_qs(urlparse.urlparse(google_url).query)['q'][0]
						if (not re.search('\.{3}',movie_link)) and re.search('english\/\d*',movie_link):
							download_url = movie_link
							break

			except:
				print "Failed to get subtitles for movie"
				continue

			if download_url == '':
				print "Failed to get subtitles for movie"
				continue


			try:
				website=urllib2.urlopen(download_url)
				html=website.read()
				soup = BeautifulSoup(html,'html.parser')
				for child in soup.find_all('div',attrs={'class':"download"}):
					get_url='http://subscene.com'+child.a['href']
					break
				urllib.urlretrieve (get_url, "subtitle.rar")
				current_path = os.getcwd()
				q=''
				if zipfile.is_zipfile('subtitle.rar')==True:
					zfile = zipfile.ZipFile('subtitle.rar')
					for z in zfile.namelist():
						zfile.extract(z,root)
						q=z
				else:
					rf = rarfile.RarFile('subtitle.rar')
					for f in rf.infolist():
						rf.extract(f,root)
						q=f.filename
				os.rename(root+os.sep+q,root+os.sep+fileName+'.srt')
				os.remove('subtitle.rar',current_path)
			except:
				continue
			print "Subtitles downloaded and renamed."
print "Enjoy!"