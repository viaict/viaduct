from flask_wtf import Form
from wtforms import BooleanField, StringField, TextAreaField, FieldList, \
    SelectField, SubmitField, RadioField, FormField

from wtforms.validators import Required, Regexp, Optional

from wtforms import Form as UnsafeForm


class EditGroupPagePermissionEntry(UnsafeForm):
    select = SelectField(None, coerce=int, choices=[(0, 'Geen'), (1, 'Lees'),
                                                    (2, 'Lees/Schrijf')])


class EditPageForm(Form):
    title = StringField('Title', [Required()])
    content = TextAreaField('Content', [Optional()])
    comment = StringField('Comment')
    filter_html = BooleanField('Sta HTML tags toe.')
    needs_payed = BooleanField('Betaling vereist.')
    permissions = FieldList(FormField(EditGroupPagePermissionEntry))
    save_page = SubmitField('Save Page')
    form_id = SelectField('Formulier', coerce=int)


class HistoryPageForm(Form):
    previous = RadioField('Previous', coerce=int)
    current = RadioField('Current', coerce=int)
    compare = SubmitField('Compare')


class ChangePathForm(Form):
    path = StringField('Path', [Required(),
                                Regexp(r'^ */?[\w-]+(/[\w-]+)*/?  *$',
                                       message='You suck at typing URL paths')]
                       )
    move_only_this = SubmitField('Only this page')
    move_children = SubmitField('This and its children ')
