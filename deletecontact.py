import cgi

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.alt.appengine
import gdata.spreadsheet
import atom
import gdata.urlfetch
# Use urlfetch instead of httplib
gdata.service.http_request_handler = gdata.urlfetch
import getopt
import sys
import string
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template

class DeleteContactData:

  def __init__(self, email, password, index):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.gd_client.source = 'Spreadsheets GData Sample'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = ''
    self.curr_wksht_id = ''
    self.list_feed = None
    self.spreadsheet = 'Contacts'
    self.worksheet = 'Phone'
    self.index = index

  def Run(self):
    self._ProcessSpreadsheet()
    self._ProcessWorksheet()
    result = self._ListDeleteAction()
    return result

  def _ProcessSpreadsheet(self):
    # Get the list of spreadsheets
    feed = self.gd_client.GetSpreadsheetsFeed()
    for i, entry in enumerate(feed.entry):
	if (entry.title.text == self.spreadsheet):
		id_parts = feed.entry[i].id.text.split('/')
    		self.curr_key = id_parts[len(id_parts) - 1]
  
  def _ProcessWorksheet(self):
    # Get the list of worksheets
    feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
    for i, entry in enumerate(feed.entry):
	if(entry.title.text == self.worksheet):
		id_parts = feed.entry[i].id.text.split('/')
    		self.curr_wksht_id = id_parts[len(id_parts) - 1]
        
  def _ListDeleteAction(self):
    self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
    self.gd_client.DeleteRow(self.list_feed.entry[string.atoi(self.index)])
    print 'Deleted!'
	     
  def _InvalidCommandError(self, input):
    print 'Invalid input: %s\n' % (input)


class DeleteContact(webapp.RequestHandler):
  def get(self):
    
    username = self.request.get("un")
    password = self.request.get("pw")
    index = self.request.get("index")
    prog = DeleteContactData(username, password, index)
    result = prog.Run()
    self.response.out.write(result);
