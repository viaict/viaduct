from application import db

# Vacature zelf

class Vacancy(db.Model):
	__tablename__ = 'vacancy'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(256), unique=True)
	description = db.Column(db.String(1024))
	company_id = db.Column(db.Integer)
	start_date = db.Column(db.DateTime(timezone='Europe/Amsterdam')) # weet niet of timezone zo werkt
	end_date = db.Column(db.DateTime(timezone='Europe/Amsterdam'))
	contract_of_service = db.Column(db.String(256)) # moet ENUM worden met (voltijd, deeltijd, bijbaan, stage)
	date = db.Column(db.DateTime(timezone='Europe/Amsterdam'))

	def __init__(self, title, description, company_id, start_date, end_date, contract_of_service):
		self.title = title
		self.description = description
		self.company_id = company_id
		self.start_date = start_date
		self.end_date = end_date
		self.contract_of_service = contract_of_service
		self.date = date # Automatische datum van vandaag - plaatsings datum
