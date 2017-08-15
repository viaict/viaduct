
# class FieldGroup(Field):
    # def __init__(self, groups, **kwargs):
        # super(FieldGroup, self).__init__(**kwargs)
        # self.groups = groups

    # # def validate(self, form, extra_validators=tuple()):
        # # for field in self.groups[1]:
            # # field.validate(form, extra_validators)

    # # def pre_validate(self, form):
        # # for field in self.groups[1]:
            # # field.pre_validate(form)

    # # def post_validate(self, form, validation_stopped):
        # # for field in self.groups[1]:
            # # field.post_validate(form, validation_stopped)

    # # def process(self, formdata, data=unset_value):
        # # for (groupname, fields) in self.groups:
            # # for field in fields:
                # # print(field)
                # # field.process(formdata, data)

    # # def process_data(self, value):
        # # for (groupname, fields) in self.groups:
            # # for field in fields:
                # # field.process_data(value)

    # # def process_formdata(self, valuelist):
        # # for field in self.groups[1]:
            # # field.process_formdata(valuedict)

    # # A field group should not have data
    # data = None
    # raw_data = None

    # # TODO errors, process_errors
    # @property
    # def errors(self):
        # errors = []
        # for field in self.groups[1]:
            # errors.append(field.errors)

        # return errors

    # @property
    # def process_errors(self):
        # errors = []
        # for field in self.groups[1]:
            # errors.append(field.process_errors)

        # return errors
