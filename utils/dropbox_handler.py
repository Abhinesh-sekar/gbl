# utils/dropbox_handler.py
import dropbox
from dropbox.exceptions import ApiError, AuthError
import os

def test_connection(access_token):
    """
    Test Dropbox connection with the provided access token
    
    Args:
        access_token (str): Dropbox access token
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    
    try:
        dbx = dropbox.Dropbox(access_token)
        # Try to get account info to test connection
        dbx.users_get_current_account()
        return True
    except AuthError:
        return False
    except Exception:
        return False

def upload_to_dropbox(local_file_path, access_token, dropbox_folder, filename):
    """
    Upload a file to Dropbox
    
    Args:
        local_file_path (str): Path to the local file
        access_token (str): Dropbox access token
        dropbox_folder (str): Dropbox folder path
        filename (str): Name for the file in Dropbox
    
    Returns:
        bool: True if upload successful, False otherwise
    """
    
    try:
        # Initialize Dropbox client
        dbx = dropbox.Dropbox(access_token)
        
        # Ensure dropbox folder starts with '/'
        if not dropbox_folder.startswith('/'):
            dropbox_folder = '/' + dropbox_folder
        
        # Ensure dropbox folder ends with '/'
        if not dropbox_folder.endswith('/'):
            dropbox_folder += '/'
        
        # Create full dropbox path
        dropbox_path = dropbox_folder + filename
        
        # Read and upload file
        with open(local_file_path, 'rb') as file:
            file_size = os.path.getsize(local_file_path)
            
            # For files smaller than 150MB, use simple upload
            if file_size <= 150 * 1024 * 1024:  # 150MB
                dbx.files_upload(
                    file.read(),
                    dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite,
                    autorename=True
                )
            else:
                # For larger files, use session upload
                upload_session_start_result = dbx.files_upload_session_start(
                    file.read(4 * 1024 * 1024)  # 4MB chunks
                )
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=file.tell()
                )
                
                # Upload remaining chunks
                while file.tell() < file_size:
                    chunk = file.read(4 * 1024 * 1024)
                    if len(chunk) <= 4 * 1024 * 1024:
                        dbx.files_upload_session_finish(
                            chunk,
                            cursor,
                            dropbox.files.CommitInfo(path=dropbox_path)
                        )
                        break
                    else:
                        dbx.files_upload_session_append_v2(chunk, cursor)
                        cursor.offset = file.tell()
        
        return True
        
    except AuthError:
        print("Authentication failed. Check your access token.")
        return False
    except ApiError as e:
        print(f"API error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def create_folder(access_token, folder_path):
    """
    Create a folder in Dropbox
    
    Args:
        access_token (str): Dropbox access token
        folder_path (str): Path of the folder to create
    
    Returns:
        bool: True if folder created successfully, False otherwise
    """
    
    try:
        dbx = dropbox.Dropbox(access_token)
        
        # Ensure folder path starts with '/'
        if not folder_path.startswith('/'):
            folder_path = '/' + folder_path
        
        dbx.files_create_folder_v2(folder_path)
        return True
        
    except ApiError as e:
        # Folder might already exist
        if e.error.is_path() and e.error.get_path().is_conflict():
            return True  # Folder already exists
        else:
            print(f"Error creating folder: {e}")
            return False
    except Exception as e:
        print(f"Unexpected error creating folder: {e}")
        return False

def list_files(access_token, folder_path=""):
    """
    List files in a Dropbox folder
    
    Args:
        access_token (str): Dropbox access token
        folder_path (str): Path of the folder to list
    
    Returns:
        list: List of file names, empty list if error
    """
    
    try:
        dbx = dropbox.Dropbox(access_token)
        
        # Ensure folder path starts with '/' but handle root folder
        if folder_path and not folder_path.startswith('/'):
            folder_path = '/' + folder_path
        elif not folder_path:
            folder_path = ''
        
        result = dbx.files_list_folder(folder_path)
        files = []
        
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                files.append(entry.name)
        
        return files
        
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def get_download_link(access_token, file_path):
    """
    Get a temporary download link for a file in Dropbox
    
    Args:
        access_token (str): Dropbox access token
        file_path (str): Path to the file in Dropbox
    
    Returns:
        str: Download link or None if error
    """
    
    try:
        dbx = dropbox.Dropbox(access_token)
        
        # Ensure file path starts with '/'
        if not file_path.startswith('/'):
            file_path = '/' + file_path
        
        link = dbx.files_get_temporary_link(file_path)
        return link.link
        
    except Exception as e:
        print(f"Error getting download link: {e}")
        return None