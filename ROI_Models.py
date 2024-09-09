import streamlit as st
import pandas as pd
import pickle

# Load the trained models
def load_model(model_name):
    with open(model_name, 'rb') as f:
        return pickle.load(f)

# Dictionary of available models
models = {
    'HELOC ROI': 'heloc_model.pkl',
    'Reverse Mortgage': 'RM_Vesta.pkl',
    #'Unison':'Unison_Vesta.pkl',
    #'Point':'Point_Vesta.pkl',
    #'Haus':'Haus_Vesta.pkl',
    #'Homium':'Homium_Vesta.pkl',
      # Add other models like Unison if available
    # Add more models here if needed (e.g., 'Unison': 'unison_model.pkl')
}

# Streamlit app title
st.title("ROI Prediction for Different Competitors")

# Model selection
model_choice = st.selectbox("Select Model", list(models.keys()))

# Load the selected model
model = load_model(models[model_choice])

# Input fields for users to enter new data
estimated_value = st.number_input('Estimated Value', value=1000000)
equity_value = st.number_input('Equity Value', value=800000)
hei_opportunity = st.number_input('HEI Opportunity', value=50000)
mortgage_balance = st.number_input('Morgage Balance', value=400000)
heloc_cost = st.number_input('HELOC Cost (10 years)', value=30000)
reverse_mortgage_cost = st.number_input('Reverse Mortgage Cost (10 years)', value=30000)
vesta_buyout = st.number_input('Vesta Buyout (10 years)', value=70000)

# Collect data into a DataFrame
new_data = pd.DataFrame({
    'Estimated_Value': [estimated_value],
    'Equity_Value': [equity_value],
    'HEI Opportunity': [hei_opportunity],
    'Morgage Balance': [mortgage_balance],
    'HELOC_Cost_10yr': [heloc_cost],
    'Vesta_Buyout_10yr': [vesta_buyout]
})

# Adjust the input fields based on the selected model (optional step)
if model_choice == "Reverse Mortgage":
    new_data = pd.DataFrame({
        'Estimated_Value': [estimated_value],
        'Equity_Value': [equity_value],
        'HEI Opportunity': [hei_opportunity],
        'Morgage Balance': [mortgage_balance],
        'Reverse_Mortgage_Cost_10yr': [reverse_mortgage_cost],  # Adjust the feature name for RM model
        'Vesta_Buyout_10yr': [vesta_buyout]
    })

# Predict ROI based on the selected model
if st.button('Predict'):
    prediction = model.predict(new_data)
    st.write(f"Predicted ROI for {model_choice}: {prediction[0]}")
