from typing import Optional, Union, List, Dict, Any
import pandas as pd
from datetime import date
from brynq_sdk_functions import Functions
from .schemas.leave import LeaveSchema, LeaveImportSchema

# Entity type constant
ENTITY_TYPE = "hr2d__Leave__c"
IMPORT_ENTITY_TYPE = "hr2d__LeaveImport__c"


class Leave:
    """
    Handles leave operations for HR2Day API.
    Leave holds information about leave requests in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the Leave class.

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
        Get leave data from Salesforce.

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
            pd.DataFrame: DataFrame containing leave data
            
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
            schema=LeaveSchema
        )
        
    def process(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to process leave records (insert, update, or delete) using the LeaveImport object.
        
        Args:
            leaves (List[Dict[str, Any]]): List of leave records to process. Each leave must include:
                - hr2d__Operation__c: Operation type ("insert", "update", or "delete")
                
                For insert:
                - One of hr2d__EmployeeId__c or hr2d__EmployeeNr__c
                - One of hr2d__EmployerId__c, hr2d__EmployerTaxId__c, or hr2d__EmployerName__c
                - One of hr2d__LeaveCode__c or hr2d__Leave__c
                - Required leave fields: hr2d__Hours__c, hr2d__StartDate__c, 
                  hr2d__EndDate__c, hr2d__ArbrelVolgnr__c, hr2d__Workflowstatus__c
                
                For update/delete:
                - One of hr2d__ExternalKey__c or hr2d__InternalId__c
                
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        try:
            # Convert list to DataFrame for validation

            # Validate each leave record against the schema
            valid_leaves, invalid_leaves = Functions.validate_pydantic_data(leaves, LeaveImportSchema)
        except Exception as e:
            raise ValueError(f"Leave data validation failed:\n{str(e)}")

        # If there are invalid leave records, raise an error
        if invalid_leaves:
            error_messages = []
            for i, leave in enumerate(invalid_leaves):
                error_messages.append(f"Leave {i+1}: {leave.get('_validation_errors', 'Unknown error')}")
            
            error_summary = "\n".join(error_messages)
            raise ValueError(f"Leave data validation failed:\n{error_summary}")
        
        # Additional validation for required fields based on operation
        for i, leave in enumerate(valid_leaves):
            operation = leave.get("hr2d__Operation__c")
            
            if operation == "insert":
                # Check employee identification
                if not (leave.get("hr2d__EmployeeId__c") or leave.get("hr2d__EmployeeNr__c")):
                    raise ValueError(f"Leave {i+1}: For insert operation, either hr2d__EmployeeId__c or hr2d__EmployeeNr__c is required")
                
                # Check employer identification
                if not (leave.get("hr2d__EmployerId__c") or leave.get("hr2d__EmployerTaxId__c") or leave.get("hr2d__EmployerName__c")):
                    raise ValueError(f"Leave {i+1}: For insert operation, one of hr2d__EmployerId__c, hr2d__EmployerTaxId__c, or hr2d__EmployerName__c is required")
                
                # Check leave identification
                if not (leave.get("hr2d__LeaveCode__c") or leave.get("hr2d__Leave__c")):
                    raise ValueError(f"Leave {i+1}: For insert operation, either hr2d__LeaveCode__c or hr2d__Leave__c is required")
                
                # Check required fields
                required_fields = ["hr2d__Hours__c", "hr2d__StartDate__c", "hr2d__EndDate__c", 
                                 "hr2d__ArbrelVolgnr__c", "hr2d__Workflowstatus__c"]
                missing_fields = [field for field in required_fields if not leave.get(field)]
                if missing_fields:
                    raise ValueError(f"Leave {i+1}: For insert operation, the following fields are required: {', '.join(missing_fields)}")
            
            elif operation in ["update", "delete"]:
                # Check identification
                if not (leave.get("hr2d__ExternalKey__c") or leave.get("hr2d__InternalId__c")):
                    raise ValueError(f"Leave {i+1}: For {operation} operation, either hr2d__ExternalKey__c or hr2d__InternalId__c is required")
        
        # Create request body for composite API
        records = []
        for leave in valid_leaves:
            # Create a flat record structure for the API
            record = {
                "attributes": {"type": IMPORT_ENTITY_TYPE}
            }
            
            # Add API fields
            for field in [
                "hr2d__ExternalKey__c", "hr2d__InternalId__c", "hr2d__EmployeeId__c",
                "hr2d__EmployeeNr__c", "hr2d__Mode__c", "hr2d__Operation__c",
                "hr2d__EmployerId__c", "hr2d__EmployerTaxId__c", "hr2d__EmployerName__c"
            ]:
                if field in leave and leave[field] is not None:
                    record[field] = leave[field]
            
            # Add leave fields
            for field in [
                "hr2d__Hours__c", "hr2d__StartDate__c", "hr2d__EndDate__c",
                "hr2d__ArbrelVolgnr__c", "hr2d__Reason__c", "hr2d__Details__c",
                "hr2d__TvtType__c", "hr2d__Description__c", "hr2d__LeaveCode__c",
                "hr2d__Leave__c", "hr2d__Changes__c", "hr2d__Workflowstatus__c"
            ]:
                if field in leave and leave[field] is not None:
                    # Convert date objects to string format
                    if isinstance(leave[field], date):
                        record[field] = leave[field].isoformat()
                    else:
                        record[field] = leave[field]
            
            records.append(record)
        
        # Create the final request body
        request_body = {
            "allOrNone": False,
            "records": records
        }
        
        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/data/{self.hr2day.API_VERSION}/composite/sobjects/"
        
        # Send POST request
        response = self.hr2day.session.post(
            url=url,
            json=request_body
        )
        
        # Error handling
        response.raise_for_status()
        
        # Return response as JSON
        return response.json()
        
    def insert(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to insert leave records using the LeaveImport object.
        This is a convenience method that sets the operation type to "insert".
        
        Args:
            leaves (List[Dict[str, Any]]): List of leave records to insert. Each leave must include:
                - One of hr2d__EmployeeId__c or hr2d__EmployeeNr__c
                - One of hr2d__EmployerId__c, hr2d__EmployerTaxId__c, or hr2d__EmployerName__c
                - One of hr2d__LeaveCode__c or hr2d__Leave__c
                - Required leave fields: hr2d__Hours__c, hr2d__StartDate__c, 
                  hr2d__EndDate__c, hr2d__ArbrelVolgnr__c, hr2d__Workflowstatus__c
                
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        # Set operation type to "insert" for all records
        for leave in leaves:
            leave["hr2d__Operation__c"] = "insert"
            leave["hr2d__Mode__c"] = "online"
            
        return self.process(leaves)
        
    def update(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to update leave records using the LeaveImport object.
        This is a convenience method that sets the operation type to "update".
        
        Args:
            leaves (List[Dict[str, Any]]): List of leave records to update. Each leave must include:
                - One of hr2d__ExternalKey__c or hr2d__InternalId__c to identify the leave record
                - The leave fields to update
                
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        # Set operation type to "update" for all records
        for leave in leaves:
            leave["hr2d__Operation__c"] = "update"
            leave["hr2d__Mode__c"] = "online"
            
        return self.process(leaves)
        
    def delete(self, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a request to the HR2Day API to delete leave records using the LeaveImport object.
        This is a convenience method that sets the operation type to "delete".
        
        Args:
            leaves (List[Dict[str, Any]]): List of leave records to delete. Each leave must include:
                - One of hr2d__ExternalKey__c or hr2d__InternalId__c to identify the leave record
                
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        # Set operation type to "delete" for all records
        for leave in leaves:
            leave["hr2d__Operation__c"] = "delete"
            leave["hr2d__Mode__c"] = "online"
            
        return self.process(leaves) 