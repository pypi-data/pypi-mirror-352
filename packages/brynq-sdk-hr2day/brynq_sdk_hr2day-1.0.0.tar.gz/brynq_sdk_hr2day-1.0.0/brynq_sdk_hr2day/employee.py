from typing import Optional, Union, List, Dict, Any
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.employee import EmployeeSchema, EmployeeUpdateSchema

# Entity type constant
ENTITY_TYPE = "hr2d__Employee__c"


class Employee:
    """
    Handles employee operations for HR2Day API.
    Employee holds information about employees in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the Employee class.

        Args:
            hr2day_instance: The HR2Day class instance.
        """
        self.hr2day = hr2day_instance

    def get(self,
            filter: Optional[str] = None,
            select_fields: Optional[Union[List[str], str]] = None,
            related: Optional[Dict[str, List[str]]] = None,
            orderby: Optional[Union[List[str], str]] = None,
            limit: Optional[int] = None,
            skip: Optional[int] = None) -> pd.DataFrame:
        """
        Get employee data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "Id = 'a08P500000USWDPIA5'"
            select_fields (Union[List[str], str], optional): Fields to select. If None, all fields will be selected.
                            Example (list): ["Id", "FirstName", "LastName"]
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                            Example: {"DepartmentToday": ["Name"]} will include department name.
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
                            Example (list): ["LastName ASC", "FirstName DESC"]
            limit (int, optional): Number of records to return (LIMIT clause). Max 200 when all_fields is True. Defaults to 200.
                            Example: 100
            skip (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
                            Example: 0
        Returns:
            pd.DataFrame: DataFrame containing employee data
            
        Raises:
            ValueError: If validate is True and the data validation fails
        """
        return self.hr2day.get(
            entity_type=ENTITY_TYPE,
            select_fields=select_fields,
            related_fields=related,
            filter=filter,
            order_by=orderby,
            limit=limit,
            offset=skip,
            schema=EmployeeSchema
        ) 
        
    def update(self, employees: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a PUT request to the HR2Day API to update employee information.
        
        Args:
            employees (List[Dict[str, Any]]): List of employees to update. Each employee must include at least one of 
                                             the following parameters:
                - employeeId: 18 characters, case sensitive (e.g., a05A00000ZKQj3IAH)
                - employeeKey: 22 characters, case sensitive (e.g., 000000000L01-012345678)
                - employeeEmplnr: Max 10 characters, numeric (e.g., 123)
                - employeeEmplnrAlternative: Max 10 characters, case sensitive (e.g., 0123-A)
                
                If employeeEmplnr or employeeEmplnrAlternative is used, one of the following is required:
                - employerId: 18 characters, case sensitive (e.g., a04A000004eQcJIAU)
                - employerName: Max 80 characters, case sensitive
                - employerTaxId: 12 characters, case sensitive
                
                Fields that can be updated:
                - hr2d__Email__c: Private email (in email format)
                - hr2d__EmailWork__c: Work email (in email format)
                - hr2d__Phone__c: Phone number (max 20 characters)
                - hr2d__Phone2__c: Second phone number (max 20 characters)
                - hr2d__Phone3__c: Third phone number (max 20 characters)
                - hr2d__Workplace__c: Workplace/room number (max 25 characters)
                - hr2d__DefaultUsername__c: Default username (max 80 characters)
                - hr2d__BundelId__c: SAML Bundle Id (max 60 characters)
                - hr2d__EmplNr_Alt__c: Alternative personnel number (max 20 characters)
                
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        
        try:
            # Validate each employee update data
            valid_employees, invalid_employees = Functions.validate_pydantic_data(employees, EmployeeUpdateSchema)
        except Exception as e:
            # Add validation error to the employee data
            raise ValueError(f"Employee data validation failed:\n{str(e)}")
        # If there are invalid employees, raise an error
        if invalid_employees:
            error_messages = []
            for i, employee in enumerate(invalid_employees):
                error_messages.append(f"Employee {i+1}: {employee.get('_validation_errors', 'Unknown error')}")
            
            error_summary = "\n".join(error_messages)
            raise ValueError(f"Employee data validation failed:\n{error_summary}")
        
        # Create request body
        request_body = {
            "request": {
                "requesterId": self.hr2day.requester_id,
                "employees": valid_employees
            }
        }
        
        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/apexrest/hr2d/employee"
        
        # Send PUT request
        response = self.hr2day.session.put(
            url=url,
            json=request_body
        )
        
        # Error handling
        response.raise_for_status()
        
        # Return response as JSON
        return response.json() 