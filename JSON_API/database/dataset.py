from collections import defaultdict
from typing import Iterable

from sqlalchemy import create_engine, text

exp_db = create_engine(
    "mysql://root:ok@127.0.0.1:3306/openml_expdb",
    echo=True,
    future=True,
)


def get_features_for_dataset(dataset_id: int) -> dict:
    columns = ["`index`", "name", "data_type", "is_target", "is_ignore", "is_row_identifier", "NumberOfMissingValues"]

    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT {', '.join(columns)} 
            FROM data_feature 
            WHERE did={dataset_id};
            """
        ))

    columns[columns.index("`index`")] = "index"
    features = [dict(zip(columns, values)) for values in result]

    if any(feature["data_type"] == "nominal" for feature in features):
        with exp_db.connect() as conn:
            result = conn.execute(text(
                f"""
                SELECT `index`, value 
                FROM data_feature_value 
                WHERE did={dataset_id};
                """
            ))
        values_per_feature = defaultdict(list)
        for index, value in result:
            values_per_feature[index].append(value)

        for feature in features:
            if feature["data_type"] == "nominal":
                feature["nominal_value"] = values_per_feature[feature["index"]]

    return features


def list_dataset_qualities() -> Iterable:
    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT name
            FROM quality 
            WHERE type='DataQuality';
            """
        ))

    return (name for name, in result)


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
