from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.types import JSON

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile fields for prediction
    insured_sex = db.Column(db.String(10), nullable=False)
    insured_education_level = db.Column(db.String(50), nullable=False)
    insured_occupation = db.Column(db.String(50), nullable=False)
    insured_relationship = db.Column(db.String(50), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with claims
    claims = db.relationship('Claim', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Claim(db.Model):
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Claim form fields
    months_as_customer = db.Column(db.Integer, nullable=False)
    policy_csl = db.Column(db.String(20), nullable=False)
    policy_deductable = db.Column(db.Integer, nullable=False)
    policy_annual_premium = db.Column(db.Float, nullable=False)
    umbrella_limit = db.Column(db.Integer, nullable=False)
    capital_gains = db.Column(db.Float, nullable=False)
    capital_loss = db.Column(db.Float, nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    collision_type = db.Column(db.String(50), nullable=False)
    incident_severity = db.Column(db.String(50), nullable=False)
    authorities_contacted = db.Column(db.String(50), nullable=False)
    incident_hour_of_the_day = db.Column(db.Integer, nullable=False)
    number_of_vehicles_involved = db.Column(db.Integer, nullable=False)
    property_damage = db.Column(db.String(10), nullable=False)
    bodily_injuries = db.Column(db.Integer, nullable=False)
    witnesses = db.Column(db.Integer, nullable=False)
    police_report_available = db.Column(db.String(10), nullable=False)
    injury_claim = db.Column(db.Float, nullable=False)
    property_claim = db.Column(db.Float, nullable=False)
    vehicle_claim = db.Column(db.Float, nullable=False)
    
    # Prediction result
    # model_predictions_json = db.Column(db.Text, nullable=True)  
    fraud_prediction = db.Column(db.String(20), nullable=True)
    prediction_confidence = db.Column(db.Float, nullable=True)
    model_predictions_json = db.Column(db.Text, nullable=True)  # Store JSON of all model predictions
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)