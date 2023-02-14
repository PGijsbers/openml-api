from fastapi import FastAPI, HTTPException
from database import get_dataset, get_dataset_checksum, get_dataset_description, get_dataset_description_version, get_dataset_processing_date, get_dataset_status, get_dataset_tags

app = FastAPI()

@app.get("/")
def read_no_query():
  return {"message": "This is a REST API for OpenML with JSON."}

@app.get("/dataset/{dataset_id}")
def read_item(dataset_id: int):
  try:
    description = get_dataset(dataset_id)
  except IndexError:
    raise HTTPException(status_code=412, detail={"error": {"code":"111", "message": "Unknown dataset"}})
  else:
    if description["visibility"] == "private":
      raise HTTPException(status_code=412, detail={"error":{"code":"112","message":"No access granted"}})

  description = description | {
    **get_dataset_status(dataset_id),
    **get_dataset_processing_date(dataset_id),
    **get_dataset_checksum(description["file_id"]),
    **get_dataset_description_version(dataset_id),
    **get_dataset_description(dataset_id),
    **get_dataset_tags(dataset_id),
  }
  
  # ./openml_OS/models/api/v1/Api_data.php:      $dataset->url = BASE_URL . 'data/v1/download/' . $dataset->file_id . '/' . htmlspecialchars($dataset->name) . '.' . strtolower($dataset->format);
  description["url"] = f"https://api.openml.org/data/v1/download/{description['file_id']}/{description['name']}.{description['format'].lower()}"

  description["upload_date"] = description["upload_date"].strftime(r"%Y-%m-%dT%H:%M:%S")
  description["description"] = description["description"].replace("\r","").strip()
  description["id"] = description["did"]
  description["md5_checksum"] = description["md5_hash"]

  if description.get("collection_date"):
    description["collection_date"] = description["collection_date"].strip()

  for field in ["creator", "contributor"]:
    if isinstance(description.get(field), str):
      if ',' in description[field]:
        description[field] = [person.strip().replace('"', '') for person in description[field].split(",")]
      else:
        description[field] = [description[field].strip()]

  if isinstance(description.get("ignore_attribute"), str):
    description["ignore_attribute"] = description["ignore_attribute"].replace('"', '')

  # Parquet url only exists in the API, not the database:
  # ./openml_OS/models/api/v1/Api_data.php:767:      $dataset->parquet_url = 'http://openml1.win.tue.nl/dataset' . $data_id . '/dataset_' . $data_id . '.pq';
  minio_url = f"http://openml1.win.tue.nl/dataset{dataset_id}/dataset_{dataset_id}.pq"
  description["parquet_url"] = description["minio_url"] = minio_url

  return convert_dataset_description_to_old_format(description)

def convert_dataset_description_to_old_format(description):
  if description["description"] == "":
    description['description'] = []
  
  for field in ["creator", "contributor"]:
    if isinstance(description.get(field), list) and len(description[field]) == 1:
      description[field] = description[field][0]

  for k, v in description.items():
    if not isinstance(v, list):
      description[k] = str(description[k])

  if len(description["tag"]) == 1:
    description["tag"] = description["tag"][0]

  ignored_fields = [
    "did",
    "md5_hash",
    "isOriginal",
    "last_update",
    "uploader",
    "source",
    "update_comment",
  ]

  for field in [f for f in ignored_fields if f in description]:
    del description[field]

  return {k: v for k, v in description.items() if v is not None and v != 'None'}
