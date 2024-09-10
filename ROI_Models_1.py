import streamlit as st
import pandas as pd
import pickle
import numpy as np
import plotly.graph_objects as go

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
    'HELOC ROI': 'heloc_model.pkl',
    'Reverse Mortgage': 'reverse_mortgage_model.pkl',
    'Unison': 'unison_model.pkl',
    'Point': 'point_model.pkl',
    'Haus': 'haus_model.pkl',
    'Homium': 'homium_model.pkl'
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
    
    # Access type selection
    access_type = st.selectbox('Select Access Type', ['Equity Access', 'Mortgage Exit'])
    
    # Calculate HEI Opportunity
    if access_type == 'Equity Access':
        hei_opportunity = (percent_equity_access / 100) * equity_value
    elif access_type == 'Mortgage Exit':
        hei_opportunity = mortgage_balance
    else:
        hei_opportunity = 0
    
    # Display the calculated HEI Opportunity
    st.write(f"Calculated HEI Opportunity: ${hei_opportunity:,.2f}")
    
    # Static calculation for Vesta Buyout (10 years)
    vesta_buyout_10yr = ((1 - 0.15) * estimated_value) * (1 + 0.04) ** 10
    
    # Function to calculate competitor buyout based on formulas provided
    def calculate_competitor_buyout(competitor, estimated_value, hei_opportunity, equity_percent):
        if competitor == 'HELOC ROI':
            rate = 0.11 / 12
            nper = 10 * 12
            competitor_buyout_10yr = np.pmt(rate, nper, -hei_opportunity) * 120  # Formula for HELOC
        elif competitor == 'Reverse Mortgage':
            rate = 0.0806 / 12
            nper = 10 * 12
            competitor_buyout_10yr = np.fv(rate, nper, 0, -hei_opportunity)  # Formula for Reverse Mortgage
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
            vesta_roi = vesta_buyout_10yr / estimated_value * 100  # Example formula
            
            # Display predictions side by side
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Vesta ROI Prediction (Static)")
                st.success(f"Static ROI for Vesta: {vesta_roi:.2f}%")
                st.write("**Input Data (Vesta):**")
                st.write(f"Vesta Buyout (10 years): ${vesta_buyout_10yr:,.2f}")
            with col2:
                st.subheader(f"{model_choice} ROI Prediction")
                st.success(f"Predicted ROI for {model_choice}: {competitor_roi:.2f}%")
                st.write("**Input Data (Competitor):**")
                st.write(competitor_data)
            
            # Visualization side by side
            st.subheader("Visualization of Key Metrics")
            col1, col2 = st.columns(2)
            with col1:
                labels = ['Estimated Value', 'Equity Value', 'HEI Opportunity', 'Mortgage Balance', 'Predicted ROI']
                values = [estimated_value, equity_value, hei_opportunity, mortgage_balance, vesta_roi]
                fig_vesta = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig_vesta.update_layout(
                    title_text="Vesta Metrics and Static ROI",
                    annotations=[dict(text='Vesta', x=0.5, y=0.5, font_size=20, showarrow=False)]
                )
                st.plotly_chart(fig_vesta)
            with col2:
                values = [estimated_value, equity_value, hei_opportunity, mortgage_balance, competitor_roi]
                fig_competitor = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig_competitor.update_layout(
                    title_text=f"{model_choice} Metrics and Predicted ROI",
                    annotations=[dict(text=model_choice, x=0.5, y=0.5, font_size=20, showarrow=False)]
                )
                st.plotly_chart(fig_competitor)
        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")
else:
    st.error("Failed to load competitor models. Please check the model files.")
