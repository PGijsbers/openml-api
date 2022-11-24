import functools
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

@functools.cache
def get_column_names(table: str):
  with openml_db.connect() as conn:
    result = conn.execute(text(
      f"""
      SELECT column_name
      FROM INFORMATION_SCHEMA.COLUMNS
      WHERE TABLE_NAME=N'{table}';
      """
    ))
  return [colname for colname, in result.all()]

def row_as_dictionary(column_names):
  """ Wrap a single row result into a dictionary. """
  def decorator(func):
    def wrapper(*args, **kwargs):
      result = func(*args, **kwargs)
      row = result.all()[0]
      return dict(zip(column_names, row))
    return wrapper
  return decorator

def get_dataset_tags(dataset_id: int) -> dict:
  with exp_db.connect() as conn:
    result = conn.execute(text(
      f"""
      SELECT tag
      FROM dataset_tag
      WHERE id={dataset_id}
      """
    ))
  return {"tag": [t for t, in result.all()]}

@row_as_dictionary(["description_version"])
def get_dataset_description_version(dataset_id: int) -> dict:
  with exp_db.connect() as conn:
    return conn.execute(text(
      f"""
      SELECT version
      FROM dataset_description
      WHERE did={dataset_id}
      ORDER BY version DESC 
      LIMIT 1;
      """
    ))

@row_as_dictionary(["description"])
def get_dataset_description(dataset_id: int) -> dict:
  with exp_db.connect() as conn:
    return conn.execute(text(
      f"""
      SELECT description
      FROM dataset_description
      WHERE did={dataset_id}
      ORDER BY version DESC 
      LIMIT 1;
      """
    ))

@row_as_dictionary(["md5_hash"])
def get_dataset_checksum(file_id: int) -> dict:
  with openml_db.connect() as conn:
    return conn.execute(text(
      f"""
      SELECT md5_hash
      FROM file
      WHERE id={file_id}
      ORDER BY creation_date DESC
      LIMIT 1;
      """
    ))

@row_as_dictionary(["processing_date"])
def get_dataset_processing_date(dataset_id: int) -> dict:
  with exp_db.connect() as conn:
    return conn.execute(text(
      f"""
      SELECT processing_date
      FROM data_processed
      WHERE did={dataset_id}
      ORDER BY processing_date DESC 
      LIMIT 1;
      """
    ))

@row_as_dictionary(["status"])
def get_dataset_status(dataset_id: int) -> dict:
  with exp_db.connect() as conn:
    return conn.execute(text(
      f"""
      SELECT status
      FROM dataset_status
      WHERE did={dataset_id};
      """
    ))


@functools.cache
def get_dataset(dataset_id: int) -> dict:
  columns = get_column_names("dataset")
  with exp_db.connect() as conn:
    result = conn.execute(text(
      f"""
      SELECT {', '.join(columns)}
      FROM dataset
      WHERE did={dataset_id};
      """
    ))
  row = result.all()[0]
  return dict(zip(columns, row))
  