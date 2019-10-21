#!/usr/bin/env bash

AWS_IP=205.156.8.85

# Get the number of arguments.
NARGS=$#
ARGS=("$@")


# Print usage
usage() {
   echo "USAGE: mv_batch_on_aws.sh <user_name> <plots_dir> <xml_file>"
   echo "       <user_name>             AWS user name"
   echo "       <xml_file>              XML file for batch"

}

# Check for 3 arguments
if [[ ${NARGS} -ne 2 ]]; then
   usage
   exit 1
fi

# Sub-routine for running a command and checking return status
run_command() {

  # Print the command being called
  echo "CALLING: $1"

  # Run the command and store the return status
  $1
  STATUS=$?

  # Check return status
  if [[ ${STATUS} -ne 0 ]]; then
     echo "ERROR: Command returned with non-zero status ($STATUS): $1"
     exit ${STATUS}
  fi

  return ${STATUS}
}


# Parse the command line
USER_NAME=$1
XML_FILE=$2
XML_FILE_NAME=$(basename $XML_FILE)

#copy XML to AWS user's home directory
run_command "scp ${XML_FILE} ${USER_NAME}@${AWS_IP}:~"

#run prune on AWS
ssh ${USER_NAME}@${AWS_IP} "/opt/metviewer/bin/mv_prune_aws.sh ${USER_NAME} ${XML_FILE_NAME}"
