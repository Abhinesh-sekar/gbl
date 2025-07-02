import streamlit as st

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "name"

# Function to navigate to next page
def next_page(current):
    if current == "name":
        st.session_state.page = "age"
    elif current == "age":
        st.session_state.page = "qualification"
    elif current == "qualification":
        st.session_state.page = "summary"

# Page 1: Name
if st.session_state.page == "name":
    st.title("Step 1: Enter your Name")
    name = st.text_input("Name", key="name_input")
    if st.button("Next"):
        if name:
            st.session_state.name = name
            next_page("name")
        else:
            st.warning("Please enter your name.")

# Page 2: Age
elif st.session_state.page == "age":
    st.title("Step 2: Enter your Age")
    age = st.number_input("Age", min_value=0, step=1, key="age_input")
    if st.button("Next"):
        st.session_state.age = age
        next_page("age")

# Page 3: Qualification
elif st.session_state.page == "qualification":
    st.title("Step 3: Enter your Qualification")
    qualification = st.text_input("Qualification", key="qual_input")
    if st.button("Next"):
        if qualification:
            st.session_state.qualification = qualification
            next_page("qualification")
        else:
            st.warning("Please enter your qualification.")

# Final Page: Summary
elif st.session_state.page == "summary":
    st.title("Summary of Your Input")
    st.write(f"**Name:** {st.session_state.name}")
    st.write(f"**Age:** {st.session_state.age}")
    st.write(f"**Qualification:** {st.session_state.qualification}")
    st.success("Thank you! 🎉")
