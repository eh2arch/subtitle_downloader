#! /usr/bin/python
from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as Queue
import threading
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
import uuid
import sys

#This hash function receives the name of the file and returns the hash code
def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()

def explore_path(path):
	directories = []
	nondirectories = []
	for filename in os.listdir(path):
		fullname = os.path.join(path, filename)
		if os.path.isdir(fullname):
			directories.append(fullname)
		else:
			if filename.endswith(('.mkv', '.avi', '.3gp', '.mp4', '.flv', '.wmv', '.mov', '.mpg')) and os.path.splitext(filename)[0] + ".srt" not in os.listdir(path):
				nondirectories.append([filename, path])
	if nondirectories:
		map(lambda x: files_to_process.put(x), nondirectories)
	return directories

def parallel_worker():
    while True:
        path = unsearched.get()
        dirs = explore_path(path)
        for newdir in dirs:
            unsearched.put(newdir)
        unsearched.task_done()

def get_html_response(user_agent, request_url):
	headers = {'User-Agent':user_agent}
	return urllib2.urlopen(urllib2.Request(request_url, None, headers)).read()

def do_subtitle_magic(queue):
	while True:
		f, path = queue.get()
		try:
			fileName, fileExtension = os.path.splitext(f)
			files = os.listdir(path)
			if fileName + ".srt" in files:
				continue
			print "Processing for " + fileName
			try:
				user_agent = 'SubDB/1.0 (subtitle_downloader_v2/1.0; https://github.com/eh2arch/subtitle_downloader_v2)'
				url = 'http://api.thesubdb.com/?action=download&language=en'
				response = get_html_response(user_agent, url+'&hash='+get_hash(path+os.sep+f))
				if len(response) > 0 :
					sub = open (path+os.sep+fileName + ".srt","wb")
					sub.write(response)
					print "Subtitles downloaded for " + fileName
					continue
			except:
				pass
			mapping = [(".", " "), ("-"," "), ("_"," "), ("[", " "), ("]", " "), ("bluray",""), ("x264",""), ("yify",""), ("1080p",""), ("720p",""), ("axxo",""), ("xvid",""), ("bdrip",""), ("brrip",""), ("aac-vision",""), ("aac",""), ("dvdscr",""), ("scr",""), ("dvdrip",""), ("camrip",""), ("hdtv",""), ("1cd",""), ("mp3",""), ("audio",""), ("hindi",""), ("dual",""), ("subs","")]
			query = fileName.lower()
			for k, v in mapping:
				query = query.replace(k, v)
			query = ' '.join(query.split()[0:5])
			user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
			url = "https://google.co.in/search?"
			query = ' '.join(query.split())
			query_url = urllib.urlencode( {'q' : query } )
			try:
				response = get_html_response(user_agent, url + query_url)
			except:
				print "Failed to get subtitles for " + fileName
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
			try:
				response = get_html_response(user_agent, url + query)
			except:
				print "Failed to get subtitles for " + fileName
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
				print "Failed to get subtitles for " + fileName
				continue

			if download_url == '':
				print "Failed to get subtitles for " + fileName
				continue
			try:
				response=urllib2.urlopen(download_url).read()
				soup = BeautifulSoup(response,'html.parser')
				for child in soup.find_all('div',attrs={'class':"download"}):
					get_url='http://subscene.com'+child.a['href']
					break
				unique_filename = str(uuid.uuid4()) + ".rar"
				urllib.urlretrieve (get_url, unique_filename)
				current_path = os.getcwd()
				q=''
				if zipfile.is_zipfile(unique_filename)==True:
					zfile = zipfile.ZipFile(unique_filename)
					for z in zfile.namelist():
						zfile.extract(z,path)
						q=z
				else:
					rf = rarfile.RarFile(unique_filename)
					for f in rf.infolist():
						rf.extract(f,path)
						q=f.filename
				os.rename(path+os.sep+q,path+os.sep+fileName+'.srt')
				print "Subtitles downloaded for " + fileName
				try:
					os.remove(current_path + os.sep + unique_filename)
				except:
					pass
			except:
				continue
		finally:
			queue.task_done()

if __name__ == "__main__":
	if len(sys.argv) == 1:
		paths = [os.getcwd()]
	else:
		paths = sys.argv[1:]
	unsearched = Queue()
	files_to_process = Queue(maxsize=0)
	map(lambda x: unsearched.put(x), paths)
	pool = Pool(5)
	for i in range(5):
	    pool.apply_async(parallel_worker)
	num_threads = 10
	for i in range(num_threads):
		worker = threading.Thread(target=do_subtitle_magic, args=(files_to_process,))
		worker.setDaemon(True)
		worker.start()
	unsearched.join()
	files_to_process.join()
	print "Enjoy!"