from typing import Iterable


def format_features(features: dict) -> dict:
    # The database column name and expected JSON field name are cased differently:
    for feature in features:
        feature["number_of_missing_values"] = feature["NumberOfMissingValues"]
        del feature["NumberOfMissingValues"]
    
    return {
        "data_features": {
            # are there potential other keys in this dictionary?
            "feature": features
        }
    }


def format_data_qualities_list(qualities: Iterable[str]) -> dict:
    return {
        "data_qualities_list": {
            "quality": list(qualities)
        }
    }


# WORKS / UNTESTED
def _get_dataset_qualities(dataset_id: int) -> dict:
    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT quality, value 
            FROM data_quality 
            WHERE data={dataset_id};
            """
        ))
    return {
        "data_qualities": {
            "quality": [
                {
                    "name": name,
                    "value": value
                } for name, value in result.all()
            ]
        }
    }


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
