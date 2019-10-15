#!/usr/bin/env bash

AWS_IP=205.156.8.85
AWS_DATA_PATH=/data/mv_data/

# Get the number of arguments.
NARGS=$#
ARGS=("$@")
LOAD_DIRS=()


# Print usage
usage() {
   echo "USAGE: mv_load_to_aws.sh <user_name> <base_dir> <xml_file>"
   echo "       <user_name>             AWS user name"
   echo "       <base_dir>              base directory for the data files "
   echo "       <xml_file>              XML file for loading"
   echo "       [subdirs]               Subdirs of <base_dir> to be transferred (optional)"

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
BASE_DIR=$2
XML_FILE=$3
XML_FILE_NAME=$(basename $XML_FILE)

#collect included subdirs from the command line
for((i=3; i<$NARGS; i++)); do
   LOAD_DIRS+=("$BASE_DIR/${ARGS[$i]}")
done

run_command "cd ${BASE_DIR}"

if [[ ${#LOAD_DIRS[@]} -eq 0 ]]; then
   run_command "scp -r ./* ${USER_NAME}@${AWS_IP}:/${AWS_DATA_PATH}${USER_NAME}"
else

  #copy subdirs or base_dir
  for((i=0; i<${#LOAD_DIRS[@]}; i++)); do
    run_command "scp -r ${LOAD_DIRS[$i]} ${USER_NAME}@${AWS_IP}:/${AWS_DATA_PATH}${USER_NAME}"
  done
fi

#copy XML to user's home dir on AWS
run_command "scp ${XML_FILE} ${USER_NAME}@${AWS_IP}:~"

#run load on AWS
ssh ${USER_NAME}@${AWS_IP} "/opt/metviewer/bin/mv_load_aws.sh ${USER_NAME} ${XML_FILE_NAME}"
