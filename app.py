from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Claim
from forms import SignupForm, LoginForm, ClaimForm
from config import Config
import numpy as np
from models import db, User, Claim
from forms import SignupForm, LoginForm, ClaimForm
from config import Config
from ml_predictor import predictor

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('claim_form'))
    
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            name=form.name.data,
            insured_sex=form.insured_sex.data,
            insured_education_level=form.insured_education_level.data,
            insured_occupation=form.insured_occupation.data,
            insured_relationship=form.insured_relationship.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('claim_form'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('claim_form'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/claim', methods=['GET', 'POST'])
@login_required
def claim_form():
    form = ClaimForm()
    
    if form.validate_on_submit():
        # Create new claim
        claim = Claim(
            user_id=current_user.id,
            months_as_customer=form.months_as_customer.data,
            policy_csl=form.policy_csl.data,
            policy_deductable=form.policy_deductable.data,
            policy_annual_premium=form.policy_annual_premium.data,
            umbrella_limit=form.umbrella_limit.data,
            capital_gains=form.capital_gains.data,
            capital_loss=form.capital_loss.data,
            incident_type=form.incident_type.data,
            collision_type=form.collision_type.data,
            incident_severity=form.incident_severity.data,
            authorities_contacted=form.authorities_contacted.data,
            incident_hour_of_the_day=form.incident_hour_of_the_day.data,
            number_of_vehicles_involved=form.number_of_vehicles_involved.data,
            property_damage=form.property_damage.data,
            bodily_injuries=form.bodily_injuries.data,
            witnesses=form.witnesses.data,
            police_report_available=form.police_report_available.data,
            injury_claim=form.injury_claim.data,
            property_claim=form.property_claim.data,
            vehicle_claim=form.vehicle_claim.data
        )
        
        # Get predictions from all models
        prediction_result = predictor.predict_all_models(claim, current_user)
        reasons = predictor.get_fraud_reasons(claim, current_user, prediction_result)
        
        # Store prediction results
        claim.fraud_prediction = prediction_result['overall_prediction']
        claim.prediction_confidence = prediction_result['overall_confidence']
        
        db.session.add(claim)
        db.session.commit()
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'claim_id': claim.id,
                'overall_prediction': prediction_result['overall_prediction'],
                'overall_confidence': prediction_result['overall_confidence'],
                'fraud_count': prediction_result['fraud_count'],
                'not_fraud_count': prediction_result['not_fraud_count'],
                'total_models': prediction_result['total_models'],
                'reasons': reasons,
                'model_predictions': prediction_result['model_predictions']
            })
        
        # Fallback for non-AJAX requests
        flash(f'Claim submitted! Prediction: {prediction_result["overall_prediction"]}', 'success')
        return redirect(url_for('claim_form'))

    # Return validation errors for AJAX
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        errors = {}
        print("FORM ERRORS:", form.errors)
        for field, field_errors in form.errors.items():
            errors[field] = field_errors[0]
        return jsonify({'success': False, 'errors': errors}), 400
    
    return render_template('claim_form.html', form=form, user=current_user)

@app.route('/api/model-detail/<model_name>/<int:claim_id>')
@login_required
def get_model_detail(model_name, claim_id):
    """API endpoint to get specific model prediction details"""
    claim = Claim.query.get_or_404(claim_id)
    
    # Verify claim belongs to current user
    if claim.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get fresh prediction for this specific model
    prediction_result = predictor.predict_all_models(claim, current_user)
    
    if model_name in prediction_result['model_predictions']:
        model_pred = prediction_result['model_predictions'][model_name]
        return jsonify({
            'model_name': model_name,
            'prediction': 'FRAUD' if model_pred['is_fraud'] else 'NOT FRAUD',
            'confidence': model_pred.get('confidence'),
            'details': {
                'total_claim': claim.injury_claim + claim.property_claim + claim.vehicle_claim,
                'witnesses': claim.witnesses,
                'police_report': claim.police_report_available,
                'incident_severity': claim.incident_severity
            }
        })
    
    return jsonify({'error': 'Model not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)