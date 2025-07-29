from azurex.cosmos import CosmosCRUDService

cosmos_service = CosmosCRUDService(
    "TestDB", ["/id", "/partition_key1", "/partition_key2"], "TestContainer"
)


def test_create_item():
    item1 = cosmos_service.create_item(
        item={
            "id": "1",
            "partition_key1": "value1",
            "partition_key2": "value2",
            "TestKey": "TestValue",
        }
    )

    assert item1 in ["Item Created Successfully", "Item already exists"]


def test_query_items():
    query = "SELECT * FROM C"
    items = cosmos_service.query_items(query=query)
    assert isinstance(items, list)


def test_update_item():
    updated_item = {
        "id": "1",
        "partition_key1": "value1",
        "partition_key2": "value2",
        "TestKey": "NewTestValue",
        "TempKey": "TempValue",
    }
    item = cosmos_service.update_item(item_id="1", updated_item=updated_item)
    assert isinstance(item, dict)


def test_delete_item():
    item = cosmos_service.delete_item(item_id="1")
    assert item in ["Item Deleted Successfully", "Item not found"]


def test_delete_item_with_partition_keys():
    result = cosmos_service.create_item(
        item={
            "id": "2",
            "partition_key1": "value1",
            "partition_key2": "value2",
            "TestKey": "TestValue",
        }
    )
    assert result == "Item Created Successfully" or "Item already exists"
    item = cosmos_service.delete_item(item_id="2")
    assert item in ["Item Deleted Successfully", "Item not found"]


def test_str_representation():
    assert (
        str(cosmos_service)
        == "CosmosCRUDService(database_name=TestDB, container_name=TestContainer,partition_key_path=['/id', '/partition_key1', '/partition_key2'])"
    )
