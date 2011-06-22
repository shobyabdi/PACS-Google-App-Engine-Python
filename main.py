from google.appengine.ext import webapp
from google.appengine.ext.webapp import RequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from mycontacts import ContactsSpreadsheetXML
from addcontact import AddContact
from updatecontact import UpdateContact
from deletecontact import DeleteContact
from createspreadsheet import CreateSpreadsheet


class RedirectToHomeHandler(RequestHandler):
	def get(self):
		self.redirect('/static/home.html')
	
application = webapp.WSGIApplication([('/', RedirectToHomeHandler),
                                      ('/allcontacts', ContactsSpreadsheetXML),
				      ('/addcontact', AddContact),
				      ('/updatecontact', UpdateContact),
				      ('/deletecontact', DeleteContact),
                                      ('/createspreadsheet', CreateSpreadsheet),
                                      ],
                                      debug=True)
run_wsgi_app(application)
