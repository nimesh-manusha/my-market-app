import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
import json

st.set_page_config(
    page_title="Online Retail Data Dashboard",
    page_icon="🛒",
    layout="wide"
)

@st.cache_data
def load_data():
    return pd.read_csv('data/cleaned_data.csv')

df = load_data()

def show_cleaned_data():
    st.header("🧹 Cleaned Data Preview")
    st.write("Preview of the cleaned dataset used for analysis and modeling.")
    st.dataframe(df.head(30), use_container_width=True)
    st.markdown("---")
    st.subheader("Summary Statistics")
    st.dataframe(df.describe(include='all').T, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Cleaned Data as CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")

def show_data_processing():
    st.header("🔧 Data Processing Steps")
    st.write("""
    **Main steps in data cleaning and processing:**
    1. Removed duplicates and missing values
    2. Standardized column names and formats
    3. Feature engineering (e.g., price per item, extracting date parts)
    4. Encoded categorical variables for modeling
    5. Saved cleaned data to `cleaned_data.csv`
    """)
    st.markdown("---")
    st.subheader("Before & After Cleaning (Sample)")
    # Optionally, show a before/after if you have raw data
    st.info("Raw data preview not available. Showing cleaned data sample instead.")
    st.dataframe(df.sample(10), use_container_width=True)

def show_data_visualisation():
    st.header("📊 Data Visualization")
    st.write("Explore sales, customer, and product trends interactively.")
    with st.sidebar:
        st.header("Filter Data")
        year = st.selectbox("Year", options=sorted(df['Year'].unique()), index=0)
        category = st.multiselect("Category", options=sorted(df['category_name'].unique()), default=list(df['category_name'].unique()))
        city = st.multiselect("City", options=sorted(df['city'].unique()), default=list(df['city'].unique()))
    filtered = df[(df['Year'] == year) & (df['category_name'].isin(category)) & (df['city'].isin(city))]
    st.subheader("Sales by Category")
    cat_sales = filtered.groupby('category_name')['price'].sum().reset_index().sort_values('price', ascending=False)
    fig1 = px.bar(cat_sales, x='category_name', y='price', color='category_name', title='Total Sales by Category', labels={'price': 'Total Sales', 'category_name': 'Category'})
    st.plotly_chart(fig1, use_container_width=True)
    st.subheader("Sales Over Time (Monthly)")
    monthly = filtered.groupby(['Year', 'Month'])['price'].sum().reset_index()
    fig2 = px.line(monthly, x='Month', y='price', color='Year', markers=True, title='Monthly Sales', labels={'price': 'Total Sales', 'Month': 'Month'})
    st.plotly_chart(fig2, use_container_width=True)
    st.subheader("Customer Demographics")
    col6, col7 = st.columns(2)
    with col6:
        gender_counts = filtered['gender'].value_counts().reset_index()
        fig3 = px.pie(gender_counts, names='index', values='gender', title='Gender Distribution')
        st.plotly_chart(fig3, use_container_width=True)
    with col7:
        age_hist = px.histogram(filtered, x='age', nbins=20, title='Age Distribution')
        st.plotly_chart(age_hist, use_container_width=True)

def show_model_training():
    st.header("🤖 Model Training & Evaluation")
    st.write("""
    The machine learning model was trained to predict sales using features from the cleaned dataset. Below are the model's performance metrics and prediction interface.
    """)
    try:
        with open('model/model_metadata.json') as f:
            metadata = json.load(f)
        st.subheader("Model Performance Metrics")
        st.metric("Mean Absolute Error (MAE)", f"${metadata['performance']['MAE']:,.2f}")
        st.metric("Root Mean Squared Error (RMSE)", f"${metadata['performance']['RMSE']:,.2f}")
        st.metric("R-squared (R²)", f"{metadata['performance']['R2']:.3f}")
        st.write(f"**Algorithm:** {metadata['model_type']}")
        st.write(f"**Version:** {metadata['version']}")
        st.subheader("Model Features")
        st.write("**Categorical Features:**")
        st.write(metadata['features']['categorical'])
        st.write("**Numeric Features:**")
        st.write(metadata['features']['numeric'])
    except Exception:
        st.warning("Model metadata not found. Please ensure the model is trained and metadata is available.")
    st.markdown("---")
    st.subheader("Try a Prediction")
    try:
        with open('model/model.pkl', 'rb') as f:
            artifacts = pickle.load(f)
        model = artifacts['model']
        preprocessor = artifacts['preprocessor']
        # Use sample values from data for UI
        col1, col2 = st.columns(2)
        with col1:
            category_name = st.selectbox("Category Name", options=sorted(df['category_name'].dropna().unique()))
            product_name = st.selectbox("Product Name", options=sorted(df['product_name'].dropna().unique()))
            quantity = st.number_input("Quantity", min_value=1, max_value=100, value=1, step=1)
            price = st.number_input("Price", min_value=1.0, max_value=10000.0, value=100.0, step=1.0)
            price_per_item = st.number_input("Price per Item", min_value=0.1, max_value=10000.0, value=100.0, step=0.1)
        with col2:
            payment_method = st.selectbox("Payment Method", options=sorted(df['payment_method'].dropna().unique()))
            city = st.selectbox("City", options=sorted(df['city'].dropna().unique()))
            gender = st.radio("Customer Gender", options=sorted(df['gender'].dropna().unique()), horizontal=True)
            age = st.number_input("Customer Age", min_value=int(df['age'].min()), max_value=int(df['age'].max()), value=int(df['age'].mean()), step=1)
        if st.button("Predict Sales", type="primary"):
            input_data = pd.DataFrame({
                'category_name': [category_name],
                'product_name': [product_name],
                'quantity': [quantity],
                'price': [price],
                'payment_method': [payment_method],
                'city': [city],
                'gender': [gender],
                'age': [age],
                'price_per_item': [price_per_item]
            })
            X_new = preprocessor.transform(input_data)
            prediction = model.predict(X_new)[0]
            st.success(f"Predicted Total Sales: **${prediction:,.2f}**")
    except Exception:
        st.info("Model not available for prediction. Please train and save the model.")

# --- Main Navigation Tabs ---
st.title("Online Retail Data Dashboard")
tab1, tab2, tab3, tab4 = st.tabs([
    "Cleaned Data", "Data Processing", "Data Visualization", "Model Training"
])
with tab1:
    show_cleaned_data()
with tab2:
    show_data_processing()
with tab3:
    show_data_visualisation()
with tab4:
    show_model_training()

