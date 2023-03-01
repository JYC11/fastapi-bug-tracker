#!/bin/bash
set -e

psql postgres <<-EOSQL
    CREATE USER jason WITH ENCRYPTED PASSWORD '1234' SUPERUSER;
    CREATE DATABASE bug_tracker OWNER jason;
	CREATE DATABASE bug_tracker_test OWNER jason;
EOSQL