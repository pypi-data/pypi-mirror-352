"""
The Service class for CRUD operations on Azure Cosmos DB.
"""

import os

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from typing import List, Dict, Union, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class CosmosCRUDService:
    """The class CosmosCRUDService is a wrapper for Azure Cosmos DB which provides CRUD operations.Set your Azure Cosmos DB connection string in the environment variable AZURE_COSMOS_CONNECTION_STRING.

    ## Parameters:
        database_name (str): Provide the database name you want to create.
        partition_key (Union[str,List]): Provide the partiion key to create in the container.
        container_name (str): The name of the container You want to create.
    """

    def __init__(
        self, database_name: str, partition_key: Union[str, List], container_name: str
    ):
        self.database_name = database_name
        self.partition_key_path = partition_key
        self.container_name = container_name
        if isinstance(self.partition_key_path, str):
            self.partition_key = PartitionKey(path=self.partition_key_path, kind="Hash")
        elif isinstance(self.partition_key_path, list):
            self.partition_key = PartitionKey(
                path=self.partition_key_path, kind="MultiHash"
            )
        else:
            raise TypeError("partition key path must be str or list of str.")
        self.client, self.db, self.container = self._get_database_clients()

    def _get_database_clients(self):
        """It is Private method to get the database clients."""
        try:
            client = CosmosClient.from_connection_string(
                conn_str=os.getenv("AZURE_COSMOS_CONNECTION_STRING")
            )
            database = client.create_database_if_not_exists(self.database_name)

            container = database.create_container_if_not_exists(
                self.container_name, partition_key=self.partition_key
            )
        except Exception as e:
            print(f"Error creating database or container: {e}")
            raise e
        return client, database, container

    def create_item(self, item: Dict) -> str:
        """Create an item in the container.
        ## Parameters:
            item (dict): Item to insert into the container.
        ## Returns:
            str: Item Created Successfully or item already exists.
        """
        try:
            self.container.create_item(body=item)

        except exceptions.CosmosResourceExistsError as e:
            print(f"Item already exists: {e}")
            return "Item already exists"
        except Exception as e:
            print(f"Error creating item: {e}")
            raise e
        return "Item Created Successfully"

    def query_items(self, query: str) -> List:
        """Query items in the container using SQL-like syntax.
        ## Parameters:
            query (str): The SQL-like query to execute.
        ## Returns:
            list: A list of items matching the query.
        """
        try:
            items = list(
                self.container.query_items(
                    query=query, enable_cross_partition_query=True
                )
            )
        except Exception as e:
            print(f"Error querying items: {e}")
            return []
        return items

    def update_item(self, item_id: str, updated_item: Dict) -> Dict:
        """Update an item in the container.
        ## Parameters:
            item_id (str): The ID of the item to update.
            updated_item (dict): The updated item data.
        ## Returns:
            dict: returns updated Item dictionary.
        """
        try:
            item = self.container.replace_item(item=item_id, body=updated_item)
        except Exception as e:
            print(f"Error updating item: {e}")
            raise e
        return item

    def delete_item(
        self, item_id: str, partition_key_values: Optional[Any] = None
    ) -> str:
        """Delete an item in the container.
        ## Parameters:
            item_id (str): The ID of the item to delete.
            partition_key_values (Optional[Any]): provide the values of partition key.
        ## Returns:
            str: A message indicating that delete operation is successfull or not.
        """
        try:
            items = self.query_items(query=f"SELECT * FROM C WHERE C.id ='{item_id}'")
            if not items:
                return "Item not found"
            if partition_key_values is None:
                properties = self.container.read()
                if properties["partitionKey"]["paths"]:
                    partition_key = properties["partitionKey"]["paths"]
                partition_key_values = [
                    items[0].get(key.strip("/")) for key in partition_key
                ]
            self.container.delete_item(item=item_id, partition_key=partition_key_values)
        except exceptions.CosmosResourceNotFoundError as e:
            print(f"Item not found: {e}")
            return "Item not found"
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error deleting item: {e}")
            # raise e
        return "Item Deleted Successfully"

    def __str__(self):
        """String representation of the CosmosCRUDService class."""
        return "CosmosCRUDService(database_name={}, container_name={},partition_key_path={})".format(
            self.database_name, self.container_name, self.partition_key_path
        )
