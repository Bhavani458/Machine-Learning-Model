import streamlit as st
import pandas as pd
import pickle

# Load the trained model from the pickle file
with open('heloc_model.pkl', 'rb') as f:
    model = pickle.load(f)

st.title("HELOC ROI Prediction")

# Input fields for users to enter new data
estimated_value = st.number_input('Estimated Value', value=1000000)
equity_value = st.number_input('Equity Value', value=800000)
hei_opportunity = st.number_input('HEI Opportunity', value=50000)
mortgage_balance = st.number_input('Mortgage Balance', value=400000)
heloc_cost = st.number_input('HELOC Cost (10 years)', value=30000)
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

# Predict HELOC ROI
if st.button('Predict'):
    prediction = model.predict(new_data)
    st.write(f"Predicted HELOC ROI: {prediction[0]}")
