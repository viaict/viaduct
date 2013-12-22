from flask.ext.wtf import Form, BooleanField, TextField, TextAreaField, FieldList
from flask.ext.wtf import SelectField, SubmitField, RadioField, FormField
from flask.ext.wtf import Optional, NumberRange, Required, Regexp
import wtforms

class EditGroupPagePermissionEntry(wtforms.Form):
    select = SelectField(None, coerce=int, choices=[(0, 'Geen'), (1, 'Lees'), (2, 'Lees/Schrijf')])

class EditPageForm(Form):
    title = TextField('Title', [Required()])
    content = TextAreaField('Content', [Optional()])
    comment = TextField('Comment')
    filter_html = BooleanField('Disable HTML filtering for the current page.')
    needs_payed = BooleanField('Betaling vereist.')
    permissions = FieldList(FormField(EditGroupPagePermissionEntry))
    save_page = SubmitField('Save Page')

class HistoryPageForm(Form):
    previous = RadioField('Previous', coerce=int)
    current = RadioField('Current', coerce=int)
    compare = SubmitField('Compare')

class ChangePathForm(Form):
    path = TextField('Path', [Required(), Regexp(r'^ */?[\w-]+(/[\w-]+)*/? *$', message='You suck at typing URL paths')])
    move_only_this = SubmitField('Only this page')
    move_children = SubmitField('This and its children ')
