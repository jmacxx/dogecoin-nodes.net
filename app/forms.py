from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app import app, db
from app.models import Inventory


class ClaimPrizeForm(FlaskForm):
    nodeipaddress = StringField('Node ipaddress', default="hello_world", validators=[DataRequired()])
    youripaddress = StringField('Your ipaddress', default="hello_world", validators=[DataRequired()])
    nodeversion = StringField('Node version', default="hello_world", validators=[DataRequired()])
    dogecoinaddress = StringField('Dogecoin Address', validators=[DataRequired()])
    submit = SubmitField('Send me Dogecoinz!')

    def validate_dogecoinaddress(self, dogecoinaddress):
        # need to include dogecoin address validation here
        # base58check?
        if dogecoinaddress.data[:1] != 'D' or len(dogecoinaddress.data) != 34:
            raise ValidationError('Please enter a dogecoin address.')
        pass

    def validate_nodeversion(self, nodeversion):
        # JMC what if the user spoofed the form submittal replacing nodeversion?
        if nodeversion.data[:19] != app.config['DOGECOIN_NODE_VERSION']:
            raise ValidationError('Please upgrade your node.')
        pass

    def validate_youripaddress(self, youripaddress):
        # JMC what if the user spoofed the form submittal replacing youripaddress?
        if youripaddress.data != self.nodeipaddress.data:
            raise ValidationError('IP addresses do not match')
        pass

