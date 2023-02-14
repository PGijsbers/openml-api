from collections import defaultdict
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text

openml_db = create_engine(
    "mysql://root:ok@127.0.0.1:3306/openml",
    echo=True,
    future=True,
)

exp_db = create_engine(
    "mysql://root:ok@127.0.0.1:3306/openml_expdb",
    echo=True,
    future=True,
)
app = FastAPI()


# WORKS / UNTESTED
@app.get("/dataset/features/{dataset_id}")
def get_features(dataset_id: int) -> dict:
    columns = ["`index`", "name", "data_type", "is_target", "is_ignore", "is_row_identifier", "NumberOfMissingValues"]

    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT {', '.join(columns)} 
            FROM data_feature 
            WHERE did={dataset_id};
            """
        ))

    # The database column name and expected JSON field name are cased differently:
    columns[columns.index("NumberOfMissingValues")] = "number_of_missing_values"
    columns[columns.index("`index`")] = "index"
    features = [dict(zip(columns, values)) for values in result.all()]

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
        for index, value in result.all():
            values_per_feature[index].append(value)

        for feature in features:
            if feature["data_type"] == "nominal":
                feature["nominal_value"] = values_per_feature[feature["index"]]

    return {
        "data_features": {
            # are there potential other keys in this dictionary?
            "feature": features
        }
    }


# WORKS / UNTESTED
@app.get("/dataset/qualities/list")
def data_qualities_list() -> dict:
    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT name
            FROM quality 
            WHERE type='DataQuality';
            """
        ))
    # print(result.all())
    return {
        "data_qualities_list": {
            "quality": [
                name for name, in result
            ]
        }
    }


# WORKS / UNTESTED
@app.get("/dataset/qualities/{dataset_id}")
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
