"""
  ** Author: Rebecca Thompson
  ** Date: 4/30/17
  ** Description: RESTful API for a simple Marina
"""


from google.appengine.ext import ndb
import webapp2
import json


class Boat(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty()
	length = ndb.FloatProperty()
	at_sea = ndb.BooleanProperty(default=True)
	
class Slip(ndb.Model):
	id = ndb.StringProperty()
	number = ndb.IntegerProperty(required=True)
	current_boat = ndb.StringProperty(default=None)
	arrival_date = ndb.StringProperty()

	
class BoatHandler(webapp2.RequestHandler):
	def post(self):
		req = json.loads(self.request.body)

		# One or more fields is invalid
		if 'name' not in req or invalidBoatParams(req):
			self.response.set_status(400)
			self.response.write(self.response.status)
			return
		
		# Create new boat and initialize
		parent_key = ndb.Key(Boat, "parent_boat")
		new_boat = Boat(name=req['name'], parent=parent_key)
		new_boat.put()
		
		new_boat.id = new_boat.key.urlsafe()
		
		# Optional fields
		if 'length' in req:
			new_boat.length = req['length']
		if 'type' in req:
			new_boat.type = req['type']
		
		# Update database
		new_boat.put()
		
		self.response.set_status(201)
		bd = new_boat.to_dict()
		bd['self'] = '/boats/' + new_boat.id
		self.response.write(json.dumps(bd))
		
	def get(self, id=None):
		if id:
			# Attempt to retrieve boat
			boat = getByKey(id)
			
			# Not a valid boat
			if boat is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
		
			# Return boat
			self.response.set_status(200)
			bd = boat.to_dict()
			bd['self'] = '/boats/' + boat.id
			self.response.write(json.dumps(bd))
		else:
			boats = Boat.query().fetch()
			
			boatList = []
			for b in boats:
				newBoat = b.to_dict()
				newBoat['self'] = '/boats/' + newBoat['id']
				boatList.append(newBoat)
			
			self.response.set_status(200)
			self.response.write(json.dumps(boatList))
			
	def patch(self, id=None):
		if id:
			req = json.loads(self.request.body)
			
			# Attempt to retrieve boat
			boat = getByKey(id)
				
			# Not a valid boat
			if boat is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return

			# One or more fields is invalid
			if invalidBoatParams(req):
				self.response.set_status(400)
				self.response.write(self.response.status)
				return
			
			# Input validated, update all provided fields
			if 'length' in req:
				boat.length = req['length']
			if 'name' in req:
				boat.name = req['name']
			if 'type' in req:
				boat.type = req['type']
				
			# Update database
			boat.put()
			
			# Return updated boat to user
			self.response.set_status(200)
			boat_dict = boat.to_dict()
			self.response.write(json.dumps(boat_dict))
		else:
			self.response.set_status(403)
			self.response.write(self.response.status)
			
	def put(self, id=None):
		req = json.loads(self.request.body)
			
		# Attempt to retrieve boat
		boat = getByKey(id)
			
		# Not a valid boat
		if boat is None:
			self.response.set_status(404)
			self.response.write(self.response.status)
			return
		
		# One or more fields is invalid
		if 'name' not in req or invalidBoatParams(req):
			self.response.set_status(400)
			self.response.write(self.response.status)
			return
		
		# Reset to default values
		boat.length = None;
		boat.type = None;
		boat.at_sea = True;
		
		boat.name = req['name']
		
		# Optional fields
		if 'length' in req:
			boat.length = req['length']
		if 'type' in req:
			boat.type = req['type']
			
		# Update database
		boat.put()
			
		# Return updated boat to user
		self.response.set_status(200)
		boat_dict = boat.to_dict()
		self.response.write(json.dumps(boat_dict))
		
	def delete(self, id=None):
		if id:
			boat = getByKey(id)
			
			# Not a valid boat
			if boat is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
		
			# Remove boat from slip
			if not boat.at_sea:
				slip = Slip.query(Slip.current_boat == boat.id).get()
				slip.current_boat = None
				slip.arrival_date = None
				slip.put()
		
			# Delete boat
			ndb.Key(urlsafe=id).delete()
			
			self.response.set_status(204)
			self.response.write(self.response.status)
		else:
			self.response.set_status(403)
			self.response.write(self.response.status)
			
			
class SlipHandler(webapp2.RequestHandler):
	def post(self):
		req = json.loads(self.request.body)
		
		# Check required fields are present and valid
		if 'number' not in req or type(req['number']) is not int:
			self.response.set_status(400)
			self.response.write(self.response.status)
			return
		
		# Create slip
		parent_key = ndb.Key(Slip, "parent_slip")
		new_slip = Slip(number=req['number'], parent=parent_key)
		new_slip.put()
		
		new_slip.id = new_slip.key.urlsafe()
		
		# Update database
		new_slip.put()
		
		self.response.set_status(201)
		sd = new_slip.to_dict()
		sd['self'] = '/slips/' + new_slip.key.urlsafe()
		self.response.write(json.dumps(sd))
		
	def get(self, id=None):
		if id:
			# Attempt to retrieve slip
			slip = getByKey(id)
			
			# Not a valid slip
			if slip is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
		
			# Return slip
			self.response.set_status(200)
			sd = slip.to_dict()
			sd['self'] = '/slips/' + slip.key.urlsafe()
			self.response.write(json.dumps(sd))
		else:
			slips = Slip.query().fetch()
			
			slipList = []
			for s in slips:
				newSlip = s.to_dict()
				newSlip['self'] = '/slips/' + newSlip['id']
				slipList.append(newSlip)
			
			self.response.set_status(200)
			self.response.write(json.dumps(slipList))
			
	def patch(self, id=None):
		if id:
			req = json.loads(self.request.body)
			
			# Attempt to retrieve slip
			slip = getByKey(id)
				
			# Not a valid slip
			if slip is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return

			# Invalid number
			if 'number' in req and type(req['number']) is not int:
				self.response.set_status(400)
				self.response.write(self.response.status)
				return
			
			if 'arrival_date' in req and type(req['arrival_date']) is not unicode:
				self.response.set_status(400)
				self.response.write(self.response.status)
				return
			
			if 'number' in req:
				slip.number = req['number']
			if 'arrival_date' in req:
				slip.arrival_date = req['arrival_date']
			
			# Update database
			slip.put()
			
			# Return updated slip to user
			self.response.set_status(200)
			s = slip.to_dict()
			self.response.write(json.dumps(s))
		else:
			self.response.set_status(403)
			self.response.write(self.response.status)
			
	def put(self, id=None):
		req = json.loads(self.request.body)
			
		# Attempt to retrieve slip
		slip = getByKey(id)
			
		# Not a valid slip
		if slip is None:
			self.response.set_status(404)
			self.response.write(self.response.status)
			return
		
		# Invalid number
		if 'number' not in req or type(req['number']) is not int:
			self.response.set_status(400)
			self.response.write(self.response.status)
			return
		
		# Remove boat from slip
		if slip.current_boat is not None:
			# Attempt to retrieve boat
			boat = getByKey(slip.current_boat)

			if boat is not None:
				boat.at_sea = True
				boat.put()
		
		slip.current_boat = None
		slip.arrival_date = None
		
		slip.number = req['number']
			
		# Update database
		slip.put()
			
		# Return updated slip to user
		self.response.set_status(200)
		sd = slip.to_dict()
		self.response.write(json.dumps(sd))
			
	def delete(self, id=None):
		if id:
			# Attempt to retrieve slip
			slip = getByKey(id)
			
			# Not a valid slip
			if slip is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
		
			# Remove boat from slip
			if slip.current_boat is not None:
				# Attempt to retrieve boat
				boat = getByKey(slip.current_boat)

				if boat is not None:
					boat.at_sea = True
					boat.put()
		
			# Delete slip
			ndb.Key(urlsafe=id).delete()
			
			self.response.set_status(204)
			self.response.write(self.response.status)
		else:
			self.response.set_status(403)
			self.response.write(self.response.status)
	
class ArrivalHandler(webapp2.RequestHandler):
	def put(self, id=None):
		if id:
			req = json.loads(self.request.body)
		
			# Attempt to retrieve slip
			slip = getByKey(id)
				
			if slip is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
			
			# Check if slip is occupied
			if slip.current_boat is not None:
				self.response.set_status(403)
				self.response.write(self.response.status)
				return
			
			# Check if required input was provided
			if 'boat' not in req or 'date' not in req:
				self.response.set_status(400)
				self.response.write(self.response.status)
				return
			
			# Attempt to retrieve boat
			boat = getByKey(req['boat'])
				
			if boat is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
			
			# If boat is already in a slip, return forbidden
			if not boat.at_sea:
				self.response.set_status(403)
				self.response.write(self.response.status)
				return
			
			# Everything checks out, add boat to slip
			slip.current_boat = req['boat']
			slip.arrival_date = req['date']
			boat.at_sea = False;
			
			# Update database
			slip.put()
			boat.put()
			
			self.response.set_status(200)
			sd = slip.to_dict()
			self.response.write(json.dumps(sd))
				
	def delete(self, id=None):
		if id:
			# Attempt to retrieve slip
			slip = getByKey(id)
				
			if slip is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
			
			# Returns forbidden when slip is empty
			if slip.current_boat is None:
				self.response.set_status(403)
				self.response.write(self.response.status)
				return
			
			# Attempt to retrieve boat
			boat = getByKey(slip.current_boat)
				
			if boat is None:
				self.response.set_status(404)
				self.response.write(self.response.status)
				return
			
			# Update boat
			boat.at_sea = True
			boat.put()
			
			# Update slip
			slip.current_boat = None
			slip.arrival_date = None
			slip.put()
			
			self.response.set_status(204)
			s = slip.to_dict()
			self.response.write(json.dumps(s))

# Helper functions
def isNumber(testVal):
	if type(testVal) is int or type(testVal) is float:
		return True
	return False

def invalidBoatParams(req):
	# Check that name is provided and valid
	if 'name' in req and type(req['name']) is not unicode:
		return True
	
	# Check optional fields are valid if provided
	if 'length' in req and not isNumber(req['length']):
		return True
	
	if 'type' in req and type(req['type']) is not unicode:
		return True
	
	return False
	
def getByKey(safeKey):
	# Returns object from db OR None if doesn't exist
	try:
		thing = ndb.Key(urlsafe=safeKey).get()
	except:
		return None
	
	return thing
	
	
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Marina API")

		
# enables Patch method
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
		
app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/boats', BoatHandler),
	('/boats/(.*)', BoatHandler),
	('/slips/(.*)/boat', ArrivalHandler),
	('/slips/(.*)', SlipHandler),
	('/slips', SlipHandler),
], debug=True)