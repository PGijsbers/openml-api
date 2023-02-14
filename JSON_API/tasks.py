exp_db = None
text = lambda: None


def get_task(task_id: int) -> dict:
    return {
        "tag": _get_tags(task_id),
    }


def _get_tags(task_id: int) -> list[str]:
    # convert result to list
    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT tag 
            FROM task_tag 
            WHERE id={task_id};
            """
        ))
    tags = result.all()
    return tags


def _get_task_inputs(task_id: int) -> list[dict]:
    # input types may be defined multiple times (evaluation measures, source data, ...)
    # in practice, this is never done so I can't infer the schema.
    # So in this method we assume each `input` type is max only present once for each task.

    task_inputs = []
    # estimation procedure: get linked data
    # cost matrix: check reference tasks
    # find evaluation measure
    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT input, value 
            FROM task_tag 
            WHERE task_id={task_id};
            """
        ))
    inputs = {input_type: value for input_type, value in result.all()}

    if "source_data" in inputs:
        source_data = {
            "name": "source_data",
            "data_set": {
                "data_set_id": inputs["source_data"],
            }
        }

        optionals_fields = [
            "target_feature",
            "target_feature_left",
            "target_feature_right",
            "target_feature_event"
        ]
        for optional_field in optionals_fields:
            if optional_field in inputs:
                if inputs[optional_field]:
                    source_data["data_set"][optional_field] = inputs[optional_field]
                else:
                    source_data["data_set"][optional_field] = []

        task_inputs.append(source_data)

    task_inputs.append({
        "name": "cost_matrix",
        "cost_matrix": inputs.get("cost_matrix", []),
    })

    task_inputs.append({
        "name": "evaluation_measures",
        "evaluation_measures": inputs.get("evaluation_measures", []),
    })

    return task_inputs


def _get_estimation_procedure_info(procedure_id: int) -> dict:
    with exp_db.connect() as conn:
        result = conn.execute(text(
            f"""
            SELECT *
            FROM estimation_procedure 
            WHERE ttid={procedure_id};
            """
        ))
    row = result.all()[0]
    columns = [
        "id", "ttid", "name", "type", "repeats", "folds", "samples", "percentage",
        "stratified_sampling", "custom_testset", "date",
    ]
    result = dict(zip(columns, row, strict=True))
    # example with estimation 15
    procedure = {
        "id": result["id"],
        "type": result["type"],
        "data_splits_url": None,  # Template from other table"
        "parameter": []
    }

    return result
