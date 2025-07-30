from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from pandera.typing import Series
import pandera as pa

from .base import BaseSalesforceSchema


class PersonalInfoSchema(BaseModel):
    """Schema for personal information"""
    hr2d__FirstName__c: Optional[str] = Field(None, description="Formal first name of the employee")
    hr2d__Initials__c: Optional[str] = Field(None, description="Initials of the employee, in capitals separated by a dot")
    hr2d__Nickname__c: Optional[str] = Field(None, description="Nickname of employee (if filled, overrides first name in formatted name)")
    hr2d__Prefix__c: Optional[str] = Field(None, description="Prefix for employee's surname (birth name)")
    hr2d__Surname__c: Optional[str] = Field(None, description="Employee's surname (birth name)")
    hr2d__PrefixPartner__c: Optional[str] = Field(None, description="Prefix for partner's surname")
    hr2d__SurnamePartner__c: Optional[str] = Field(None, description="Partner's surname")
    hr2d__A_name__c: Optional[str] = Field(None, description="Formatted name of employee (first name surname - partner name) depending on selected name format")
    hr2d__A_Surname__c: Optional[str] = Field(None, description="Formatted surname of employee (prefixes surname - partner prefixes partner surname) depending on chosen name format")
    hr2d__NameFormat__c: Optional[str] = Field(None, description="Controls formatting of employee name (combination of birth name and partner name)")
    hr2d__TitleBefore__c: Optional[str] = Field(None, description="Title before name")
    hr2d__TitleBeforeSel__c: Optional[str] = Field(None, description="Title before name (select)")
    hr2d__TitleAfter__c: Optional[str] = Field(None, description="Title after name")
    hr2d__TitleAfterSel__c: Optional[str] = Field(None, description="Title after name (select)")
    hr2d__Gender__c: Optional[str] = Field(None, description="Gender of the employee")
    hr2d__BirthDate__c: Optional[datetime] = Field(None, description="Date of birth (enter with century indication, dd-mm-yyyy)")
    hr2d__BirthPlace__c: Optional[str] = Field(None, description="Place of birth")
    hr2d__BirthCountry__c: Optional[str] = Field(None, description="Country of birth")
    hr2d__Nationality__c: Optional[str] = Field(None, description="Nationality")
    hr2d__MaritalStatus__c: Optional[str] = Field(None, description="Marital status")
    hr2d__MaritalStatusDate__c: Optional[datetime] = Field(None, description="Date when marital status takes effect")
    hr2d__DeathDate__c: Optional[datetime] = Field(None, description="Date of death")
    hr2d__Age__c: Optional[float] = Field(None, description="Age of employee (today)")
    hr2d__AgeGroup__c: Optional[str] = Field(None, description="Age group")
    hr2d__Language__c: Optional[str] = Field(None, description="Language of the employee")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class AddressSchema(BaseModel):
    """Schema for address information"""
    hr2d__Street__c: Optional[str] = Field(None, description="Street name (without house number)")
    hr2d__HouseNr__c: Optional[float] = Field(None, description="House number without addition")
    hr2d__HouseNrAdd__c: Optional[str] = Field(None, description="House number addition")
    hr2d__AddAddressLine__c: Optional[str] = Field(None, description="Additional address line")
    hr2d__PostalCode__c: Optional[str] = Field(None, description="Postal code")
    hr2d__City__c: Optional[str] = Field(None, description="City")
    hr2d__Country__c: Optional[str] = Field(None, description="Country (ISO code)")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class PostalAddressSchema(BaseModel):
    """Schema for postal address information"""
    hr2d__Mail_Street__c: Optional[str] = Field(None, description="Postal street (without house number)")
    hr2d__Mail_HouseNr__c: Optional[float] = Field(None, description="Postal house number without addition")
    hr2d__Mail_HouseNrAdd__c: Optional[str] = Field(None, description="Postal house number addition")
    hr2d__Mail_AddAddressLine__c: Optional[str] = Field(None, description="Postal additional address line")
    hr2d__Mail_PostalCode__c: Optional[str] = Field(None, description="Postal postal code")
    hr2d__Mail_City__c: Optional[str] = Field(None, description="Postal city")
    hr2d__Mail_Country__c: Optional[str] = Field(None, description="Postal country (ISO code)")
    hr2d__MailAddress_Copy__c: Optional[bool] = Field(None, description="Uncheck if postal address differs from standard address")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ContactSchema(BaseModel):
    """Schema for contact information"""
    hr2d__Phone__c: Optional[str] = Field(None, description="Phone number of the employee")
    hr2d__Phone2__c: Optional[str] = Field(None, description="Second phone number")
    hr2d__Phone3__c: Optional[str] = Field(None, description="Third phone number")
    hr2d__Email__c: Optional[str] = Field(None, description="Private email of the employee")
    hr2d__EmailWork__c: Optional[str] = Field(None, description="Work email of the employee")
    hr2d__Workplace__c: Optional[str] = Field(None, description="Workplace/room number")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class IdentificationSchema(BaseModel):
    """Schema for identification information"""
    hr2d__BSN__c: Optional[str] = Field(None, description="Citizen service number (BSN/SoFi). Check: length 9 characters, 11-test")
    hr2d__ID_Type__c: Optional[str] = Field(None, description="Type of ID for establishing employee identity")
    hr2d__ID_Nr__c: Optional[str] = Field(None, description="ID number")
    hr2d__ID_RelDate__c: Optional[datetime] = Field(None, description="ID date of issue")
    hr2d__ID_EndDate__c: Optional[datetime] = Field(None, description="ID expiration date")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class EmploymentSchema(BaseModel):
    """Schema for employment information"""
    hr2d__EmplNr__c: Optional[float] = Field(None, description="Employee number")
    hr2d__EmplNr_Alt__c: Optional[str] = Field(None, description="Alternative employee number")
    hr2d__Alias__c: Optional[str] = Field(None, description="Employee alias. Can also be used as alphanumeric personnel number")
    hr2d__HireDate__c: Optional[datetime] = Field(None, description="Date of employment")
    hr2d__HireDateConcern__c: Optional[datetime] = Field(None, description="Date employee joined the concern (seniority)")
    hr2d__TerminationDate__c: Optional[datetime] = Field(None, description="End date of employment (last day employee was still employed)")
    hr2d__RetirementDate__c: Optional[datetime] = Field(None, description="Expected AOW/pension date based on current legislation")
    hr2d__Seniority__c: Optional[float] = Field(None, description="Number of years of service of the employee (today)")
    hr2d__EducationLevel__c: Optional[str] = Field(None, description="Highest education completed")
    hr2d__Employer__c: Optional[str] = Field(None, description="Employer")
    hr2d__ArbeidsrelatieToday__c: Optional[str] = Field(None, description="Current valid employment relationship")
    hr2d__DepartmentToday__c: Optional[str] = Field(None, description="Current department")
    hr2d__JobToday__c: Optional[str] = Field(None, description="Current job")
    hr2d__WtfTotalToday__c: Optional[float] = Field(None, description="Current total part-time factor")
    hr2d__Mentor__c: Optional[str] = Field(None, description="Employee who is mentor of this employee")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class BankSchema(BaseModel):
    """Schema for bank information"""
    hr2d__Bank__c: Optional[str] = Field(None, description="Bank account number")
    hr2d__BankIBAN__c: Optional[str] = Field(None, description="International Bank Account Number")
    hr2d__BankBIC__c: Optional[str] = Field(None, description="Bank Identification Code (BIC or formerly SWIFT code)")
    hr2d__BankName__c: Optional[str] = Field(None, description="Alternative bank account holder name")
    hr2d__Bank_Description__c: Optional[str] = Field(None, description="Alternative description for bank payment")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class UserSchema(BaseModel):
    """Schema for user information"""
    hr2d__User__c: Optional[str] = Field(None, description="Salesforce user for Employee Self Service")
    hr2d__UserAdditional__c: Optional[str] = Field(None, description="Additional user account with different authorizations")
    hr2d__DefaultUserName__c: Optional[str] = Field(None, description="Standard username when creating user")
    hr2d__BundelId__c: Optional[str] = Field(None, description="SAML Bundle Id for user creation")
    hr2d__InboxSettings__c: Optional[str] = Field(None, description="Inbox settings for this employee")
    hr2d__PortfolioSettings__c: Optional[str] = Field(None, description="Portfolio settings")
    hr2d__PortfolioPermission__c: Optional[str] = Field(None, description="Portfolio permissions")
    hr2d__PrivacySettings__c: Optional[str] = Field(None, description="Privacy settings of this employee")
    hr2d__PayslipSettings__c: Optional[str] = Field(None, description="Pay slip settings")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class EmployeeSchema(BaseSalesforceSchema):
    """Schema for hr2d__Employee__c entity in HR2Day. Represents an employee record."""
    # Salesforce Standard Fields
    OwnerId: Series[str] = pa.Field(nullable=True, description="Owner ID")

    # HR2Day Custom Fields
    LastActivityDate: Series[datetime] = pa.Field(nullable=True, description="Last activity date", coerce=True)
    LastViewedDate: Series[datetime] = pa.Field(nullable=True, description="Last viewed date", coerce=True)
    LastReferencedDate: Series[datetime] = pa.Field(nullable=True, description="Last referenced date", coerce=True)
    hr2d__A_Surname__c: Series[str] = pa.Field(nullable=True, description="Formatted surname")
    hr2d__A_name__c: Series[str] = pa.Field(nullable=True, description="Formatted full name")
    hr2d__BirthDate__c: Series[datetime] = pa.Field(nullable=True, description="Birth date", coerce=True)
    hr2d__EmplNr__c: Series[float] = pa.Field(nullable=True, description="Employee number")
    hr2d__Employer__c: Series[str] = pa.Field(nullable=True, description="Employer ID")
    hr2d__FirstName__c: Series[str] = pa.Field(nullable=True, description="First name")
    hr2d__Gender__c: Series[str] = pa.Field(
        nullable=True, 
        description="Gender",
        isin=['Man', 'Vrouw', 'Other']
    )
    hr2d__HireDate__c: Series[datetime] = pa.Field(nullable=True, description="Hire date", coerce=True)
    hr2d__Initials__c: Series[str] = pa.Field(nullable=True, description="Initials")
    hr2d__NameFormat__c: Series[str] = pa.Field(nullable=True, description="Name format")
    hr2d__Nickname__c: Series[str] = pa.Field(nullable=True, description="Nickname")
    hr2d__Phone2__c: Series[str] = pa.Field(
        nullable=True, 
        description="Second phone number",
        str_length={"max_value": 20}
    )
    hr2d__Phone__c: Series[str] = pa.Field(
        nullable=True, 
        description="Primary phone number",
        str_length={"max_value": 20}
    )
    hr2d__PrefixPartner__c: Series[str] = pa.Field(nullable=True, description="Partner's prefix")
    hr2d__Prefix__c: Series[str] = pa.Field(nullable=True, description="Prefix")
    hr2d__SurnamePartner__c: Series[str] = pa.Field(nullable=True, description="Partner's surname")
    hr2d__Surname__c: Series[str] = pa.Field(nullable=True, description="Surname")
    hr2d__TerminationDate__c: Series[datetime] = pa.Field(nullable=True, description="Termination date", coerce=True)
    hr2d__EmailWork__c: Series[str] = pa.Field(
        nullable=True, 
        description="Work email",
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    hr2d__DepartmentToday__c: Series[str] = pa.Field(nullable=True, description="Current department ID")
    hr2d__JobToday__c: Series[str] = pa.Field(nullable=True, description="Current job ID")
    hr2d__ArbeidsrelatieToday__c: Series[str] = pa.Field(nullable=True, description="Current employment relationship ID")
    hr2d__RecordId__c: Series[str] = pa.Field(nullable=True, description="Case insensitive record ID")
    hr2d__Phone3__c: Series[str] = pa.Field(
        nullable=True, 
        description="Third phone number",
        str_length={"max_value": 20}
    )
    hr2d__TerminationDateFilter__c: Series[str] = pa.Field(nullable=True, description="Termination date filter", coerce=True)
    
    # Custom Fields
    Bonus__c: Series[bool] = pa.Field(nullable=True, description="Bonus flag")
    JubCor__c: Series[str] = pa.Field(nullable=True, description="Jubilee correction")
    Jub125__c: Series[datetime] = pa.Field(nullable=True, description="12.5 year jubilee date", coerce=True)
    Jub10__c: Series[datetime] = pa.Field(nullable=True, description="10 year jubilee date", coerce=True)
    Jub15__c: Series[datetime] = pa.Field(nullable=True, description="15 year jubilee date", coerce=True)
    Jub25__c: Series[datetime] = pa.Field(nullable=True, description="25 year jubilee date", coerce=True)
    Jub40__c: Series[datetime] = pa.Field(nullable=True, description="40 year jubilee date", coerce=True)

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True


class EmployeeUpdateFieldsSchema(BaseModel):
    """Schema for updatable employee fields in HR2Day API."""
    hr2d__Email__c: Optional[str] = Field(None, description="Private email (in email format a@b.c)")
    hr2d__EmailWork__c: Optional[str] = Field(None, description="Work email (in email format a@b.c)")
    hr2d__Phone__c: Optional[str] = Field(None, description="Phone number (max 20 characters)")
    hr2d__Phone2__c: Optional[str] = Field(None, description="Second phone number (max 20 characters)")
    hr2d__Phone3__c: Optional[str] = Field(None, description="Third phone number (max 20 characters)")
    hr2d__Workplace__c: Optional[str] = Field(None, description="Workplace (max 25 characters)")
    hr2d__DefaultUsername__c: Optional[str] = Field(None, description="Default username (max 80 characters)")
    hr2d__BundelId__c: Optional[str] = Field(None, description="SAML Bundle Id (max 60 characters)")
    hr2d__EmplNr_Alt__c: Optional[str] = Field(None, description="Alternative personnel number (max 20 characters)")

    class Config:
        """Pydantic configuration"""
        frozen = False
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "forbid"


class EmployeeUpdateSchema(BaseModel):
    """Schema for employee update request in HR2Day API."""
    employerId: Optional[str] = Field(None, description="Employer ID (18 characters, case sensitive)")
    employerName: Optional[str] = Field(None, description="Employer name (max 80 characters, case sensitive)")
    employerTaxId: Optional[str] = Field(None, description="Employer tax ID (12 characters, case sensitive)")
    employeeId: Optional[str] = Field(None, description="Employee ID (18 characters, case sensitive)")
    employeeKey: Optional[str] = Field(None, description="Employee Key (22 characters, case sensitive)")
    employeeEmplnr: Optional[str] = Field(None, description="Employee number (max 10 characters, numeric)")
    employeeEmplnrAlternative: Optional[str] = Field(None, description="Alternative employee number (max 10 characters, case sensitive)")
    errors: Optional[str] = Field("", description="Error messages for this employee update")
    employee: EmployeeUpdateFieldsSchema = Field(..., description="Employee fields to update")

    @field_validator('employeeEmplnr')
    @classmethod
    def validate_employee_emplnr(cls, v, info):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Employee number must be at most 10 characters')
            try:
                int(v)  # Check if it can be converted to integer
            except ValueError:
                raise ValueError('Employee number must be numeric')
            
            # Check if employer identifier is provided
            data = info.data
            if not data.get('employerId') and not data.get('employerName') and not data.get('employerTaxId'):
                raise ValueError('When using employeeEmplnr, one of employerId, employerName, or employerTaxId is required')
        return v
    
    @field_validator('employeeEmplnrAlternative')
    @classmethod
    def validate_employee_emplnr_alt(cls, v, info):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Alternative employee number must be at most 10 characters')
            # Check if employer identifier is provided
            data = info.data
            if not data.get('employerId') and not data.get('employerName') and not data.get('employerTaxId'):
                raise ValueError('When using employeeEmplnrAlternative, one of employerId, employerName, or employerTaxId is required')
        return v
    
    @field_validator('employee')
    @classmethod
    def validate_employee_fields(cls, v):
        # Ensure at least one field is provided for update
        if not any(getattr(v, field) is not None for field in v.__fields__):
            raise ValueError('At least one employee field must be provided for update')
        return v
    
    # Validate that at least one employee identifier is provided
    @field_validator('employeeId', 'employeeKey', 'employeeEmplnr', 'employeeEmplnrAlternative')
    @classmethod
    def validate_employee_identifier(cls, v, info):
        field_name = info.field_name
        if field_name == 'employeeEmplnrAlternative':
            data = info.data
            if not any([
                data.get('employeeId'), 
                data.get('employeeKey'), 
                data.get('employeeEmplnr'), 
                v
            ]):
                raise ValueError('At least one of employeeId, employeeKey, employeeEmplnr, or employeeEmplnrAlternative must be provided')
        return v

    class Config:
        """Pydantic configuration"""
        frozen = False
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "forbid"

