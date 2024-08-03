import streamlit as st

# Initialize session state
if 'view' not in st.session_state:
    st.session_state.view = 'main'

def switch_to_secondary():
    st.session_state.view = 'secondary'

def switch_to_main():
    st.session_state.view = 'main'

# Main view
def main_view():
    st.title("Main View")
    st.write("This is the main view of the app.")
    if st.button("Go to Secondary View"):
        switch_to_secondary()

# Secondary view
def secondary_view():
    st.title("Secondary View")
    st.write("This is the secondary view of the app.")
    if st.button("Back to Main View"):
        switch_to_main()

# Conditional rendering based on session state
if st.session_state.view == 'main':
    main_view()
elif st.session_state.view == 'secondary':
    secondary_view()