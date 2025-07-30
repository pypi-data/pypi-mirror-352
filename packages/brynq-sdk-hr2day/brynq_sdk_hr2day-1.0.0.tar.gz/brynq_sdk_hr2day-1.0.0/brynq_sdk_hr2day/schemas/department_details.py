from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

from .base import BaseSchema


class DatesSchema(BaseModel):
    """Schema for date information"""
    hr2d__StartDate__c: Optional[date] = Field(None, description="First day on which these details are valid")
    hr2d__EndDate__c: Optional[date] = Field(None, description="Last day on which these settings are valid")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class CostCenterSchema(BaseModel):
    """Schema for cost center information"""
    hr2d__CostCenter__c: Optional[str] = Field(None, description="Cost center")
    hr2d__CostCenter_Dim2__c: Optional[str] = Field(None, description="Cost center dimension 2")
    hr2d__CostCenter_Dim3__c: Optional[str] = Field(None, description="Cost center dimension 3")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class CustomFieldsSchema(BaseModel):
    """Schema for custom field information"""
    hr2d__FieldName__c: Optional[str] = Field(None, description="Field name")
    hr2d__FieldName2__c: Optional[str] = Field(None, description="Field name 2")
    hr2d__FieldName3__c: Optional[str] = Field(None, description="Field name 3")
    hr2d__FieldValue__c: Optional[str] = Field(None, description="Field value")
    hr2d__FieldValue2__c: Optional[str] = Field(None, description="Field value 2")
    hr2d__FieldValue3__c: Optional[str] = Field(None, description="Field value 3")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class RelationshipSchema(BaseModel):
    """Schema for relationship information"""
    hr2d__Department__c: Optional[str] = Field(None, description="Department to which this is a detail")
    hr2d__Employer__c: Optional[str] = Field(None, description="Employer for which these details apply")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class DepartmentDetailsSchema(BaseModel):
    """Schema for hr2d__DepartmentDetails__c entity in HR2Day. Represents department details record."""
    base: BaseSchema = Field(None)
    dates: DatesSchema = Field(None)
    cost_center: CostCenterSchema = Field(None)
    custom_fields: CustomFieldsSchema = Field(None)
    relationship: RelationshipSchema = Field(None)

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 