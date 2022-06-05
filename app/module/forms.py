# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, SelectField, BooleanField, FormField, FieldList, IntegerField
# from wtforms.validators import DataRequired


# class PrivilegesSubForm(FlaskForm):
#     schema_name = StringField('Schema name to apply permissions against', validators=[DataRequired()])
#     tables = StringField('Comma seperated list of table permissions', validators=[DataRequired()])
#     functions = StringField('Comma seperated list of function permissions', validators=[DataRequired()])
#     sequences = StringField('Comma seperated list of sequence permissions', validators=[DataRequired()])

# class RolesSubform(FlaskForm):
#     name = StringField('Name of custom permission role', validators=[DataRequired()])
#     privileges = FieldList(FormField(PrivilegesSubForm), min_entries=1)
#     members = FieldList(StringField('Members', validators=[DataRequired()]), min_entries=1 )


# class DatabasesSubForm(FlaskForm):
#     name = StringField('Name of the database', validators=[DataRequired()])
#     owner = StringField('Login that owns the database', validators=[DataRequired()])
#     encoding = StringField('Database encoding', validators=[DataRequired()])
#     conn_limit = IntegerField('Database connection limit', validators=[DataRequired()])
#     roles = FieldList(FormField(RolesSubform), min_entries=1, max_entries=3)

# class MetadataSubForm(FlaskForm):
#     metadata_owner = StringField('Cluster owner', validators=[DataRequired()])
#     metadata_description = StringField('Cluster purpose', validators=[DataRequired()])

# class ConfigSubForm(FlaskForm):
#     metadata = FormField(MetadataSubForm)

# class NameForm(FlaskForm):
#     type_choices = ['standalone','manual_failover', 'auto_failover']
#     version_choices = [11,12,13,14]
#     primary_region_choices = ['UK1','UK2','EU1','USWEST']
#     primary_az_choices = ['AZ1','AZ2','AZ3']
#     name = StringField('Enter a unique name for the Database cluster?', validators=[DataRequired()])
#     type = SelectField('Specify the cluster type', choices=type_choices, validators=[DataRequired()])
#     version = SelectField('Specify the database software version', choices=version_choices, default=14, validators=[DataRequired()])
#     primary_region = SelectField('Specify the primary region where cluster will be located', choices=primary_region_choices, default='UK1', validators=[DataRequired()])
#     primary_az = SelectField('Specify the primary az where cluster will be located', choices=primary_az_choices, default='AZ1', validators=[DataRequired()])
#     dr_enabled = BooleanField('Is DR required, will provide a replica in different geo-location', default=False)

#     config = FormField(ConfigSubForm)

#     databases = FieldList(FormField(DatabasesSubForm), min_entries=1)

#     submit = SubmitField('Submit')