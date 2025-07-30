import os
import tempfile
import traceback
import time
import requests
import msal
from typing import List, Optional, Union
import pandas as pd
import logging
from functools import wraps


class SharePointUploader:
    """
    A class to handle file uploads to SharePoint using Microsoft Graph API.

    This class provides methods to upload various file types to SharePoint,
    create folders, and handle authentication with retry logic and proper
    resource cleanup.

    Attributes:
        client_id (str): Azure AD application client ID
        client_secret (str): Azure AD application client secret
        tenant_id (str): Azure AD tenant ID
        site_domain_name (str): SharePoint site domain name
        drive_name (str): SharePoint drive name
        logger (logging.Logger): Logger instance for tracking operations
        access_token (str): Microsoft Graph API access token
        drive_id (str): ID of the SharePoint drive being used
    """

    def __init__(self, client_id: str, client_secret: str, tenant_id: str,
                 site_domain_name: str, drive_name: str, logger=None):
        """
        Initialize SharePointUploader with authentication credentials.

        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID
            site_domain_name: SharePoint site domain name (e.g., 'contoso.sharepoint.com')
            drive_name: SharePoint drive/site name where files will be uploaded
            logger: Optional custom logger (defaults to basic console logger)

        Raises:
            Exception: If authentication fails or drive cannot be accessed
        """
        self.logger = logger or self._get_default_logger()
        self.logger.info("Initializing SharePointUploader")

        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.site_domain_name = site_domain_name
        self.drive_name = drive_name

        # These will be set during initialization
        self.access_token = None
        self.drive_id = None

        # Initialize connection
        self._initialize_connection()

    def _initialize_connection(self):
        """Establish connection to SharePoint by getting access token and drive ID."""
        try:
            self.access_token = self._get_access_token()
            self.drive_id = self._get_drive_id(self.drive_name)
            self.logger.info("SharePointUploader initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SharePointUploader: {str(e)}")
            raise

    def _get_default_logger(self) -> logging.Logger:
        """
        Create a basic console logger if none provided.

        Returns:
            logging.Logger: Configured logger instance
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _handle_api_errors(func):
        """
        Decorator to handle common API errors and implement retry logic.

        This decorator will:
        1. Retry the operation up to 3 times for transient errors
        2. Refresh the access token if it's expired
        3. Log detailed error information
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            max_retries = 3
            retry_delay = 5  # seconds

            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        self.logger.error(f"API request failed after {max_retries} attempts: {str(e)}")
                        raise

                    # Check if token might be expired (401 error)
                    if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                        self.logger.warning("Access token may be expired, refreshing...")
                        try:
                            self.access_token = self._get_access_token()
                        except Exception as token_error:
                            self.logger.error(f"Failed to refresh access token: {str(token_error)}")
                            raise

                    self.logger.warning(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                    time.sleep(retry_delay * (attempt + 1))

        return wrapper

    def _get_access_token(self) -> str:
        """
        Retrieve access token using MSAL.

        Returns:
            str: Access token for Microsoft Graph API

        Raises:
            Exception: If token retrieval fails
        """
        self.logger.info("Getting access token")
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
                client_credential=self.client_secret
            )
            token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

            if "access_token" not in token_response:
                error_msg = f"Failed to retrieve access token: {token_response.get('error_description', 'Unknown error')}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            self.logger.debug("Successfully obtained access token")
            return token_response["access_token"]
        except Exception as e:
            self.logger.error(f"Error in _get_access_token: {str(e)}")
            raise

    @_handle_api_errors
    def _get_drive_id(self, drive_name: str) -> str:
        """
        Get the drive ID for the given SharePoint site/drive name.

        Args:
            drive_name: Name of the SharePoint drive/site

        Returns:
            str: Drive ID

        Raises:
            Exception: If drive ID cannot be retrieved
        """
        try:
            self.logger.info(f"Getting drive ID for: '{drive_name}'")

            if not isinstance(drive_name, str):
                self.logger.warning(f"drive_name is not a string: {type(drive_name)}")
                drive_name = str(drive_name)

            site_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_domain_name}:/sites/{drive_name}"
            self.logger.debug(f"Using site URL: {site_url}")

            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(site_url, headers=headers)
            response.raise_for_status()

            site_id = response.json().get("id")
            if not site_id:
                raise Exception("Missing 'id' in site response")
            self.logger.info(f"Got site ID: {site_id}")

            drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
            self.logger.debug(f"Getting drive info from URL: {drive_url}")
            response = requests.get(drive_url, headers=headers)
            response.raise_for_status()

            drive_id = response.json().get("id")
            if not drive_id:
                raise Exception("Missing 'id' in drive response")
            self.logger.info(f"Got drive ID: {drive_id}")
            return str(drive_id)

        except Exception as e:
            self.logger.error(f"Error in _get_drive_id: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @_handle_api_errors
    def create_folder(self, folder_name: str, parent_folder_path: str = "") -> str:
        """
        Create a folder in SharePoint if it doesn't exist.

        Args:
            folder_name: Name of the folder to create
            parent_folder_path: Path to the parent folder (default is root)

        Returns:
            str: Full path of the created folder

        Raises:
            Exception: If folder creation fails
        """
        self.logger.info(f"Creating folder '{folder_name}' in '{parent_folder_path}'")

        full_path = f"{parent_folder_path}/{folder_name}" if parent_folder_path else folder_name

        # Check if folder already exists
        check_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{full_path}/children"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(check_url, headers=headers)
        
        if response.status_code == 200:
            self.logger.info(f"Folder '{folder_name}' already exists at '{full_path}'")
            return full_path
        elif response.status_code == 404:
            # Folder doesn't exist, create it
            folder_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{parent_folder_path}:/children"
            data = {
                "name": folder_name, 
                "folder": {}, 
                "@microsoft.graph.conflictBehavior": "fail"
            }

            response = requests.post(folder_url, headers=headers, json=data)
            response.raise_for_status()

            self.logger.info(f"Folder '{folder_name}' created at '{full_path}'")
            return full_path
        else:
            error_msg = f"Error checking/creating folder: {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    @_handle_api_errors
    def upload_file(self, file_path: str, folder_path: str = "", 
                   content_type: str = None, max_retries: int = 3) -> bool:
        """
        Upload any file type to SharePoint.

        Args:
            file_path: Local path to the file to upload
            folder_path: Target folder path in SharePoint (default is root)
            content_type: MIME type of the file (autodetected if None)
            max_retries: Maximum number of upload attempts (default 3)

        Returns:
            bool: True if upload succeeded, False otherwise

        Raises:
            Exception: If upload fails after all retries
            FileNotFoundError: If source file doesn't exist
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        self.logger.info(f"Uploading file '{file_name}' to '{folder_path}'")

        upload_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{folder_path}/{file_name}:/content"

        if not content_type:
            content_type = self._get_content_type(file_name)
            self.logger.debug(f"Detected content type: {content_type}")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": content_type,
        }

        for attempt in range(max_retries):
            try:
                with open(file_path, "rb") as file:
                    response = requests.put(upload_url, headers=headers, data=file)
                    response.raise_for_status()

                self.logger.info(f"File '{file_name}' uploaded successfully")
                return True
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < max_retries - 1:
                    self.logger.warning("Access token may be expired, refreshing...")
                    self.access_token = self._get_access_token()
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    continue
                
                if attempt == max_retries - 1:
                    error_msg = f"Failed to upload '{file_name}' after {max_retries} attempts: {str(e)}"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)
                
                self.logger.warning(f"Retry {attempt + 1}/{max_retries} for file '{file_name}'")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                error_msg = f"Unexpected error uploading '{file_name}': {str(e)}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

        return False

    def upload_docx(self, file_paths: List[str], folder_path: str = "") -> bool:
        """
        Upload multiple .docx files to SharePoint.

        Args:
            file_paths: List of paths to .docx files
            folder_path: Target folder path in SharePoint (default is root)

        Returns:
            bool: True if all files uploaded successfully, False otherwise
        """
        self.logger.info(f"Uploading {len(file_paths)} docx files to '{folder_path}'")
        results = []
        
        for file_path in file_paths:
            try:
                success = self.upload_file(
                    file_path, 
                    folder_path, 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                results.append(success)
            except Exception as e:
                self.logger.error(f"Failed to upload {file_path}: {str(e)}")
                results.append(False)
        
        return all(results)

    def upload_dataframe_as_csv(self, dataframe: pd.DataFrame, file_name: str, 
                              folder_path: str = "", **csv_kwargs) -> bool:
        """
        Upload a pandas DataFrame as a CSV file to SharePoint.

        Args:
            dataframe: pandas DataFrame to upload
            file_name: Name for the CSV file (will add .csv if missing)
            folder_path: Target folder path in SharePoint (default is root)
            **csv_kwargs: Additional arguments to pass to DataFrame.to_csv()

        Returns:
            bool: True if upload succeeded, False otherwise
        """
        self.logger.info(f"Uploading DataFrame as CSV to SharePoint: {file_name}")

        # Ensure file_name has .csv extension
        if not file_name.lower().endswith('.csv'):
            file_name = f"{file_name}.csv"
            self.logger.info(f"Added .csv extension to filename: {file_name}")

        # Create and manage temporary file
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as temp_file:
                temp_path = temp_file.name
                dataframe.to_csv(temp_file, index=False, **csv_kwargs)
                self.logger.debug(f"DataFrame saved to temporary file: {temp_path}")

            # Ensure the file is closed before uploading
            if temp_path and os.path.exists(temp_path):
                return self.upload_file(temp_path, folder_path, "text/csv")
            return False
        except Exception as e:
            self.logger.error(f"Error uploading DataFrame: {str(e)}")
            return False
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    self.logger.debug("Temporary file deleted successfully")
                except Exception as delete_error:
                    self.logger.warning(f"Could not delete temporary file: {str(delete_error)}")

    def _get_content_type(self, filename: str) -> str:
        """
        Get content type based on file extension.

        Args:
            filename: Name of the file

        Returns:
            str: Corresponding MIME type or 'application/octet-stream' if unknown
        """
        extension = os.path.splitext(filename)[1].lower()
        content_types = {
            '.csv': 'text/csv',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
            '.zip': 'application/zip',
            '.json': 'application/json',
        }
        return content_types.get(extension, 'application/octet-stream')
    