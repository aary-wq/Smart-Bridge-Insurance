from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, ValidationError, NumberRange
from models import User

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    
    insured_sex = SelectField('Sex', 
                             choices=[('', 'Select'), ('MALE', 'Male'), ('FEMALE', 'Female'),('OTHERS', 'Others')],
                             validators=[DataRequired()])
    
    
    insured_education_level = SelectField('Education Level',
                                     choices=[('', 'Select'),
                                             ('High School', 'High School'),
                                             ('Associate', 'Associate'),
                                             ('College', 'College'),
                                             ('Masters', 'Masters'),
                                             ('PhD', 'PhD'),
                                             ('MD', 'MD'),
                                             ('JD', 'JD (Juris Doctor)')],
                                     validators=[DataRequired()])
    
    insured_occupation = SelectField('Occupation',
                                choices=[('', 'Select'),
                                        ('adm-clerical', 'Administrative/Clerical'),
                                        ('armed-forces', 'Armed Forces'),
                                        ('craft-repair', 'Craft/Repair'),
                                        ('exec-managerial', 'Executive/Managerial'),
                                        ('farming-fishing', 'Farming/Fishing'),
                                        ('handlers-cleaners', 'Handlers/Cleaners'),
                                        ('machine-op-inspct', 'Machine Operator/Inspector'),
                                        ('other-service', 'Other Service'),
                                        ('priv-house-serv', 'Private House Service'),
                                        ('prof-specialty', 'Professional Specialty'),
                                        ('protective-serv', 'Protective Service'),
                                        ('sales', 'Sales'),
                                        ('tech-support', 'Tech Support'),
                                        ('transport-moving', 'Transport/Moving')],
                                validators=[DataRequired()])
    
    insured_relationship = SelectField('Relationship',
                                  choices=[('', 'Select'),
                                          ('husband', 'Husband'),
                                          ('wife', 'Wife'),
                                          ('own-child', 'Own Child'),
                                          ('unmarried', 'Unmarried'),
                                          ('other-relative', 'Other Relative'),
                                          ('not-in-family', 'Not in Family')],
                                  validators=[DataRequired()])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class ClaimForm(FlaskForm):
    months_as_customer = IntegerField('Months as Customer', 
                                     validators=[InputRequired(), NumberRange(min=0)])
    
    policy_csl = SelectField('Policy CSL',
                            choices=[('', 'Select'),
                                    ('100/300', '100/300'),
                                    ('250/500', '250/500'),
                                    ('500/1000', '500/1000')],
                            validators=[DataRequired()])
    
    policy_deductable = IntegerField('Policy Deductable', 
                                    validators=[InputRequired(), NumberRange(min=0)])
    
    policy_annual_premium = FloatField('Policy Annual Premium', 
                                      validators=[InputRequired(), NumberRange(min=0)])
    
    umbrella_limit = IntegerField('Umbrella Limit', 
                                 validators=[InputRequired(), NumberRange(min=0)])
    
    capital_gains = FloatField('Capital Gains', 
                              validators=[InputRequired(), NumberRange(min=0)])
    
    capital_loss = FloatField('Capital Loss', 
                             validators=[InputRequired(), NumberRange(min=0)])
    
    incident_type = SelectField('Incident Type',
                               choices=[('', 'Select'),
                                       ('Single Vehicle Collision', 'Single Vehicle Collision'),
                                       ('Vehicle Theft', 'Vehicle Theft'),
                                       ('Multi-vehicle Collision', 'Multi-vehicle Collision'),
                                       ('Parked Car', 'Parked Car')],
                               validators=[DataRequired()])
    
    collision_type = SelectField('Collision Type',
                                choices=[('', 'Select'),
                                        ('Front Collision', 'Front Collision'),
                                        ('Rear Collision', 'Rear Collision'),
                                        ('Side Collision', 'Side Collision'),
                                        ('Unknown', 'Unknown')],
                                validators=[DataRequired()])
    
    incident_severity = SelectField('Incident Severity',
                                   choices=[('', 'Select'),
                                            ('Minor Damage', 'Minor Damage'),
                                            ('Major Damage', 'Major Damage'),
                                            ('Total Loss', 'Total Loss'),
                                            ('Trivial Damage', 'Trivial Damage')],
                                   validators=[DataRequired()])
    
    authorities_contacted = SelectField('Authorities Contacted',
                                       choices=[('', 'Select'),
                                               ('Police', 'Police'),
                                               ('Fire', 'Fire'),
                                               ('Ambulance', 'Ambulance'),
                                               ('None', 'None'),
                                               ('Other', 'Other')],
                                       validators=[DataRequired()])
    
    incident_hour_of_the_day = IntegerField('Incident Hour (0-23)', 
                                           validators=[InputRequired(), NumberRange(min=0, max=23)])
    
    number_of_vehicles_involved = IntegerField('Number of Vehicles Involved', 
                                              validators=[InputRequired(), NumberRange(min=1)])
    
    property_damage = SelectField('Property Damage',
                                 choices=[('', 'Select'), ('YES', 'Yes'), ('NO', 'No')],
                                 validators=[DataRequired()])
    
    bodily_injuries = IntegerField('Bodily Injuries', 
                                  validators=[InputRequired(), NumberRange(min=0)])
    
    witnesses = IntegerField('Witnesses', 
                            validators=[InputRequired(), NumberRange(min=0)])
    
    police_report_available = SelectField('Police Report Available',
                                         choices=[('', 'Select'), ('YES', 'Yes'), ('NO', 'No')],
                                         validators=[DataRequired()])
    
    injury_claim = FloatField('Injury Claim', 
                             validators=[InputRequired(), NumberRange(min=0)])
    
    property_claim = FloatField('Property Claim', 
                               validators=[InputRequired(), NumberRange(min=0)])
    
    vehicle_claim = FloatField('Vehicle Claim', 
                              validators=[InputRequired(), NumberRange(min=0)])
