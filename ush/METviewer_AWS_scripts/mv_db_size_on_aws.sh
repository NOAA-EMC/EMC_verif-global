#!/usr/bin/env bash

# Get the number of arguments.
NARGS=$#


# Print usage
usage() {
   echo "USAGE: mv_db_size_on_aws.sh <user_name>"
   echo "       <user_name>            AWS user name"
}

# Check for 1 arguments
if [[ ${NARGS} -ne 1 ]]; then
   usage
   exit 1
fi

# Parse the command line
USER_NAME=$1

# execure db size script on AWS
ssh ${USER_NAME}@205.156.8.85 "/opt/metviewer/bin/mv_db_size.sh" | column -t
