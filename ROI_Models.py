import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt

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
    'Point': 'Point_model.pkl',
    'Haus':'Haus_model.pkl',
    'Homium':'Homium_model.pkl'
}

# Streamlit app title
st.title("Vesta ROI Prediction for Different Competitors")

# Background information
st.markdown("""
    ### Welcome to the Home Equity Investment (HEI) ROI Prediction Tool!
    Select a competitor from the dropdown, enter the relevant details, and click **Predict** to get the estimated ROI.
""")


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
    elif model_choice == "Haus":
        haus_buyout = st.number_input('Haus Buyout (10 years)', value=70000)
        new_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Mortgage Balance': [mortgage_balance],  # Corrected typo
            'Haus_Buyout_10yr': [haus_buyout],
            'Vesta_Buyout_10yr': [vesta_buyout]
        })
    elif model_choice == "Homium":
        homium_buyout = st.number_input('Homium Buyout (10 years)', value=70000)
        new_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Mortgage Balance': [mortgage_balance],  # Corrected typo
            'Homium_Buyout_10yr': [homium_buyout],
            'Vesta_Buyout_10yr': [vesta_buyout]
        })
    # Predict ROI based on the selected model
    if st.button('Predict'):
        try:
            prediction = model.predict(new_data.values)
            st.success(f"Predicted ROI for Vesta and {model_choice}: ${prediction[0]:,.2f}")

            # Display the input data
            st.subheader("Input Data:")
            st.write(new_data)

            # Visualization with Pie Chart including the Predicted Value
            st.subheader("Visualization of Key Metrics:")
            fig, ax = plt.subplots()
            labels = ['Estimated Value', 'Equity Value', 'HEI Opportunity', 'Mortgage Balance', 'Predicted ROI']
            values = [estimated_value, equity_value, hei_opportunity, mortgage_balance, predicted_value]
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")
else:
    st.error("Failed to load model. Please check the model file or path.")
