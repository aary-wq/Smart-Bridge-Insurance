import pandas as pd
import numpy as np
import joblib
from pathlib import Path

class FraudPredictor:
    def __init__(self):
        self.models_dir = Path('models')
        self.models = {}
        self.scaler = None
        self.X_train_columns = None  # Store training columns for alignment
        self.load_models()
    
    def load_models(self):
        """Load all trained models and scaler"""
        try:
            # Load X_train columns for alignment (essential for correct feature ordering)
            try:
                # The user's notebook logic expects alignment with training columns
                self.X_train_columns = joblib.load(self.models_dir / 'feature_columns.pkl')
                print(f"Loaded {len(self.X_train_columns)} feature columns for alignment")
            except FileNotFoundError:
                print("Warning: feature_columns.pkl not found")
            
            # Load scaler
            try:
                self.scaler = joblib.load(self.models_dir / 'scaler.pkl')
                print("Scaler loaded successfully")
            except FileNotFoundError:
                print("Warning: scaler.pkl not found")
            
            # Load all models
            model_files = {
                'AdaBoost': 'adaboost_model.pkl',
                'Random Forest': 'random_forest_model.pkl',
                'XGBoost': 'xgboost_model.pkl',
                'LightGBM': 'lightgbm_model.pkl',
                'CatBoost': 'catboost_model.pkl',
                'Gradient Boosting': 'gradient_boosting_model.pkl',
                'Extra Trees': 'extra_trees_model.pkl',
                'KNN': 'knn_model.pkl',
                'SVC': 'svc_model.pkl',
                'Decision Tree': 'decision_tree_model.pkl',
                'Stochastic GB': 'sgb_model.pkl',
                'Voting Classifier': 'voting_classifier_model.pkl'
            }
            
            for name, filename in model_files.items():
                try:
                    model = joblib.load(self.models_dir / filename)
                    self.models[name] = model
                    print(f"Loaded: {name}")
                except FileNotFoundError:
                    print(f"Warning: {filename} not found")
        
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def prepare_dataframe(self, claim, user):
        """Prepare DataFrame matching the exact structure from the user's updated logic"""
        
        # Define sample input matching the original DataFrame's structure (before any drops)
        sample_input_data = {
            'months_as_customer': claim.months_as_customer,
            'age': 35,  # Placeholder
            'policy_number': 123456,  # Placeholder
            'policy_bind_date': '2010-01-01',  # Placeholder
            'policy_state': 'OH',  # Placeholder
            'policy_csl': claim.policy_csl,
            'policy_deductable': claim.policy_deductable,
            'policy_annual_premium': claim.policy_annual_premium,
            'umbrella_limit': claim.umbrella_limit,
            'insured_zip': 430000,  # Placeholder
            'insured_sex': user.insured_sex,
            'insured_education_level': user.insured_education_level,
            'insured_occupation': user.insured_occupation,
            'insured_hobbies': 'reading',  # Placeholder
            'insured_relationship': user.insured_relationship,
            'capital-gains': claim.capital_gains,
            'capital-loss': claim.capital_loss,
            'incident_date': '2023-01-01',  # Placeholder
            'incident_type': claim.incident_type,
            'collision_type': claim.collision_type,
            'incident_severity': claim.incident_severity,
            'authorities_contacted': claim.authorities_contacted,
            'incident_state': 'NY',  # Placeholder
            'incident_city': 'Columbus',  # Placeholder
            'incident_location': 'street A',  # Placeholder
            'incident_hour_of_the_day': claim.incident_hour_of_the_day,
            'number_of_vehicles_involved': claim.number_of_vehicles_involved,
            'property_damage': claim.property_damage,
            'bodily_injuries': claim.bodily_injuries,
            'witnesses': claim.witnesses,
            'police_report_available': claim.police_report_available,
            'total_claim_amount': claim.injury_claim + claim.property_claim + claim.vehicle_claim,
            'injury_claim': claim.injury_claim,
            'property_claim': claim.property_claim,
            'vehicle_claim': claim.vehicle_claim,
            'auto_make': 'Honda',  # Placeholder
            'auto_model': 'CRV',  # Placeholder
            'auto_year': 2015,  # Placeholder
            '_c39': np.nan  # Placeholder
        }
        
        # Create DataFrame
        sample_df = pd.DataFrame([sample_input_data])
        
        # Apply the exact same column drops as during training (as provided by user)
        to_drop = ['policy_number','policy_bind_date','policy_state','insured_zip','incident_location',
                   'incident_date','incident_state','incident_city','insured_hobbies','auto_make',
                   'auto_model','auto_year', '_c39']
        sample_df.drop(to_drop, inplace=True, axis=1)
        sample_df.drop(columns=['age', 'total_claim_amount'], inplace=True)
        
        return sample_df
    
    def preprocess_features(self, sample_df):
        """Preprocess features: scale numerical, encode categorical, and align columns"""
        
        # Define column groups as per user logic
        num_cols = ['months_as_customer', 'policy_deductable', 'umbrella_limit',
                    'capital-gains', 'capital-loss', 'incident_hour_of_the_day',
                    'number_of_vehicles_involved', 'bodily_injuries', 'witnesses',
                    'injury_claim', 'property_claim', 'vehicle_claim']
        
        cat_cols = ['policy_csl', 'insured_sex', 'insured_education_level', 'insured_occupation',
                    'insured_relationship', 'incident_type', 'collision_type',
                    'incident_severity', 'authorities_contacted', 'property_damage',
                    'police_report_available']
        
        sample_num_df = sample_df[num_cols]
        sample_cat_df = sample_df[cat_cols]
        
        # Scale numerical features
        if self.scaler:
            scaled_sample_data = self.scaler.transform(sample_num_df)
            scaled_sample_num_df = pd.DataFrame(data=scaled_sample_data, columns=num_cols, index=sample_df.index)
        else:
            scaled_sample_num_df = sample_num_df
        
        # One-hot encode categorical features (drop_first=True as per user logic)
        encoded_sample_cat_df = pd.get_dummies(sample_cat_df, drop_first=True)
        
        # Concatenate scaled numerical and encoded categorical
        final_sample_df = pd.concat([scaled_sample_num_df, encoded_sample_cat_df], axis=1)
        
        # Align columns with X_train columns (Crucial for model consistency)
        if self.X_train_columns is not None:
            # Add missing columns (present in training but not in current input) with value 0
            missing_cols = set(self.X_train_columns) - set(final_sample_df.columns)
            for c in missing_cols:
                final_sample_df[c] = 0
            
            # Drop extra columns (present in current input but not in training)
            # (Though get_dummies on the same categories should mostly be fine, alignment ensures it)
            
            # Ensure the order of columns matches training data exactly
            final_sample_df = final_sample_df[self.X_train_columns]
        
        # Convert boolean columns to integer (0 or 1)
        for col in final_sample_df.columns:
            if final_sample_df[col].dtype == 'bool' or str(final_sample_df[col].dtype).startswith('bool'):
                final_sample_df[col] = final_sample_df[col].astype(int)
        
        return final_sample_df
    
    def predict_all_models(self, claim, user):
        """Get predictions from all models"""
        print(f"\n=== Starting prediction with {len(self.models)} models ===")
        
        # Prepare DataFrame
        sample_df = self.prepare_dataframe(claim, user)
        print(f"DataFrame prepared with shape: {sample_df.shape}")
        
        # Preprocess features
        final_sample_df = self.preprocess_features(sample_df)
        print(f"Features preprocessed with shape: {final_sample_df.shape}")
        
        predictions = {}
        fraud_count = 0
        not_fraud_count = 0
        
        for model_name, model in self.models.items():
            try:
                # Make prediction
                prediction = model.predict(final_sample_df)
                
                # Handle different prediction formats ('Y'/'N' or 1/0)
                if isinstance(prediction[0], str):
                    is_fraud = (prediction[0] == 'Y')
                else:
                    is_fraud = bool(prediction[0] == 1)
                
                # Get probability if available
                try:
                    proba = model.predict_proba(final_sample_df)[0]
                    if is_fraud:
                        # If prediction is fraud, take the probability of fraud class
                        confidence = max(proba) * 100
                    else:
                        # If prediction is not fraud, take the probability of not fraud class
                        confidence = max(proba) * 100
                except Exception as e:
                    confidence = None
                    print(f"No probability available for {model_name}: {e}")
                
                predictions[model_name] = {
                    'is_fraud': is_fraud,
                    'prediction': prediction[0],
                    'confidence': confidence
                }
                
                print(f"{model_name}: {'FRAUD' if is_fraud else 'NOT FRAUD'} (confidence: {confidence})")
                
                if is_fraud:
                    fraud_count += 1
                else:
                    not_fraud_count += 1
                    
            except Exception as e:
                print(f"❌ Error with {model_name}: {e}")
                predictions[model_name] = {
                    'is_fraud': None,
                    'prediction': None,
                    'confidence': None,
                    'error': str(e)
                }
        
        print(f"\n=== Results: {fraud_count} FRAUD, {not_fraud_count} NOT FRAUD ===\n")
        
        # Determine overall prediction
        total_models = fraud_count + not_fraud_count
        overall_is_fraud = fraud_count > not_fraud_count
        overall_confidence = (fraud_count / total_models * 100) if total_models > 0 else 0
        
        return {
            'overall_prediction': 'FRAUD' if overall_is_fraud else 'NOT FRAUD',
            'overall_confidence': overall_confidence,
            'fraud_count': fraud_count,
            'not_fraud_count': not_fraud_count,
            'total_models': total_models,
            'model_predictions': predictions
        }
    
    def get_fraud_reasons(self, claim, user, prediction_result):
        """Generate reasons for fraud prediction"""
        reasons = []
        
        if prediction_result['overall_prediction'] == 'FRAUD':
            # High claim amount
            total_claim = claim.injury_claim + claim.property_claim + claim.vehicle_claim
            if total_claim > 50000:
                reasons.append(f"High total claim amount: ${total_claim:,.2f}")
            
            # No witnesses
            if claim.witnesses == 0:
                reasons.append("No witnesses present at the incident")
            
            # No police report
            if claim.police_report_available == 'NO':
                reasons.append("No police report available")
            
            # Suspicious timing
            if claim.incident_hour_of_the_day < 5 or claim.incident_hour_of_the_day > 22:
                reasons.append(f"Incident occurred at unusual hour: {claim.incident_hour_of_the_day}:00")
            
            # Low customer tenure
            if claim.months_as_customer < 6:
                reasons.append(f"Short customer relationship: {claim.months_as_customer} months")
            
            # Multiple vehicles but single collision type
            if claim.number_of_vehicles_involved > 2 and 'Single' in claim.incident_type:
                reasons.append("Inconsistent vehicle count and incident type")
            
            # High severity with low witness count
            if claim.incident_severity == 'Total Loss' and claim.witnesses < 2:
                reasons.append("Severe incident with insufficient witnesses")
            
        else:
            reasons.append("Claim details appear consistent and legitimate")
            reasons.append(f"Sufficient evidence: {claim.witnesses} witnesses")
            if claim.police_report_available == 'YES':
                reasons.append("Police report available")
        
        return reasons if reasons else ["Standard claim validation applied"]

# Global predictor instance
predictor = FraudPredictor()