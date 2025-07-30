from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

from .base import BaseSchema


class AddressSchema(BaseModel):
    """Schema for address information"""
    hr2d__Street__c: Optional[str] = Field(None, description="Street name (without house number)")
    hr2d__HouseNr__c: Optional[float] = Field(None, description="House number without addition")
    hr2d__HouseNrAdd__c: Optional[str] = Field(None, description="House number addition")
    hr2d__PostalCode__c: Optional[str] = Field(None, description="Postal code of the location")
    hr2d__City__c: Optional[str] = Field(None, description="City of the location")
    hr2d__Country__c: Optional[str] = Field(None, description="Country")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ValiditySchema(BaseModel):
    """Schema for validity information"""
    hr2d__StartDate__c: Optional[date] = Field(None, description="First day the location is valid. Leave empty to not restrict start of validity")
    hr2d__EndDate__c: Optional[date] = Field(None, description="Last day the location is valid. Leave empty to not restrict end of validity")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ContactSchema(BaseModel):
    """Schema for contact information"""
    hr2d__Phone__c: Optional[str] = Field(None, description="Phone number of the location")
    hr2d__Description__c: Optional[str] = Field(None, description="Detailed description of the location")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class LocationSchema(BaseModel):
    """Schema for hr2d__Location__c entity in HR2Day. Represents a location record."""
    base: BaseSchema = Field(None)
    address: AddressSchema = Field(None)
    validity: ValiditySchema = Field(None)
    contact: ContactSchema = Field(None)

    hr2d__Employer__c: Optional[str] = Field(None, description="Employer")
    hr2d__Key__c: Optional[str] = Field(None, description="Location key field from employer's wage tax number and location name")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 