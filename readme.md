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
