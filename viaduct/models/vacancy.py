from viaduct import db
from datetime import datetime

class Vacancy(db.Model):
	__tablename__ = 'vacancy'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(256), unique=True)
	description = db.Column(db.String(1024))
	company_id = db.Column(db.Integer)
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)
	contract_of_service = db.Column(db.Enum('voltijd', 'deeltijd', 'bijbaan',
			'stage'))
	workload = db.Column(db.String(256))
	date = db.Column(db.DateTime)

	def __init__(self, title, description, company_id, start_date, end_date,
			contract_of_service, workload):
		self.title = title
		self.description = description
		self.company_id = company_id
		self.start_date = start_date
		self.end_date = end_date
		self.contract_of_service = contract_of_service
		self.workload = workload
		self.date = datetime.now()