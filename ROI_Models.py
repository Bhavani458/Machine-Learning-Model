import streamlit as st
import pandas as pd
import pickle

# Load the trained models
def load_model(model_name):
    try:
        with open(model_name, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error(f"Model file {model_name} not found. Please check the file path.")
        return None

# Dictionary of available models
models = {
    'HELOC ROI': 'heloc_model.pkl',
    'Reverse Mortgage': 'RM_model.pkl',
    'Unison': 'Unison_model.pkl',
    'Point': 'Point_model.pkl'
}

# Streamlit app title
st.title("ROI Prediction for Different Competitors")

# Model selection
model_choice = st.selectbox("Select Model", list(models.keys()))

# Load the selected model
model = load_model(models[model_choice])

# Check if the model is loaded successfully
if model:
    # Input fields for users to enter new data
    estimated_value = st.number_input('Estimated Value', value=1000000)
    equity_value = st.number_input('Equity Value', value=800000)
    hei_opportunity = st.number_input('HEI Opportunity', value=50000)
    mortgage_balance = st.number_input('Mortgage Balance', value=400000)  # Correct typo
    vesta_buyout = st.number_input('Vesta Buyout (10 years)', value=70000)

    # Adjust input fields based on the selected model
    if model_choice == "HELOC ROI":
        heloc_cost = st.number_input('HELOC Cost (10 years)', value=30000)
        new_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Mortgage Balance': [mortgage_balance],  # Corrected typo
            'HELOC_Cost_10yr': [heloc_cost],
            'Vesta_Buyout_10yr': [vesta_buyout]
        })
    elif model_choice == "Reverse Mortgage":
        reverse_mortgage_cost = st.number_input('Reverse Mortgage Cost (10 years)', value=30000)
        new_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Mortgage Balance': [mortgage_balance],  # Corrected typo
            'Reverse_Mortgage_Cost_10yr': [reverse_mortgage_cost],
            'Vesta_Buyout_10yr': [vesta_buyout]
        })
    elif model_choice == "Unison":
        unison_buyout = st.number_input('Unison Buyout (10 years)', value=70000)
        new_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Mortgage Balance': [mortgage_balance],  # Corrected typo
            'Unison_Buyout_10yr': [unison_buyout],
            'Vesta_Buyout_10yr': [vesta_buyout]
        })
    elif model_choice == "Point":
        point_buyout = st.number_input('Point Buyout (10 years)', value=70000)
        new_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Mortgage Balance': [mortgage_balance],  # Corrected typo
            'Point_Buyout_10yr': [point_buyout],
            'Vesta_Buyout_10yr': [vesta_buyout]
        })

    # Predict ROI based on the selected model
    if st.button('Predict'):
        try:
            prediction = model.predict(new_data.values)  # Ensure .values is used
            st.write(f"Predicted ROI for Vesta and {model_choice}: {prediction[0]}")
        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")
else:
    st.error("Failed to load model. Please check the model file or path.")
