from viaduct.models.custom_form import CustomForm, CustomFormResult
from viaduct import db

class CustomFormAPI:
	@staticmethod
	def update_payment(transaction_id, payed):
		form_result = CustomFormResult.query.filter(CustomFormResult.transaction_id==transaction_id).first()
		if form_result:
			form_result.has_payed = payed
			db.session.commit()
		return


