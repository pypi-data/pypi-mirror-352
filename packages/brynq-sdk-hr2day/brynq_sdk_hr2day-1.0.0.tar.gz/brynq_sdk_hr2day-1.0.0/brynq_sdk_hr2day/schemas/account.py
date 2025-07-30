from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class BillingShippingAddress(BaseModel):
    """Schema for address information"""
    city: Optional[str] = Field(None, description="City")
    country: Optional[str] = Field(None, description="Country")
    geocodeAccuracy: Optional[str] = Field(None, description="Geocode accuracy")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    postalCode: Optional[str] = Field(None, description="Postal code")
    state: Optional[str] = Field(None, description="State/Province")
    street: Optional[str] = Field(None, description="Street address")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class AccountAttributes(BaseModel):
    """Schema for account object attributes"""
    type: Optional[str] = Field(None, description="Object type")
    url: Optional[str] = Field(None, description="Object URL")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class AccountSchema(BaseModel):
    """Schema for Salesforce Account data"""
    attributes: Optional[AccountAttributes] = Field(None, description="Object attributes")
    Id: Optional[str] = Field(None, description="Account ID")
    IsDeleted: Optional[bool] = Field(None, description="Is deleted")
    MasterRecordId: Optional[str] = Field(None, description="Master record ID")
    Name: Optional[str] = Field(None, description="Account name")
    Type: Optional[str] = Field(None, description="Account type")
    RecordTypeId: Optional[str] = Field(None, description="Record type ID")
    ParentId: Optional[str] = Field(None, description="Parent account ID")
    
    # Billing address fields
    BillingStreet: Optional[str] = Field(None, description="Billing address - street")
    BillingCity: Optional[str] = Field(None, description="Billing address - city")
    BillingState: Optional[str] = Field(None, description="Billing address - state/province")
    BillingPostalCode: Optional[str] = Field(None, description="Billing address - postal code")
    BillingCountry: Optional[str] = Field(None, description="Billing address - country")
    BillingLatitude: Optional[float] = Field(None, description="Billing address - latitude")
    BillingLongitude: Optional[float] = Field(None, description="Billing address - longitude")
    BillingGeocodeAccuracy: Optional[str] = Field(None, description="Billing address - geocode accuracy")
    BillingAddress: Optional[BillingShippingAddress] = Field(None, description="Billing address - complete address object")
    
    # Shipping address fields
    ShippingStreet: Optional[str] = Field(None, description="Shipping address - street")
    ShippingCity: Optional[str] = Field(None, description="Shipping address - city")
    ShippingState: Optional[str] = Field(None, description="Shipping address - state/province")
    ShippingPostalCode: Optional[str] = Field(None, description="Shipping address - postal code")
    ShippingCountry: Optional[str] = Field(None, description="Shipping address - country")
    ShippingLatitude: Optional[float] = Field(None, description="Shipping address - latitude")
    ShippingLongitude: Optional[float] = Field(None, description="Shipping address - longitude")
    ShippingGeocodeAccuracy: Optional[str] = Field(None, description="Shipping address - geocode accuracy")
    ShippingAddress: Optional[BillingShippingAddress] = Field(None, description="Shipping address - complete address object")
    
    # Contact information
    Phone: Optional[str] = Field(None, description="Phone number")
    Fax: Optional[str] = Field(None, description="Fax number")
    AccountNumber: Optional[str] = Field(None, description="Account number")
    Website: Optional[str] = Field(None, description="Website")
    PhotoUrl: Optional[str] = Field(None, description="Photo URL")
    
    # Company information
    Sic: Optional[str] = Field(None, description="SIC code")
    Industry: Optional[str] = Field(None, description="Industry")
    AnnualRevenue: Optional[float] = Field(None, description="Annual revenue")
    NumberOfEmployees: Optional[int] = Field(None, description="Number of employees")
    Ownership: Optional[str] = Field(None, description="Ownership type")
    TickerSymbol: Optional[str] = Field(None, description="Ticker symbol")
    Description: Optional[str] = Field(None, description="Description")
    Rating: Optional[str] = Field(None, description="Rating")
    Site: Optional[str] = Field(None, description="Site")
    
    # System information
    OwnerId: Optional[str] = Field(None, description="Owner ID")
    CreatedDate: Optional[str] = Field(None, description="Creation date")
    CreatedById: Optional[str] = Field(None, description="Creator user ID")
    LastModifiedDate: Optional[str] = Field(None, description="Last modification date")
    LastModifiedById: Optional[str] = Field(None, description="Last modifier user ID")
    SystemModstamp: Optional[str] = Field(None, description="System modification timestamp")
    LastActivityDate: Optional[str] = Field(None, description="Last activity date")
    LastViewedDate: Optional[str] = Field(None, description="Last viewed date")
    LastReferencedDate: Optional[str] = Field(None, description="Last referenced date")
    
    # Partnership information
    IsPartner: Optional[bool] = Field(None, description="Is partner")
    ChannelProgramName: Optional[str] = Field(None, description="Channel program name")
    ChannelProgramLevelName: Optional[str] = Field(None, description="Channel program level name")
    JigsawCompanyId: Optional[str] = Field(None, description="Jigsaw company ID")
    SicDesc: Optional[str] = Field(None, description="SIC description")
    
    # Custom fields
    Multinational__c: Optional[bool] = Field(None, description="Is multinational")
    Klant_van_concurrent__c: Optional[str] = Field(None, description="Customer of competitor")
    AFAS_Klant__c: Optional[bool] = Field(None, description="AFAS customer")
    Contactpersoon__c: Optional[str] = Field(None, description="Contact person")
    In_de_toekomst_benaderen__c: Optional[bool] = Field(None, description="Contact in the future")
    GCLID__c: Optional[str] = Field(None, description="Google Click ID")
    AdWords_actie_c__c: Optional[str] = Field(None, description="AdWords action")
    Bellen__c: Optional[bool] = Field(None, description="To be called")
    Klant_voor_producten_diensten__c: Optional[str] = Field(None, description="Customer for products/services")
    Klant_Salure__c: Optional[str] = Field(None, description="Salure customer")
    Activiteit_land__c: Optional[str] = Field(None, description="Activity country")
    Functioneel_beheer__c: Optional[bool] = Field(None, description="Functional management")
    salarisadministratie__c: Optional[bool] = Field(None, description="Salary administration")
    Vervangingstool__c: Optional[bool] = Field(None, description="Replacement tool")
    Consultancy__c: Optional[bool] = Field(None, description="Consultancy")
    Business_intelligence__c: Optional[bool] = Field(None, description="Business intelligence")
    AFAS_organisatie_ID__c: Optional[str] = Field(None, description="AFAS organization ID")
    Continuiteitsborging__c: Optional[bool] = Field(None, description="Continuity assurance")
    Mailadres_facturatie__c: Optional[str] = Field(None, description="Billing email address")
    KvK_nummer__c: Optional[str] = Field(None, description="Chamber of Commerce number")
    Respons_FB__c: Optional[str] = Field(None, description="FB response")
    Account_ID_18__c: Optional[str] = Field(None, description="18-digit Account ID")
    BTW_nummer_del__c: Optional[str] = Field(None, description="VAT number")
    X5__c: Optional[str] = Field(None, description="X5 field")

    @field_validator('CreatedDate', 'LastModifiedDate', 'SystemModstamp', 'LastActivityDate', 'LastViewedDate', 'LastReferencedDate')
    def validate_datetime(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the string is a valid ISO format datetime"""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid datetime format: {str(e)}")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True
        extra = "allow"  # Allow extra fields that are not defined in the model 