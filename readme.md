# New OpenML API Prototyping

This repository contains some prototyping work for a new python-based OpenML API.
These prototypes serve (part of) the production database through both a REST API and a GraphQL API.

Developed and tested on MacOS 12.4 with Python 3.10.

## Setup

### Database

The first thing you need to set up is the OpenML database.
You can run the MySQL database in a Docker container.
See this [readme](database/readme.md) in the `database` directory on how to start the server.

### Dependencies

You need to install a `mysql` client before installing the Python dependencies (specifically `mysqlclient`).

Then install all dependencies in `requirements.txt`:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## REST API

Using the REST API:

- Run `uvicorn main:app`, which starts the app at `127.0.0.1:8000` (optionally set a different port with `--port INT`).
- `test_main.py` runs unit tests (currently just a direction comparison to the production server for the first 100 datasets)

Current functionality:

- `/dataset/DATASET_ID` retrieves JSON similar to production.

### REST API Example

Querying `http://127.0.0.1:8001/dataset/61` gives:

```json
{
  "citation": "https://archive.ics.uci.edu/ml/citation_policy.html",
  "collection_date": "1936",
  "creator": "R.A. Fisher",
  "default_target_attribute": "class",
  "description": "**Author**: R.A. Fisher  \n**Source**: [UCI](https://archive.ics.uci.edu/ml/datasets/Iris) - 1936 - Donated by Michael Marshall  \n**Please cite**:   \n\n**Iris Plants Database**  \nThis is perhaps the best known database to be found in the pattern recognition literature.  Fisher's paper is a classic in the field and is referenced frequently to this day.  (See Duda & Hart, for example.)  The data set contains 3 classes of 50 instances each, where each class refers to a type of iris plant.  One class is     linearly separable from the other 2; the latter are NOT linearly separable from each other.\n\nPredicted attribute: class of iris plant.  \nThis is an exceedingly simple domain.  \n \n### Attribute Information:\n    1. sepal length in cm\n    2. sepal width in cm\n    3. petal length in cm\n    4. petal width in cm\n    5. class: \n       -- Iris Setosa\n       -- Iris Versicolour\n       -- Iris Virginica",
  "file_id": "61",
  "format": "ARFF",
  "language": "English",
  "licence": "Public",
  "name": "iris",
  "original_data_url": "https://archive.ics.uci.edu/ml/datasets/Iris",
  "paper_url": "http://digital.library.adelaide.edu.au/dspace/handle/2440/15227",
  "upload_date": "2014-04-06T23:23:39",
  "url": "https://api.openml.org/data/v1/download/61/iris.arff",
  "version": "1",
  "version_label": "1",
  "visibility": "public",
  "status": "active",
  "processing_date": "2020-11-20 19:02:18",
  "description_version": "1",
  "tag": [
    "study_1",
    "study_25",
    "study_4",
    "study_41",
    "study_50",
    "study_52",
    "study_7",
    "study_86",
    "study_88",
    "study_89",
    "uci"
  ],
  "id": "61",
  "md5_checksum": "ad484452702105cbf3d30f8deaba39a9",
  "parquet_url": "http://openml1.win.tue.nl/dataset61/dataset_61.pq",
  "minio_url": "http://openml1.win.tue.nl/dataset61/dataset_61.pq"
}
```

_note:_ I set the app port to 8001 in this example.

## GraphQL API

- `graphql-main.py` starts the app on `127.0.0.1:8000/graphql`.

Example GraphQL queries with example output:

```graphql
query DatasetWithUploader {
  allDataset(first: 1) {
    edges {
      node {
        did
        name
        users {
          firstName
          lastName
        }
        file {
          md5Hash
          filesize
        }
      }
    }
  }
}
```

produces:

```json
{
  "data": {
    "allDataset": {
      "edges": [
        {
          "node": {
            "did": "1",
            "name": "anneal",
            "users": {
              "firstName": "Jan",
              "lastName": "van Rijn"
            },
            "file": {
              "md5Hash": "43b29a3eb09e8fac9a8525c3c83abec8",
              "filesize": 143338
            }
          }
        }
      ]
    }
  }
}
```

Fetching data from a single table:

```graphql
query userBasicInfo {
  allUsers {
    edges {
      node {
        firstName
        lastName
        company
      }
    }
  }
}
```

output:

```json
{
  "data": {
    "allUsers": {
      "edges": [
        {
          "node": {
            "firstName": "Jan",
            "lastName": "van Rijn",
            "company": "Leiden University"
          }
        },
        {
          "node": {
            "firstName": "Joaquin",
            "lastName": "Vanschoren",
            "company": "Eindhoven University of Technology"
          }
        }
      ]
    }
  }
}
```
