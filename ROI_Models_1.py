import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt
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

# Load the Vesta model
vesta_model = load_model('vesta_model.pkl')

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

# Ensure both models are loaded
if vesta_model and competitor_model:
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
    
    # Calculate Vesta Buyout (10 years)
    vesta_buyout_10yr = ((1 - 0.15) * estimated_value) * (1 + 0.04) ** 10
    
    # Function to calculate competitor buyout based on competitor
    def calculate_competitor_buyout(competitor, estimated_value):
        if competitor == 'HELOC ROI':
            competitor_buyout_10yr = estimated_value * (1 + 0.05) ** 10  # Example formula
        elif competitor == 'Reverse Mortgage':
            competitor_buyout_10yr = estimated_value * (1 + 0.03) ** 10
        elif competitor == 'Unison':
            competitor_buyout_10yr = estimated_value * (1 + 0.045) ** 10
        elif competitor == 'Point':
            competitor_buyout_10yr = estimated_value * (1 + 0.04) ** 10
        elif competitor == 'Haus':
            competitor_buyout_10yr = estimated_value * (1 + 0.035) ** 10
        elif competitor == 'Homium':
            competitor_buyout_10yr = estimated_value * (1 + 0.05) ** 10
        else:
            competitor_buyout_10yr = 0
        return competitor_buyout_10yr

    # Calculate competitor buyout
    competitor_buyout_10yr = calculate_competitor_buyout(model_choice, estimated_value)
    
    # Prepare data for Vesta model
    vesta_data = pd.DataFrame({
        'Estimated_Value': [estimated_value],
        'Equity_Value': [equity_value],
        'HEI Opportunity': [hei_opportunity],
        'Morgage Balance': [mortgage_balance],
        'Vesta_Buyout_10yr': [vesta_buyout_10yr]
    })
    
    # Prepare data for competitor model
    if model_choice == "HELOC ROI":
        competitor_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Morgage Balance': [mortgage_balance],
            'HELOC_Cost_10yr': [competitor_buyout_10yr],
            'Vesta_Buyout_10yr': [vesta_buyout_10yr]
        })
    elif model_choice == "Reverse Mortgage":
        competitor_data = pd.DataFrame({
            'Estimated_Value': [estimated_value],
            'Equity_Value': [equity_value],
            'HEI Opportunity': [hei_opportunity],
            'Morgage Balance': [mortgage_balance],
            'Reverse_Mortgage_Cost_10yr': [competitor_buyout_10yr],
            'Vesta_Buyout_10yr': [vesta_buyout_10yr]
        })
    # Add similar blocks for other competitors...
    else:
        # Generic case for other competitors
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
            # Vesta prediction
            vesta_prediction = vesta_model.predict(vesta_data.values)
            vesta_roi = vesta_prediction[0]
            
            # Competitor prediction
            competitor_prediction = competitor_model.predict(competitor_data.values)
            competitor_roi = competitor_prediction[0]
            
            # Display predictions side by side
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Vesta ROI Prediction")
                st.success(f"Predicted ROI for Vesta: ${vesta_roi:,.2f}")
                st.write("**Input Data:**")
                st.write(vesta_data)
            with col2:
                st.subheader(f"{model_choice} ROI Prediction")
                st.success(f"Predicted ROI for {model_choice}: ${competitor_roi:,.2f}")
                st.write("**Input Data:**")
                st.write(competitor_data)
            
            # Visualization side by side
            st.subheader("Visualization of Key Metrics")
            col1, col2 = st.columns(2)
            with col1:
                labels = ['Estimated Value', 'Equity Value', 'HEI Opportunity', 'Mortgage Balance', 'Predicted ROI']
                values = [estimated_value, equity_value, hei_opportunity, mortgage_balance, vesta_roi]
                fig_vesta = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig_vesta.update_layout(
                    title_text="Vesta Metrics and Predicted ROI",
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
    st.error("Failed to load models. Please check the model files.")
