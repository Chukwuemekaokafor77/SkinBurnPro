import streamlit as st
import requests

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = None

# Define the login function
def login(username, password):
    try:
        response = requests.post("http://api:8000/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.token = response.json().get("access_token")
            return True
        else:
            st.error("Login failed. Please check your username and password.")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the backend. Please check your connection.")
        return False

# Define the register function
def register(username, password):
    try:
        response = requests.post("http://api:8000/register", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Registration successful! You can now log in.")
            return True
        else:
            st.error("Registration failed. Please try again.")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the backend. Please check your connection.")
        return False

# Define the logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.token = None

# Main app structure with tabs for Login and Register
if not st.session_state.logged_in:
    st.title("Burn Classification Dashboard")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(username, password):
                st.success("Login successful!")

    with tab2:
        st.subheader("Register")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register(new_username, new_password):
                st.success("Registration successful! You can now log in.")

else:
    # Main application content
    st.title("Burn Classification Dashboard")

    uploaded_file = st.file_uploader("Upload an image for classification", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        st.write("Classifying...")

        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.post("http://api:8000/predict", files={"file": uploaded_file.getvalue()}, headers=headers)

            if response.status_code == 200:
                result = response.json()
                st.write(f"Predicted Class: {result['classification']['predicted_class']}")
                st.write(f"Confidence: {result['classification']['confidence']:.2f}")

                # Example: st.download_button("Download Report", data=report_data, file_name="report.xlsx")
            else:
                st.error("Error during prediction. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to the backend. Please check your connection.")

    if st.button("Logout"):
        logout()

# Disclaimer
st.write("### Disclaimer")
st.write("This application is strictly for academic purposes and is not intended to replace medical care.")
