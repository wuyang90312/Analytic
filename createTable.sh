#!/bin/bash
user="root"
password="user1234"

# set up the mysql database
mysql --user="$user" --password="$password" < "Config_Table.sql"

# run python
sudo python server.py
