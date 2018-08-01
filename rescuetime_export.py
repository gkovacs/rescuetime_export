#!/usr/bin/env python
# md5: 444984cc01980f8d4d447753a6bfd1f1
# coding: utf-8



try:
  import ujson as json
except:
  import json
import yaml
from pymongo import MongoClient
from urllib import urlopen
import os
from urlparse import urlparse

secrets = yaml.load(open('.getsecret.yaml'))
mongouri = secrets['MONGODB_URI']
dbname = secrets['MONGODB_DBNAME']
rescuetime_url = secrets['rescuetime_url']
# heroku tmisurvey
client = MongoClient(mongouri)
#client = MongoClient()

#db = client.default
db = client[dbname]

category_collection = db.category
productivity_collection = db.productivity
docactivity_collection = db.docactivity



def getval(collection, key):
  val = collection.find_one(key)
  if val == None:
    return None
  return val['val']

def setval(collection, key, val):
  collection.update_one({'_id': key}, {'$set': {'val': val}}, upsert=True)

def getval_category(key):
  return getval(category_collection, key)

def setval_category(key, val):
  setval(category_collection, key, val)

def getval_productivity(key):
  return getval(productivity_collection, key)

def setval_productivity(key, val):
  setval(productivity_collection, key, val)

def get_key_set():
  output = set()
  for x in productivity_collection.find():
    output.add(x['_id'])
  return output



#all_categories = set()

#for x in category_collection.find():
#  all_categories.add(x['val'])

#print all_categories



#print get_key_set()



#for x in category_collection.find():
#  print x['_id']

#print setval_category('something.foo.with.a.period', 'sdfjkl')
#print getval_category('something.foo.with.a.period')



import threading

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t



all_domains = set(json.load(open('domains.json')))



#print len(all_domains)



#print dir(category_collection)



#print len(urlparse('The New York Times').netloc)




def to_dict(data):
  output = []
  rows = data['rows']
  row_headers = data['row_headers']
  for row in rows:
    output.append({row_headers[i]: x for i,x in enumerate(row)})
  return output

def check_rescuetime():
  print '============================'
  print 'check_rescuetime'
  print '============================'
  data_text = urlopen(rescuetime_url).read()
  data = json.loads(data_text)
  lines = to_dict(data)
  category_bulk = category_collection.initialize_unordered_bulk_op()
  productivity_bulk = productivity_collection.initialize_unordered_bulk_op()
  docactivity_bulk = docactivity_collection.initialize_unordered_bulk_op()
  for line in lines:
    activity = line['Activity']
    if activity.startswith('mobile - '):
      activity = activity[len('mobile - '):]
    new_activity = True
    if activity in seen_domains:
      new_activity = False
    category = line['Category']
    productivity = line['Productivity']
    if new_activity:
      category_bulk.find({'_id': activity}).upsert().update_one({'$set': {'val': category}})
      productivity_bulk.find({'_id': activity}).upsert().update_one({'$set': {'val': productivity}})
      seen_domains.add(activity)
    document = line['Document']
    if not document or document == 'No Details':
      continue
    if not document.startswith('http'):
      document = 'http://' + document
    document_domain = urlparse(document).netloc
    #print document_domain
    if document_domain in seen_domains:
      continue
    if not document_domain:
      continue
    if document_domain == activity:
      continue
    category_bulk.find({'_id': document_domain}).upsert().update_one({'$set': {'val': category}})
    productivity_bulk.find({'_id': document_domain}).upsert().update_one({'$set': {'val': productivity}})
    docactivity_bulk.find({'_id': document_domain}).upsert().update_one({'$set': {'val': activity}})
    seen_domains.add(document_domain)
  try:
    category_bulk.execute()
  except:
    pass
  try:
    productivity_bulk.execute()
  except:
    pass
  try:
    docactivity_bulk.execute()
  except:
    pass



#set_interval(check_rescuetime, 2+60*3)
#set_interval(check_rescuetime, 10)



seen_domains = set()

def set_seen_domains():
  print '++++++++++++++++++++++++++++'
  print 'set_seen_domains'
  print '++++++++++++++++++++++++++++'
  global seen_domains
  global all_domains
  seen_domains = get_key_set()

  for x in ['']:
    if x in all_domains:
      all_domains.remove(x)

  for x in seen_domains:
    if x in all_domains:
      all_domains.remove(x)
    wx = 'www.' + x
    if wx in all_domains:
      all_domains.remove(wx)

set_seen_domains()



#check_rescuetime()
#seen_domains = set()
#set_seen_domains()
#print seen_domains



#print len(seen_domains)
#print len(all_domains)
#print all_domains



#for x in all_domains:


#print apidock



#check_rescuetime()



#print seen_domains



#print all_domains



import random

def shuffled(l):
  l = l[:]
  random.shuffle(l)
  return l



import pyautogui
import time
import webbrowser

# google chrome version
'''
last_check_rescuetime = 0
last_update_seen_domains = time.time()
open_tabs = 0
while len(all_domains) > 0:
  for domain in shuffled(list(all_domains)):
    try:
      if time.time() > last_check_rescuetime + 125:
        last_check_rescuetime = time.time()
        check_rescuetime()
      if time.time() > last_update_seen_domains + 2000:
        last_update_seen_domains = time.time()
        set_seen_domains()
      if domain in seen_domains:
        if domain in all_domains:
          all_domains.remove(domain)
        continue
      if domain.startswith('www.'):
        no_www_domain = domain[4:]
        if no_www_domain in seen_domains:
          if domain in all_domains:
            all_domains.remove(domain)
          if no_www_domain in all_domains:
            all_domains.remove(no_www_domain)
          continue
      #print domain
      webbrowser.open_new_tab('http://' + domain)
      time.sleep(1)
      open_tabs += 1
      if open_tabs >= 20:
        #pyautogui.hotkey('command', '1')
        #pyautogui.hotkey('ctrlleft', '1')
        time.sleep(1)
        #pyautogui.hotkey('ctrlleft', 'q')
        if os.name == 'nt':
          pyautogui.hotkey('altleft', 'f4')
        else:
          pyautogui.hotkey('command', 'q')
        time.sleep(1)
        pyautogui.hotkey('left')
        time.sleep(0.1)
        pyautogui.hotkey('enter')
        webbrowser.open_new_tab('http://www.google.com')
        #pyautogui.hotkey('ctrlleft', 'shift', 'e')
        time.sleep(3)
        open_tabs = 0
    except:
      pass
'''



# firefox version
last_check_rescuetime = 0
last_update_seen_domains = time.time()
open_tabs = 0
num_closes = 0
while len(all_domains) > 0:
  for domain in shuffled(list(all_domains)):
    try:
      if time.time() > last_check_rescuetime + 125:
        last_check_rescuetime = time.time()
        check_rescuetime()
      if time.time() > last_update_seen_domains + 2000:
        last_update_seen_domains = time.time()
        set_seen_domains()
      if domain in seen_domains:
        if domain in all_domains:
          all_domains.remove(domain)
        continue
      if domain.startswith('www.'):
        no_www_domain = domain[4:]
        if no_www_domain in seen_domains:
          if domain in all_domains:
            all_domains.remove(domain)
          if no_www_domain in all_domains:
            all_domains.remove(no_www_domain)
          continue
      #print domain
      webbrowser.open_new_tab('http://' + domain)
      time.sleep(1)
      open_tabs += 1
      tab_limit = 20
      if os.name == 'nt':
        tab_limit = 7
      if open_tabs >= tab_limit:
        #pyautogui.hotkey('command', '1')
        #pyautogui.hotkey('ctrlleft', '1')
        time.sleep(2)
        #pyautogui.hotkey('ctrlleft', 'q')
        if os.name == 'nt':
          time.sleep(2)
          pyautogui.hotkey('ctrl', 'shiftleft', 'f4')
          time.sleep(2)
        else:
          pyautogui.hotkey('command', 'shiftleft', 'f4')
        time.sleep(2)
        open_tabs = 0
        num_closes += 1
        if num_closes >= 3:
          if os.name == 'nt':
            pyautogui.hotkey('altleft', 'f4')
            time.sleep(2)
            pyautogui.hotkey('enter')
          else:
            pyautogui.hotkey('command', 'q')
            time.sleep(2)
            pyautogui.hotkey('enter')
          time.sleep(4)
          webbrowser.open_new_tab('http://www.google.com')
          time.sleep(4)
          num_closes = 0
    except:
      pass



#def print_hello():
#  print 'hello world'

#set_interval(print_hello, 10)




#rows = data['rows']
#row_headers = data['row_headers']
#print row_headers
#print to_dict(data)
#for line in to_dict(data):
#  print line['Activity'], line['Category'], line['Productivity']
#print rows[0]



#print setval('foo', 10)
#print getval('foo')
#print getval('bar')

