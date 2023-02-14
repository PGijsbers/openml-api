"""
Defines the REST API endpoints (URL, inputs).
Note: The order of endpoints is important when they are overloaded.
The matches are performed top to bottom, and types are ignored.
An example of this is:
 - /dataset/qualities/list
 - /dataset/qualities/{dataset_id}
If they were in reverse order, then `/dataset/qualities/list` would
be matched with the second statement, as `{dataset_id}="list"`.

"""
from fastapi import FastAPI

from database.dataset import get_features_for_dataset, list_dataset_qualities
from formatting.dataset import format_features, format_data_qualities_list

app = FastAPI()


# WORKS / UNTESTED
# @app.get("/dataset/{dataset_id}")
def dataset_get_by_id(dataset_id: int) -> dict:
    return "Not migrated yet."


# WORKS / UNTESTED
@app.get("/dataset/features/{dataset_id}")
def dataset_features_for_id(dataset_id: int) -> dict:
    """
    Get metadata on all features for dataset with id `dataset_id`.

    Params
    ------
     * **dataset_id**, `int`:
        The unique identifier of the dataset for which to retrieve metadata of the features.

    Returns
    -------
    Add a link to JSON Schema
    """
    features = get_features_for_dataset(dataset_id)
    return format_features(features)


# WORKS / UNTESTED
@app.get("/dataset/qualities/list")
def dataset_qualities() -> dict:
    """
    Get the names of all qualities which are evaluated on datasets by OpenML.

    Returns
    -------
    Add a link to JSON Schema
    """
    qualities = list_dataset_qualities()
    return format_data_qualities_list(qualities)


# WORKS / UNTESTED
# @app.get("/dataset/qualities/{dataset_id}")
def dataset_qualities_for_id(dataset_id: int) -> dict:
    # data
    # response
    pass


# /data/unprocessed/{data_engine_id}/{order: normal(:= ASC)|random}
def data_unprocessed(data_engine_id: int, order: str) -> dict:
    pass


# /data/list/{filters}
# limit: max number of results to return
# offset: first result to return
# status: active/deactivated/in_preparation
# tag: single
# {data_quality}/{range}
#   data_quality: id | name | version | n_instances | n_features | n_classes | n_missing
#   range: low..high
def data_list(limit, offset, **filters) -> dict:
    # first find all datasets which adhere to the filter, then apply limit/offset
    pass
