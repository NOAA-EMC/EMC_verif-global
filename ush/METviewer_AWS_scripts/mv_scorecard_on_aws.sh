#!/usr/bin/env bash

AWS_IP=205.156.8.85
AWS_DATA_PATH=/data/mv_data/

# Get the number of arguments.
NARGS=$#
ARGS=("$@")


# Print usage
usage() {
   echo "USAGE: mv_scorecard_on_aws.sh <user_name> <scorecard_dir> <xml_file>"
   echo "       <user_name>             AWS user name"
   echo "       <scorecard_dir>         directory on WCOSS  scorecard will be copied to"
   echo "       <xml_file>              XML file for scorecard"

}

# Check for 3 arguments
if [[ ${NARGS} -ne 3 ]]; then
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
SCORECARD_DIR=$2
XML_FILE=$3
XML_FILE_NAME=$(basename $XML_FILE)

#copy XML file to user's home directory on AWS
run_command "scp ${XML_FILE} ${USER_NAME}@${AWS_IP}:~"

#run batch script on AWS
ssh ${USER_NAME}@${AWS_IP} "/opt/metviewer/bin/mv_scorecard_aws.sh ${USER_NAME} ${XML_FILE_NAME}"

#copy result to the scorecard directory on WCOSS
run_command "scp ${USER_NAME}@${AWS_IP}:/$AWS_DATA_PATH/$USER_NAME/plots/* ${SCORECARD_DIR}"

# remove the resupt from AWS
ssh ${USER_NAME}@${AWS_IP} "rm $AWS_DATA_PATH/$USER_NAME/plots/*"
