from flask.ext.wtf import Form, BooleanField, TextField, TextAreaField,\
    FieldList
from flask.ext.wtf import SelectField, SubmitField, RadioField, FormField
from flask.ext.wtf import Optional, Required, Regexp
import wtforms


class EditGroupPagePermissionEntry(wtforms.Form):
    select = SelectField(None, coerce=int, choices=[(0, 'Geen'), (1, 'Lees'),
                                                    (2, 'Lees/Schrijf')])


class SuperPageForm(Form):
    """TODO"""
    needs_payed = BooleanField(u'Betaling vereist')

    title = TextField(u'Titel', validators=[Required()])
    comment = TextField(u'Commentaar', [Optional()])

    save_page = SubmitField('Opslaan')


class PageForm(SuperPageForm):
    content = TextAreaField(u'Inhoud', [Required()])
    filter_html = BooleanField(u'Sta HTML tags toe')
    permissions = FieldList(FormField(EditGroupPagePermissionEntry))


class HistoryPageForm(Form):
    previous = RadioField('Previous', coerce=int)
    current = RadioField('Current', coerce=int)
    compare = SubmitField('Compare')


class ChangePathForm(Form):
    path = TextField('Path', [Required(), Regexp(r'^ */?[\w-]+(/[\w-]+)*/? *$',
                                                 message='You suck at typing '
                                                         'URL paths')])
    move_only_this = SubmitField('Only this page')
    move_children = SubmitField('This and its children ')
