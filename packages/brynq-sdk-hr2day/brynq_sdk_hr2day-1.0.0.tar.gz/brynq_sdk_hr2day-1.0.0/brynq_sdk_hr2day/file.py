from typing import Optional, Dict, Any, Union, BinaryIO, List
import os
import json
from datetime import datetime
import requests
from brynq_sdk_functions import Functions
from .schemas.file import (
    FileContentResponseSchema,
    FileMetadataRequestSchema,
    FileMetadataResponseSchema,
    FileMetadataSchema
)


class File:
    """
    Handles file operations for HR2Day API.
    File operations include uploading file content and linking metadata.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the File class.

        Args:
            hr2day_instance: The HR2Day class instance.
        """
        self.hr2day = hr2day_instance

    def upload_content(self, 
                      file_path: Optional[str] = None, 
                      file_content: Optional[Union[bytes, BinaryIO]] = None,
                      file_name: Optional[str] = None,
                      parent_id: Optional[str] = None) -> requests.Response:
        """
        Upload file content to HR2Day.
        
        Args:
            file_path (str, optional): Path to the file to upload. Required if file_content is not provided.
                            Example: "/home/user/documents/contract.pdf"
            file_content (Union[bytes, BinaryIO], optional): File content as bytes or file-like object. Required if file_path is not provided.
                            Example: open("/home/user/file.pdf", "rb").read()
            file_name (str, optional): Name of the file. Required if file_content is provided.
                            Example: "document.pdf"
            parent_id (str, optional): ID of the parent object to link the file to (e.g., employee ID).
            
        Returns:
            Dict[str, Any]: Response from the API containing contentVersionId if successful
            
        Raises:
            ValueError: If required parameters are missing or invalid
            requests.HTTPError: When the HTTP request fails
        """
        # Validate input parameters
        if file_path is None and file_content is None:
            raise ValueError("Either file_path or file_content must be provided")
            
        if file_content is not None and file_name is None:
            raise ValueError("file_name is required when providing file_content")
            
        # Prepare file content
        if file_path is not None:
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
                
            file_name = file_name or os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                file_content = f.read()
        
        # URL encode the file name
        import urllib.parse
        encoded_file_name = urllib.parse.quote(file_name, encoding='utf-8')
        
        # Prepare headers
        headers = {
            'title': encoded_file_name,
            'requesterId': self.hr2day.requester_id
        }
        
        if parent_id:
            headers['parentId'] = parent_id
            
        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/apexrest/hr2d/filecontent"
        
        # Send PUT request
        response = self.hr2day.session.put(
            url=url,
            headers=headers,
            data=file_content
        )
        
        # Error handling
        response.raise_for_status()

        return response
        
    def link_metadata(self, 
                     content_version_id: str,
                     key_type: str,
                     key_value: str,
                     employer: Optional[str] = None,
                     document_category: Optional[str] = None,
                     original_created_date: Optional[datetime] = None,
                     external_key: Optional[str] = None,
                     limited_access: Optional[bool] = None,
                     allowed_document_profiles: Optional[str] = None,
                     document_profile_mode: Optional[str] = None,
                     alternative_owner_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Link metadata to a previously uploaded file.
        
        Args:
            content_version_id (str): ID of the file content from FileContent upload
            key_type (str): Type of key used to identify the employee (EMPLOYEEID, BSN, EMPLOYEENR, EMPLOYEENRALTERNATIVE, EMPLOYEEKEY)
            key_value (str): Value of the field selected by keyType
            employer (str, optional): Employer name (mandatory except for keyType EMPLOYEEID)
            document_category (str, optional): Document category (e.g., 'Other', 'Leave', etc.)
            original_created_date (datetime, optional): Original creation date of the file
            external_key (str, optional): External reference key for the file
            limited_access (bool, optional): Indicates if document is only displayed for certain document profiles
            allowed_document_profiles (str, optional): Names of document profiles with access, separated by ~
            document_profile_mode (str, optional): Document profile mode (MEDEWERKER or STANDARD PROFILE)
            alternative_owner_id (str, optional): Specific user ID who becomes the owner of the file
            
        Returns:
            Dict[str, Any]: Response from the API containing fileId if successful
            
        Raises:
            ValueError: If required parameters are missing or invalid
            requests.HTTPError: When the HTTP request fails
        """
        # Prepare file metadata
        file_metadata = {}
        
        if document_category:
            file_metadata["hr2d__DocumentCategory__c"] = document_category
            
        if original_created_date:
            file_metadata["hr2d__OriginalRecordCreatedDate__c"] = original_created_date
            
        if external_key:
            file_metadata["hr2d__Key__c"] = external_key
            
        if limited_access is not None:
            file_metadata["hr2d__limitedAccess__c"] = limited_access
            
        if allowed_document_profiles:
            file_metadata["hr2d__AllowedDocumentProfiles__c"] = allowed_document_profiles
            
        # Create request data
        request_data = {
            "request": {
                "requesterId": self.hr2day.requester_id,
                "contentVersionId": content_version_id,
                "keyType": key_type.upper(),
                "keyValue": key_value,
                "file": file_metadata
            }
        }
        
        # Add optional fields
        if employer:
            request_data["request"]["employer"] = employer
            
        if document_profile_mode:
            request_data["request"]["documentProfileMode"] = document_profile_mode
            
        if alternative_owner_id:
            request_data["request"]["alternativeOwnerId"] = alternative_owner_id
            
        # Validate request data
        try:
            # Extract the request part for validation
            request_part = request_data["request"]
            valid_data, _ = Functions.validate_pydantic_data(request_part, FileMetadataRequestSchema)
        except Exception as e:
            raise ValueError(f"Invalid file metadata: {str(e)}")
            
        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/apexrest/hr2d/file"
        request_body = json.dumps(valid_data[0], default=self.hr2day.datetime_converter)

        # Send POST request
        response = self.hr2day.session.post(
            url=url,
            data=request_body
        )
        
        # Error handling
        response.raise_for_status()
        
        # Parse and validate response
        return response
        
    def upload(self, 
              file_path: Optional[str] = None,
              file_content: Optional[Union[bytes, BinaryIO]] = None,
              file_name: Optional[str] = None,
              key_type: str = "EMPLOYEEID",
              key_value: str = None,
              employer: Optional[str] = None,
              document_category: Optional[str] = None,
              original_created_date: Optional[datetime] = None,
              external_key: Optional[str] = None,
              parent_id: Optional[str] = None,
              limited_access: Optional[bool] = None,
              allowed_document_profiles: Optional[str] = None,
              document_profile_mode: Optional[str] = None,
              alternative_owner_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to HR2Day and link metadata in a single operation.
        
        Args:
            file_path (str, optional): Path to the file to upload. Required if file_content is not provided.
            file_content (Union[bytes, BinaryIO], optional): File content as bytes or file-like object. Required if file_path is not provided.
            file_name (str, optional): Name of the file. Required if file_content is provided.
            key_type (str): Type of key used to identify the employee (EMPLOYEEID, BSN, EMPLOYEENR, EMPLOYEENRALTERNATIVE, EMPLOYEEKEY)
            key_value (str): Value of the field selected by keyType
            employer (str, optional): Employer name (mandatory except for keyType EMPLOYEEID)
            document_category (str, optional): Document category (e.g., 'Other', 'Leave', etc.)
            original_created_date (datetime, optional): Original creation date of the file
            external_key (str, optional): External reference key for the file
            parent_id (str, optional): ID of the parent object to link the file to (e.g., employee ID)
            limited_access (bool, optional): Indicates if document is only displayed for certain document profiles
            allowed_document_profiles (str, optional): Names of document profiles with access, separated by ~
            document_profile_mode (str, optional): Document profile mode (MEDEWERKER or STANDARD PROFILE)
            alternative_owner_id (str, optional): Specific user ID who becomes the owner of the file
            
        Returns:
            Dict[str, Any]: Dictionary containing both content upload and metadata linking responses
            
        Raises:
            ValueError: If required parameters are missing or invalid
            requests.HTTPError: When the HTTP request fails
        """
        if key_value is None:
            raise ValueError("key_value is required")
            
        # Step 1: Upload file content
        response = self.upload_content(
            file_path=file_path,
            file_content=file_content,
            file_name=file_name,
            parent_id=parent_id
        )
        
        # Get content version ID from response
        content = response.json()
        content_version_id = content.get('contentVersionId',"aa")

        if not content_version_id:
            raise ValueError("File content upload failed: No contentVersionId returned")
            
        # Step 2: Link metadata
        metadata_response = self.link_metadata(
            content_version_id=content_version_id,
            key_type=key_type,
            key_value=key_value,
            employer=employer,
            document_category=document_category,
            original_created_date=original_created_date,
            external_key=external_key,
            limited_access=limited_access,
            allowed_document_profiles=allowed_document_profiles,
            document_profile_mode=document_profile_mode,
            alternative_owner_id=alternative_owner_id
        )
        
        # Combine responses
        return {
            "content_upload": content,
            "metadata_linking": metadata_response
        } 