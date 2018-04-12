#!/usr/bin/env bash

# exec in DB container
psql -U postgres -c "CREATE USER $POSTGRES_USER PASSWORD '$POSTGRES_PASSWORD'"
psql -U postgres -c "CREATE DATABASE leopay;"