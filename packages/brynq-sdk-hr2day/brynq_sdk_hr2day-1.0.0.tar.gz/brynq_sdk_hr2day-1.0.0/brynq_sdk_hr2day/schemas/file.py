from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class FileContentResponseSchema(BaseModel):
    """Schema for the response from the RestFileContent API."""
    requestId: Optional[str] = Field(None, description="Logging ID (not yet implemented)")
    requesterId: str = Field(..., description="The requesterId used for the API call")
    errors: Optional[str] = Field(None, description="Errors, empty if there are no errors")
    contentVersionId: Optional[str] = Field(None, description="ID of the created file if upload was successful")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class FileMetadataSchema(BaseModel):
    """Schema for file metadata in HR2Day API."""
    hr2d__DocumentCategory__c: Optional[str] = Field(None, description="Document category (e.g., 'Other', 'Leave', etc.)")
    hr2d__OriginalRecordCreatedDate__c: Optional[datetime] = Field(None, description="Original creation date of the file")
    hr2d__Key__c: Optional[str] = Field(None, description="External reference key for the file")
    hr2d__limitedAccess__c: Optional[bool] = Field(None, description="Indicates if document is only displayed for certain document profiles")
    hr2d__AllowedDocumentProfiles__c: Optional[str] = Field(None, description="Names of document profiles with access, separated by ~")

    class Config:
        """Pydantic configuration"""
        frozen = False
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "forbid"


class FileMetadataRequestSchema(BaseModel):
    """Schema for file metadata request in HR2Day API."""
    requesterId: str = Field(..., description="Requester ID provided by HR2Day")
    contentVersionId: str = Field(..., description="ID of the file content from FileContent upload")
    employer: Optional[str] = Field(None, description="Employer name (mandatory except for keyType EMPLOYEEID)")
    keyType: Literal["EMPLOYEEID", "BSN", "EMPLOYEENR", "EMPLOYEENRALTERNATIVE", "EMPLOYEEKEY"] = Field(..., description="Type of key used to identify the employee")
    keyValue: str = Field(..., description="Value of the field selected by keyType")
    documentProfileMode: Optional[Literal["MEDEWERKER", "STANDARD PROFILE"]] = Field(None, description="Document profile mode")
    alternativeOwnerId: Optional[str] = Field(None, description="Specific user ID who becomes the owner of the file")
    file: FileMetadataSchema = Field(..., description="File metadata")

    @model_validator(mode='after')
    def validate_employer(self):
        """Validate that employer is provided when keyType is not EMPLOYEEID."""
        if self.keyType != "EMPLOYEEID" and not self.employer:
            raise ValueError("Employer is mandatory when keyType is not EMPLOYEEID")
        return self

    class Config:
        """Pydantic configuration"""
        frozen = False
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "forbid"


class FileMetadataResponseSchema(BaseModel):
    """Schema for the response from the RestFile API."""
    requestId: Optional[str] = Field(None, description="Logging ID (not yet implemented)")
    requesterId: str = Field(..., description="The requesterId used for the API call")
    errors: Optional[str] = Field(None, description="Errors, empty if there are no errors")
    fileId: Optional[str] = Field(None, description="ID of the created file if metadata was successfully processed")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class FileSchema(BaseModel):
    """Schema for hr2d__File__c entity in HR2Day. Represents a file record."""
    
    # File specific fields
    hr2d__DocumentCategory__c: Optional[str] = Field(None, description="Document category")
    hr2d__OriginalRecordCreatedDate__c: Optional[datetime] = Field(None, description="Original creation date")
    hr2d__Key__c: Optional[str] = Field(None, description="External reference key")
    hr2d__Employee__c: Optional[str] = Field(None, description="Employee ID the file is linked to")
    hr2d__limitedAccess__c: Optional[bool] = Field(None, description="Limited access flag")
    hr2d__AllowedDocumentProfiles__c: Optional[str] = Field(None, description="Allowed document profiles")
    
    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 