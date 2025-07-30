from typing import Optional, Union, List, Dict, Any
import pandas as pd
from .schemas.account import AccountSchema

# Entity type constant
ENTITY_TYPE = "Account"


class Account:
    """
    Handles account operations for HR2Day API.
    Account holds information about accounts in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the Account class.

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
        Get account data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
            select_fields (Union[List[str], str], optional): Fields to select. If None, all fields will be selected.
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                                                    Example: {"DepartmentToday": ["Name"]} will include department name.
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
            limit (int, optional): Number of records to return (LIMIT clause). Max 200 when all_fields is True. Defaults to 200.
            skip (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
            validate (bool, optional): Whether to validate the data against the AccountSchema. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame containing account data
            
        Raises:
            ValueError: If validate is True and the data validation fails
        """
        # If validation is requested, pass the schema to the get method
        
        return self.hr2day.get(
            entity_type=ENTITY_TYPE,
            select_fields=select_fields,
            related_fields=related,
            filter=filter,
            order_by=orderby,
            limit=limit,
            offset=skip,
            schema=AccountSchema
        )
