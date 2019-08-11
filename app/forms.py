from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo


class ClaimPrizeForm(FlaskForm):
    dogecoinaddress = StringField('dogecoinaddress', validators=[DataRequired()])
    ipaddress = StringField('ipaddress', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_dogecoinaddress(self, dogecoinaddress):
        # need to include dogecoin address validation here
        # base58check?
        #raise ValidationError('Please enter a dogecoin address.')
        pass

    def validate_ipaddress(self, ipaddress):
        pass

