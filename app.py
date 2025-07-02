import streamlit as st
import os
from datetime import datetime
from utils.data_collection import collect_user_data
from utils.cv_generator import generate_cv_pdf
from utils.encryption import encrypt_pdf
from utils.dropbox_handler import upload_to_dropbox
from utils.auth import check_authentication, logout

def main():
    st.set_page_config(
        page_title="CV Generator",
        page_icon="📄",
        layout="wide"
    )
    
    # Check authentication first
    if not check_authentication():
        return
    
    # Show logout option in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", help="Logout and return to authentication"):
            logout()
            st.rerun()
    
    st.title("📄 Professional CV Generator")
    st.markdown("---")
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    
    # Sidebar for Dropbox configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        dropbox_token = st.text_input("Dropbox Access Token", type="password")
        dropbox_folder = st.text_input("Dropbox Folder Path", value="/CVs")
        
        if st.button("Test Dropbox Connection"):
            if dropbox_token:
                try:
                    from utils.dropbox_handler import test_connection
                    if test_connection(dropbox_token):
                        st.success("✅ Dropbox connection successful!")
                    else:
                        st.error("❌ Dropbox connection failed!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter Dropbox access token")
    
    # Main application flow
    if st.session_state.step == 1:
        st.header("📝 Personal Information")
        user_data = collect_user_data()
        
        if user_data and st.button("Generate CV", type="primary"):
            st.session_state.user_data = user_data
            st.session_state.step = 2
            st.rerun()
    
    elif st.session_state.step == 2:
        st.header("🔄 Generating Your CV...")
        
        try:
            # Generate CV PDF
            with st.spinner("Creating PDF..."):
                pdf_path = generate_cv_pdf(st.session_state.user_data)
            
            # Encrypt PDF with DOB
            with st.spinner("Securing PDF..."):
                dob = st.session_state.user_data['dob']
                password = dob.strftime("%d%m%Y")  # Format: DDMMYYYY
                encrypted_pdf_path = encrypt_pdf(pdf_path, password)
            
            # Generate filename
            name = st.session_state.user_data['name'].replace(" ", "-")
            phone = st.session_state.user_data['phone']
            final_filename = f"{name}-{phone}.pdf"
            
            # Rename file
            final_path = os.path.join(os.path.dirname(encrypted_pdf_path), final_filename)
            os.rename(encrypted_pdf_path, final_path)
            
            st.success("✅ CV generated successfully!")
            
            # Display download option
            with open(final_path, "rb") as file:
                st.download_button(
                    label="📥 Download CV",
                    data=file.read(),
                    file_name=final_filename,
                    mime="application/pdf"
                )
            
            # Upload to Dropbox if configured
            if dropbox_token and dropbox_folder:
                with st.spinner("Uploading to Dropbox..."):
                    success = upload_to_dropbox(final_path, dropbox_token, dropbox_folder, final_filename)
                    if success:
                        st.success("✅ CV uploaded to Dropbox successfully!")
                    else:
                        st.error("❌ Failed to upload to Dropbox")
            
            # Show CV details
            st.info(f"🔐 PDF Password: {password} (Your Date of Birth in DDMMYYYY format)")
            
            # Clean up temporary files
            try:
                os.remove(pdf_path)
                os.remove(final_path)
            except:
                pass
            
            if st.button("Generate Another CV"):
                st.session_state.step = 1
                st.session_state.user_data = {}
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error generating CV: {str(e)}")
            if st.button("Try Again"):
                st.session_state.step = 1
                st.rerun()

if __name__ == "__main__":
    main()