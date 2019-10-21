#!/usr/bin/env bash

AWS_IP=205.156.8.85
AWS_DATA_PATH=/data/mv_data/

# Get the number of arguments.
NARGS=$#
ARGS=("$@")


# Print usage
usage() {
   echo "USAGE: run_R_on_aws.sh <user_name> <R_script> <data_file> <local_dir>"
   echo "       <user_name>             AWS user name"
   echo "       <R_script>              R script file to run "
   echo "       <data_file>             data file for R script"
   echo "       <out_file>              name of the expected output file"
   echo "       <local_dir>             directory on WCOSS where R script and data_file are located and where the output will be copied to"
}

# Check for 4 arguments
if [[ ${NARGS} -ne 5 ]]; then
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
R_SCRIPT=$2
DATA_FILE=$3
OUT_FILE=$4
LOCAL_DIR=$5
REMOTE_DIR=${AWS_DATA_PATH}${USER_NAME}

#cd to local directory
run_command "cd ${LOCAL_DIR}"

#copy R script to AWS user's data directory
run_command "scp ${R_SCRIPT} ${USER_NAME}@${AWS_IP}:${REMOTE_DIR}"
#copy data_file to AWS user's data directory
run_command "scp ${DATA_FILE} ${USER_NAME}@${AWS_IP}:${REMOTE_DIR}"

#run Rscript on AWS
ssh ${USER_NAME}@${AWS_IP} "Rscript ${REMOTE_DIR}/${R_SCRIPT} ${REMOTE_DIR}/${DATA_FILE}"

#remove  files from AWS
ssh ${USER_NAME}@${AWS_IP} "rm ${REMOTE_DIR}/${R_SCRIPT}"
ssh ${USER_NAME}@${AWS_IP} "rm ${REMOTE_DIR}/${DATA_FILE}"

#look for the out file in remote dir if it is found copy and delete it
FILE=${REMOTE_DIR}/${OUT_FILE}
if ssh ${USER_NAME}@${AWS_IP} stat $FILE \> /dev/null 2\>\&1
then
  run_command "scp ${USER_NAME}@${AWS_IP}:$FILE ${LOCAL_DIR}"
  ssh ${USER_NAME}@${AWS_IP} "rm $FILE"
else
  #look in home
  FILE=/home/${USER_NAME}/${OUT_FILE}
  if ssh ${USER_NAME}@${AWS_IP} stat ${FILE} \> /dev/null 2\>\&1
  then
    run_command "scp ${USER_NAME}@${AWS_IP}:$FILE ${LOCAL_DIR}"
    ssh ${USER_NAME}@${AWS_IP} "rm $FILE"
  fi
fi
