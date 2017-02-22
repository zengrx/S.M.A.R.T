#!/usr/bin/python2
#-*-coding:utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import re, urllib2, sqlite3
# import sys  
# reload(sys)  
# sys.setdefaultencoding('utf8')


'''
description: test insert into selite database
date: 2016.3.20
'''


def geturl(db_name):
	#database name

	try:
		sqlite_conn = sqlite3.connect(db_name)
	except sqlite3.Error, e:
		print "sqlite connect failed", "\n", e.args[0]
	
	sqlite_cursor = sqlite_conn.cursor()

	sqlite_cursor.execute("insert into base_info (id, name, path) values(10, 'a', 'b')")
		
	sqlite_conn.commit()
	sqlite_conn.close()

	print "write data success"

geturl('fileinfo.db')

