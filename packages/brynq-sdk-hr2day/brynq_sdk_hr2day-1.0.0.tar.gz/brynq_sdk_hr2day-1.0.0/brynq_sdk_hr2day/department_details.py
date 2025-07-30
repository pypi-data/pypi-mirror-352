from typing import Optional, Union, List, Dict, Any
import pandas as pd
from .schemas.department_details import DepartmentDetailsSchema

# Entity type constant
ENTITY_TYPE = "hr2d__DepartmentDetails__c"


class DepartmentDetails:
    """
    Handles department details operations for HR2Day API.
    DepartmentDetails holds information about department details in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the DepartmentDetails class.

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
        Get department details data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
            select_fields (Union[List[str], str], optional): Fields to select. If None, all fields will be selected.
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                                                    Example: {"DepartmentToday": ["Name"]} will include department name.
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
            limit (int, optional): Number of records to return (LIMIT clause). Max 200 when all_fields is True. Defaults to 200.
            skip (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
            validate (bool, optional): Whether to validate the data against the DepartmentDetailsSchema. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame containing department details data
            
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
            schema=DepartmentDetailsSchema
        ) 