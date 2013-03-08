from flask import render_template, request

from forms import UploadForm

class UploadAPI:
	@staticmethod
	def add_file():
		print("add_file");
		form = UploadForm(request.form)

		if form.validate_on_submit():
			if form.add_attachment.data:
				form.attachments.append_entry()
			elif form.upload.data:
				pass

		return render_template('upload/api/add_file.htm', form=form)

