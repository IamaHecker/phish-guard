from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired()])
    template = SelectField('Email Template', coerce=int, validators=[DataRequired()])
    targets = TextAreaField('Target Emails (comma separated)', description="Enter email addresses separated by commas", validators=[DataRequired()])
    submit = SubmitField('Create Campaign')

class TemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired()])
    subject = StringField('Email Subject', validators=[DataRequired()])
    body = StringField('Email Body (HTML)', validators=[DataRequired()]) # Using StringField for simplicity, could be TextAreaField
    landing_page_id = SelectField('Landing Page', coerce=int, choices=[(1, 'Standard Phishing'), (2, 'Credential Harvest')], default=1)
    submit = SubmitField('Save Template')
