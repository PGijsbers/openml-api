To setup an SQL server with OpenML data, follow these steps:

1. `docker network create NETWORKNAME` (optional), you need a docker network to connect other docker containers (server and client).
   This command shows how to create a new one (where `NETWORKNAME` is the name that identifies the network).

1. `docker run -v LOCAL_DIRECTORY_WITH_SQL_FILE:/docker-entrypoint-initdb.d -e MYSQL_ROOT_PASSWORD=SOME_PASSWORD --name SERVER_CONTAINER_NAME --network NETWORKNAME -d mysql`, where:

   - `LOCAL_DIRECTORY_WITH_SQL_FILE` refers to the local directory which contains the `.sql` backup of the database.
   - `SOME_PASSWORD` is
   - `SERVER_CONTAINER_NAME` is a name you choose to identify the docker container

1. `docker run -it --network NETWORKNAME --rm mysql mysql -hSERVER_CONTAINER_NAME -uSQL_USER_NAME -p` to create a docker container running `MySQL` monitor that connects to the server, where:

If you try to connect to the sql server quickly after starting the server, you might get the message `ERROR 2003 (HY000): Can't connect to MySQL server on 'sqlserver:3306' (111)`. Just wait a moment while the sql server is reinitializing the database, you should be able to connect in a minute.

```
docker network create sql-network
docker run -v ~/repositories/openml-api/database/data:/docker-entrypoint-initdb.d -e MYSQL_ROOT_PASSWORD=ok --name sqlserver --network sql-network -p 3306:3306 -d mysql
```

to connect from a docker container:

```
docker run -it --network sql-network --rm mysql mysql -hsqlserver -uroot -p
```

to connect from a local mysql-client:

```
mysql --host 127.0.0.1 --port=3306
```
