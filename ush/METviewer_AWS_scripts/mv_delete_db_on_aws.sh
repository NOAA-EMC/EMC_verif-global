#!/usr/bin/env bash

# Get the number of arguments.
NARGS=$#


# Print usage
usage() {
   echo "USAGE: mv_delete_db_on_aws.sh <user_name> <database_name>"
   echo "       <user_name>            AWS user name"
   echo "       <database_name>        name of the database to be deleted"
}

# Check for 2 arguments
if [[ ${NARGS} -ne 2 ]]; then
   usage
   exit 1
fi

# Parse the command line
USER_NAME=$1
DATABASE_NAME=$2

#execute delete db script on AWS
ssh ${USER_NAME}@205.156.8.85 "/opt/metviewer/bin/mv_delete_db.sh ${USER_NAME} ${DATABASE_NAME}"
