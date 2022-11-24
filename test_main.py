import json
from fastapi.testclient import TestClient
from main import app
import requests
import pytest

client = TestClient(app)

filetable_too_small = {2, 15, 62}  # because only first 2k rows
private_datasets = {45, 47} #  412
missing_datasets = set(list(range(63, 70)) + list(range(79, 101)))  # 111
downloadable_datasets = set(range(1, 101)) - filetable_too_small - private_datasets - missing_datasets

@pytest.mark.parametrize("dataset_id", downloadable_datasets)
def test_compare_downloadable(dataset_id):
  fastapi_response = client.get(f"/dataset/{dataset_id}")
  assert fastapi_response.status_code == 200

  live_response = requests.get(f"https://api.openml.org/api/v1/json/data/{dataset_id}")
  assert live_response.status_code == 200

  assert fastapi_response.json() == live_response.json()["data_set_description"]

@pytest.mark.parametrize("dataset_id", private_datasets)
def test_compare_private(dataset_id):
  fastapi_response = client.get(f"/dataset/{dataset_id}")
  assert fastapi_response.status_code == 412

  live_response = requests.get(f"https://api.openml.org/api/v1/json/data/{dataset_id}")
  assert live_response.status_code == 412

  assert fastapi_response.json()["detail"] == live_response.json()


@pytest.mark.parametrize("dataset_id", missing_datasets)
def test_compare_missing_datasets(dataset_id):
  fastapi_response = client.get(f"/dataset/{dataset_id}")
  assert fastapi_response.status_code == 412

  live_response = requests.get(f"https://api.openml.org/api/v1/json/data/{dataset_id}")
  assert live_response.status_code == 412

  assert fastapi_response.json()["detail"] == live_response.json()
