**#CloudGuruChallenge**: Improve application performance using Amazon ElastiCache

The goal of this challenge, presented by ACloudGuru, is to demonstrate the power of Amazon ElastiCache to speed up data 
retrieval, relative to querying data on a relational database (in this case, a PostgreSQL instance of Amazon RDS).

The file included in this repository is the Flask app provided by the challenge creator (David Thomas), modified to 
query an Amazon ElastiCache cluster for certain data before establishing a connection to the database. Configuration 
details (database.ini, redis_host.py) are not included.