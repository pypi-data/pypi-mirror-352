from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from .base import BaseSchema


class BasicInfoSchema(BaseModel):
    """Schema for basic payroll information"""
    hr2d__Employee__c: Optional[str] = Field(None, description="Employee")
    hr2d__Employer__c: Optional[str] = Field(None, description="Employer")
    hr2d__Arbeidsrelatie__c: Optional[str] = Field(None, description="Employment relationship for this payroll")
    hr2d__Jaar__c: Optional[str] = Field(None, description="Year of payroll")
    hr2d__Periode__c: Optional[str] = Field(None, description="Payroll period (month or other period)")
    hr2d__PeriodeNr__c: Optional[float] = Field(None, description="Period number")
    hr2d__Geldig__c: Optional[bool] = Field(None, description="If enabled, this is the currently valid record")
    hr2d__Key__c: Optional[str] = Field(None, description="Key field consisting of employer tax number, employee BSN, employment number, year/period")
    hr2d__Versie__c: Optional[float] = Field(None, description="Version of this payroll record")
    hr2d__Verloond__c: Optional[str] = Field(None, description="Indicates if this is an actual payroll or dummy record")
    hr2d__Inactief__c: Optional[bool] = Field(None, description="Payroll for inactive employee")
    hr2d__Multi_DV__c: Optional[str] = Field(None, description="Multiple employment relationships")
    hr2d__Sectorfonds__c: Optional[str] = Field(None, description="Sector for social insurance premiums")
    hr2d__SectorRisGrp__c: Optional[str] = Field(None, description="Risk group within sector")
    hr2d__FiscaleRegeling__c: Optional[str] = Field(None, description="Fiscal arrangements")
    hr2d__PayslipText__c: Optional[str] = Field(None, description="Individual payslip note/explanation")
    hr2d__SalarisSpec__c: Optional[str] = Field(None, description="Payslip identifier")
    hr2d__Parameters__c: Optional[str] = Field(None, description="Applied parameters record")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class DatesSchema(BaseModel):
    """Schema for date related fields"""
    hr2d__Periode_datum__c: Optional[date] = Field(None, description="Start date of accounting period")
    hr2d__Periode_einddatum__c: Optional[date] = Field(None, description="End date of accounting period")
    hr2d__Aanvang_Arbrel__c: Optional[date] = Field(None, description="Start of employment relationship")
    hr2d__Einde_Arbrel__c: Optional[date] = Field(None, description="End of employment relationship")
    hr2d__LaatstBerekendDatum__c: Optional[datetime] = Field(None, description="Time when payroll was last calculated")
    hr2d__LaatstVernieuwdDatum__c: Optional[datetime] = Field(None, description="Time when payroll was last renewed")
    hr2d__Verlonen_tot__c: Optional[date] = Field(None, description="Date until which employee should be processed after termination")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class SalarySchema(BaseModel):
    """Schema for salary related fields"""
    hr2d__Salaris__c: Optional[float] = Field(None, description="Salary at end of period")
    hr2d__Salaris_Fulltime__c: Optional[float] = Field(None, description="Full-time salary at end of period")
    hr2d__Uurloon__c: Optional[float] = Field(None, description="Hourly wage")
    hr2d__Uurloon2__c: Optional[float] = Field(None, description="Second hourly wage")
    hr2d__Uurloon3__c: Optional[float] = Field(None, description="Third hourly wage")
    hr2d__Bruto__c: Optional[float] = Field(None, description="Total taxable wage components")
    hr2d__Netto__c: Optional[float] = Field(None, description="Net wage")
    hr2d__Uitbetalen__c: Optional[float] = Field(None, description="Total payment amount")
    hr2d__Uitbetalen_Bank2__c: Optional[float] = Field(None, description="Amount paid to second bank account")
    hr2d__Minimumloon__c: Optional[float] = Field(None, description="Minimum wage on full-time basis")
    hr2d__KostenReserveringen__c: Optional[float] = Field(None, description="Total costs based on period payments and reservations")
    hr2d__KostenWerkelijk__c: Optional[float] = Field(None, description="Total costs based on actual payments")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class WorkingTimeSchema(BaseModel):
    """Schema for working time related fields"""
    hr2d__Kalenderdagen__c: Optional[float] = Field(None, description="Number of active calendar days in period")
    hr2d__Werkdagen__c: Optional[float] = Field(None, description="Number of active working days in period")
    hr2d__Roosterdagen__c: Optional[float] = Field(None, description="Number of worked days according to schedule")
    hr2d__Roosteruren__c: Optional[float] = Field(None, description="Number of worked hours according to schedule")
    hr2d__Uren__c: Optional[float] = Field(None, description="Number of worked hours in period")
    hr2d__Deeltd_Aanvang__c: Optional[float] = Field(None, description="Part-time factor at start of period")
    hr2d__Deeltd_Einde__c: Optional[float] = Field(None, description="Part-time factor at end of period")
    hr2d__Werkdagen_Fiscaal__c: Optional[float] = Field(None, description="Working days based on fiscal days/year")
    hr2d__Prorata_KalDg__c: Optional[float] = Field(None, description="Pro-rata factor based on calendar days")
    hr2d__Prorata_WrkDg__c: Optional[float] = Field(None, description="Pro-rata factor based on working days")
    hr2d__Prorata_30dg__c: Optional[float] = Field(None, description="Pro-rata factor based on 30 days/month")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class TaxSchema(BaseModel):
    """Schema for tax related fields"""
    hr2d__LH_korting__c: Optional[float] = Field(None, description="Wage tax credit")
    hr2d__LH_korting_JN__c: Optional[bool] = Field(None, description="Wage tax credit applied")
    hr2d__Loonheffing__c: Optional[float] = Field(None, description="Wage tax table")
    hr2d__Loonheffing_BT__c: Optional[float] = Field(None, description="Special rate wage tax")
    hr2d__Tabel_LH__c: Optional[str] = Field(None, description="Applied wage tax table")
    hr2d__Arbeidskorting__c: Optional[float] = Field(None, description="Calculated labor credit for wage tax")
    hr2d__LH_grondslag__c: Optional[float] = Field(None, description="Calculation base for wage tax")
    hr2d__LH_BT_jaarln__c: Optional[float] = Field(None, description="Annual wage for special tax rate")
    hr2d__LH_BT_perc__c: Optional[float] = Field(None, description="Special tax rate percentage")
    hr2d__LH_voordeelregel__c: Optional[bool] = Field(None, description="Advantage rule applied for wage tax")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class InsuranceSchema(BaseModel):
    """Schema for insurance related fields"""
    hr2d__SV_dagen__c: Optional[float] = Field(None, description="Number of social security days in period")
    hr2d__ZVW_dagen__c: Optional[float] = Field(None, description="Number of health insurance law days in period")
    hr2d__Premie_ZVW_wg__c: Optional[float] = Field(None, description="Employer health insurance contribution")
    hr2d__Premie_ZVW_wn__c: Optional[float] = Field(None, description="Employee health insurance contribution")
    hr2d__SV_premies_wg__c: Optional[float] = Field(None, description="Total employer social security contributions")
    hr2d__SV_premies_wn__c: Optional[float] = Field(None, description="Total employee social security contributions")
    hr2d__Premie_WaoWga_wg__c: Optional[float] = Field(None, description="WGA and WAO premium")
    hr2d__Premie_WaoWga_wn__c: Optional[float] = Field(None, description="Employee WGA contribution")
    hr2d__Premie_WW_wg__c: Optional[float] = Field(None, description="Employer unemployment insurance premium")
    hr2d__Premie_WW_wn__c: Optional[float] = Field(None, description="Employee unemployment insurance premium")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class LeaveSchema(BaseModel):
    """Schema for leave related fields"""
    hr2d__L1_Accrual__c: Optional[float] = Field(None, description="Leave accrual based on worked hours")
    hr2d__L1_Balance__c: Optional[float] = Field(None, description="Leave balance at time of payroll")
    hr2d__L1_PayBuy__c: Optional[float] = Field(None, description="Paid out or bought leave hours")
    hr2d__VerlofKapitalisatie__c: Optional[str] = Field(None, description="Leave balances capitalized")


class PayrollSchema(BaseModel):
    """Schema for hr2d__Payroll__c entity in HR2Day. Represents a payroll record."""
    base: BaseSchema = Field(None)
    basic_info: BasicInfoSchema = Field(None)
    dates: DatesSchema = Field(None)
    salary: SalarySchema = Field(None)
    working_time: WorkingTimeSchema = Field(None)
    tax: TaxSchema = Field(None)
    insurance: InsuranceSchema = Field(None)
    leave: LeaveSchema = Field(None)

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 