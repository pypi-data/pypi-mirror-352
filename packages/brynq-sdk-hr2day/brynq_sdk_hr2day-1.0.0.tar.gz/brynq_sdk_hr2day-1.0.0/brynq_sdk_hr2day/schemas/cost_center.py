from typing import Optional, List, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from pandera.typing import Series
import pandera as pa
import pandas as pd

from .base import BaseSalesforceSchema

class CostCenterUpdateSchema(BaseModel):
    """Schema for cost center update/insert operations."""
    
    # Identification fields
    costcenterId: Optional[str] = Field(None, description="Cost center ID for update operations", pattern=r'^[a-zA-Z0-9]{18}$')
    employerId: Optional[str] = Field(None, description="Employer ID for insert operations", pattern=r'^[a-zA-Z0-9]{18}$')
    employerName: Optional[str] = Field(None, description="Employer name for insert operations", max_length=80)
    employerTaxId: Optional[str] = Field(None, description="Employer tax ID for insert operations", pattern=r'^[a-zA-Z0-9]{12}$')
    
    # Cost center fields
    Name: Optional[str] = Field(None, description="Name of the cost center", max_length=80)
    hr2d__StartDate__c: Optional[datetime] = Field(None, description="Start date of the cost center")
    hr2d__EndDate__c: Optional[datetime] = Field(None, description="End date of the cost center")
    hr2d__Description__c: Optional[str] = Field(None, description="Description of the cost center", max_length=75)
    hr2d__Dimension__c: Optional[str] = Field(None, description="Dimension of the cost center", pattern=r'^[1-39]$')
    hr2d__Classification__c: Optional[str] = Field(None, description="Classification of the cost center", max_length=20)
    hr2d__RecapChar__c: Optional[str] = Field(None, description="Verdichtings-kenmerk of the cost center", max_length=20)
    
    @model_validator(mode='after')
    def validate_identification_fields(self) -> 'CostCenterUpdateSchema':
        """Validate that either costcenterId or one of the employer identification fields is provided."""
        if not self.costcenterId and not self.employerId and not self.employerName and not self.employerTaxId:
            raise ValueError("Either costcenterId or one of employerId, employerName, employerTaxId must be provided")
        return self
    
    @model_validator(mode='after')
    def validate_name_for_insert(self) -> 'CostCenterUpdateSchema':
        """Validate that Name is provided for insert operations."""
        if not self.costcenterId and not self.Name:
            raise ValueError("Name is required for insert operations")
        return self
    
    class Config:
        """Schema configuration"""
        strict = True
        coerce = True

class CostCenterGetSchema(pa.DataFrameModel):
    """Schema for cost center get operations."""
    
    # System fields
    Id: Series[str] = pa.Field(nullable=False, description="Record ID", regex=r'^[a-zA-Z0-9]{18}$')
    CreatedById: Series[str] = pa.Field(nullable=False, description="Created By ID", regex=r'^[a-zA-Z0-9]{18}$')
    CreatedDate: Series[datetime] = pa.Field(nullable=False, description="Created Date", coerce=True)
    LastModifiedById: Series[str] = pa.Field(nullable=False, description="Last Modified By ID", regex=r'^[a-zA-Z0-9]{18}$')
    LastModifiedDate: Series[datetime] = pa.Field(nullable=False, description="Last Modified Date", coerce=True)
    SystemModstamp: Series[datetime] = pa.Field(nullable=False, description="System Modstamp", coerce=True)
    
    # Cost center fields
    Name: Series[str] = pa.Field(nullable=False, description="Name/Code", str_length=80)
    hr2d__Classification__c: Series[str] = pa.Field(nullable=True, description="Rubricering", str_length=20)
    hr2d__Delegate__c: Series[str] = pa.Field(nullable=True, description="Gedelegeerd budgethouder", regex=r'^[a-zA-Z0-9]{18}$')
    hr2d__Department__c: Series[str] = pa.Field(nullable=True, description="Afdeling", regex=r'^[a-zA-Z0-9]{18}$')
    hr2d__Description__c: Series[str] = pa.Field(nullable=True, description="Omschrijving", str_length=75)
    hr2d__Dimension__c: Series[str] = pa.Field(nullable=True, description="Dimensie", str_length=255)
    hr2d__Employer__c: Series[str] = pa.Field(nullable=True, description="Werkgever", regex=r'^[a-zA-Z0-9]{18}$')
    hr2d__EndDate__c: Series[datetime] = pa.Field(nullable=True, description="Einddatum", coerce=True)
    hr2d__Key__c: Series[str] = pa.Field(nullable=True, description="Key", str_length=95)
    hr2d__MainCostCenter__c: Series[bool] = pa.Field(nullable=True, description="Hoofdkostenplaats", coerce=True)
    hr2d__Manager__c: Series[str] = pa.Field(nullable=True, description="Budgethouder", regex=r'^[a-zA-Z0-9]{18}$')
    hr2d__RecapChar__c: Series[str] = pa.Field(nullable=True, description="Verdichtingskenmerk", str_length=20)
    hr2d__RecordId__c: Series[str] = pa.Field(nullable=True, description="Record-id (lang)", str_length=1300)
    hr2d__StartDate__c: Series[datetime] = pa.Field(nullable=True, description="Begindatum", coerce=True)
    
    class Config:
        """Schema configuration"""
        strict = True
        coerce = True 