import streamlit as st
import pandas as pd
import pickle
import numpy as np
import numpy_financial as npf
import plotly.graph_objects as go
import plotly.express as px

# Custom CSS to change the background color
def set_background_color():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #3d405b;  /* Blue */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Apply the custom background color
set_background_color()

# Function to load models
def load_model(model_name):
    try:
        with open(model_name, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error(f"Model file {model_name} not found. Please check the file path.")
        return None

# Dictionary of available competitor models
models = {
    'HELOC': 'heloc_model.pkl',
    'Reverse Mortgage': 'RM_model.pkl',
    'Unison': 'Unison_model.pkl',
    'Point': 'Point_model.pkl',
    'Haus': 'Haus_model.pkl',
    'Homium': 'Homium_model.pkl'
}

# Streamlit app title and description
st.title("Vesta ROI Prediction for Various Competitors")
st.markdown("""
    ### Welcome to the Home Equity Investment (HEI) ROI Prediction Tool!
    Select a competitor from the dropdown, enter the relevant details, and click **Predict** to get the estimated ROI.
""")

# Competitor selection
model_choice = st.selectbox("Select Competitor Model", list(models.keys()))

# Load the selected competitor model
competitor_model = load_model(models[model_choice])

# Ensure the competitor model is loaded
if competitor_model:
    # User inputs
    estimated_value = st.number_input('Estimated Property Value ($)', value=1000000)
    equity_value = st.number_input('Equity Value ($)', value=800000)
    mortgage_balance = st.number_input('Mortgage Balance ($)', value=400000)
    percent_equity_access = st.number_input('Percent of Equity Access (%)', value=10.0)
    
    # Validate that estimated value is greater than or equal to equity value
    if estimated_value < equity_value:
        try:
            st.error("Error: Estimated Property Value should be greater than or equal to Equity Value.")
        except Exception as e:
            st.error("Cannot proceed further")
    elif mortgage_balance > equity_value:
        try:
            st.error("Error: Mortgage Balance should be less than or equal to Equity Value.")
        except Exception as e:
            st.error("Cannot proceed further")
    else:
        # Access type selection
        access_type = st.selectbox('Select Access Type', ['Equity Access', 'Mortgage Exit'])
        # Calculate HEI Opportunity based on access type
        if access_type == 'Equity Access':
            hei_opportunity = (percent_equity_access / 100) * equity_value
        elif access_type == 'Mortgage Exit':
            hei_opportunity = mortgage_balance
        else:
            hei_opportunity = 0
        st.write(f"Calculated HEI Opportunity: ${hei_opportunity:,.2f}")
        
        #calculation for Vesta Buyout (10 years)
        vesta_appreciated_10yr = (((1 - 0.15) * estimated_value) * (1 + 0.04) ** 10)
        vesta_buyout_10yr = (percent_equity_access/100)*vesta_appreciated_10yr

    def calculate_competitor_buyout(competitor, estimated_value, hei_opportunity, equity_percent):
        try:
            # Ensure numeric types for all values
            estimated_value = float(estimated_value)
            hei_opportunity = float(hei_opportunity)
            equity_percent = float(equity_percent)

            # Competitor-specific formulas
            if competitor == 'HELOC':
                rate = 0.11 / 12
                nper = 10 * 12
                competitor_buyout_10yr = npf.pmt(rate, nper, -hei_opportunity) * 120  # Formula for HELOC
            elif competitor == 'Reverse Mortgage':
                rate = 0.0806 / 12
                nper = 10 * 12
                competitor_buyout_10yr = npf.fv(rate, nper, 0, -hei_opportunity)  # Formula for Reverse Mortgage
            elif competitor == 'Unison':
                competitor_buyout_10yr = (4 * equity_percent) * (((1 - 0.05) * estimated_value) * (1 + 0.04) ** 10) + hei_opportunity  # Unison formula
            elif competitor == 'Point':
                competitor_buyout_10yr = (equity_percent) * (((1 - 0.29) * estimated_value) * (1 + 0.04) ** 10) + hei_opportunity  # Point formula
            elif competitor == 'Haus':
                competitor_buyout_10yr = (equity_percent) * (((1 - 0.20) * estimated_value) * (1 + 0.04) ** 10) + hei_opportunity - (120 * (0.01 * hei_opportunity))  # Haus formula
            elif competitor == 'Homium':
                competitor_buyout_10yr = (equity_percent) * ((estimated_value) * (1 + 0.04) ** 10) + hei_opportunity  # Homium formula
            else:
                competitor_buyout_10yr = 0
        except ValueError:
            st.error("Input values must be numeric.")
            competitor_buyout_10yr = 0

        return competitor_buyout_10yr

    # Calculate competitor buyout using the provided formulas
    equity_percent = percent_equity_access / 100
    competitor_buyout_10yr = calculate_competitor_buyout(model_choice, estimated_value, hei_opportunity, equity_percent)
    
    # Prepare data for competitor model
    competitor_data = pd.DataFrame({
        'Estimated_Value': [estimated_value],
        'Equity_Value': [equity_value],
        'HEI Opportunity': [hei_opportunity],
        'Morgage Balance': [mortgage_balance],
        f"{model_choice}_Buyout_10yr": [competitor_buyout_10yr],
        'Vesta_Buyout_10yr': [vesta_buyout_10yr]
    })
    # Predict and display results
    if st.button('Predict'):
        try:
            # Competitor prediction
            competitor_prediction = competitor_model.predict(competitor_data.values)
            competitor_roi = competitor_prediction[0]
            
            # Static Vesta ROI calculation (this is a placeholder, modify based on your static calculation)
            vesta_roi = vesta_appreciated_10yr - vesta_buyout_10yr
            
            # Display predictions side by side
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Vesta ROI Prediction")
                st.success(f"ROI for Vesta: {vesta_roi:.2f}")
                st.write("***'ROI for vesta' is the difference between Appreciated home value in 10yrs and Vesta Buyout in 10yrs***")
                st.markdown(f"<span style='font-size:20px; font-weight:bold; color:white'>Vesta Buyout (10 years): ${vesta_buyout_10yr:,.2f}</span>", unsafe_allow_html=True)
            with col2:
                st.subheader(f"Vesta and {model_choice} ROI Prediction")
                if(competitor_roi<0):
                    st.markdown(f"Predicted ROI for Vesta & {model_choice}:<span style='font-size:20px; font-weight:bold; color:red'>{competitor_roi:.2f}</span>",unsafe_allow_html=True)
                else:
                    st.success(f"Predicted ROI for Vesta & {model_choice}: {competitor_roi:.2f}")
                st.write(f"***'Predicted ROI' is the difference between costs associated with {model_choice} and Vesta***")
                st.markdown(f"<span style='font-size:20px; font-weight:bold; color:white'>{model_choice} Buyout (10 years): ${competitor_buyout_10yr:,.2f}</span>", unsafe_allow_html=True)
                st.write("**Input Data:**")
                st.write(competitor_data)
            
            # Visualization side by side
            st.subheader("Visualization of Key Metrics")
            col1, col2 = st.columns(2)
            # Vesta Bar Chart
            with col1:
                labels = ['Estimated Value', 'Equity Value', 'HEI Opportunity', 'Mortgage Balance', 'Vesta ROI']
                values = [estimated_value, equity_value, hei_opportunity, mortgage_balance, vesta_roi]
                # Create a bar chart for Vesta
                fig_vesta = px.bar(
                    x=labels, 
                    y=values, 
                    labels={'x': 'Metrics', 'y': 'Values ($)'}, 
                    title="Vesta Metrics and ROI"
                )
                fig_vesta.update_layout(
                    title_text="Vesta Metrics and ROI", 
                    xaxis_title="Metrics", 
                    yaxis_title="Values ($)"
                )
                st.plotly_chart(fig_vesta)
            # Competitor Bar Chart
            with col2:
                # Create a bar chart to compare Vesta ROI and Competitor ROI
                labels = [f'{model_choice} and Vesta Predicted ROI']
                values = [competitor_roi]

                fig_comparison = px.bar(
                    x=labels,
                    y=values,
                    labels={'x': 'Metrics', 'y': 'ROI ($)'},
                    title=f"Cost Difference between Vesta and {model_choice}"
                )
                # Update layout
                fig_comparison.update_layout(
                    xaxis_title="Metrics",
                    yaxis_title="ROI ($)",
                    title_text=f"Cost Difference between Vesta and {model_choice}"
                )
                # Display in Streamlit
                st.plotly_chart(fig_comparison)
        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")
else:
    st.error("Failed to load competitor models. Please check the model files.")
