#!/bin/bash

USERNAME=$1
PASSWORD=$2
REPO_NAME=$3

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR/target/repository

for file in ./*
do
	curl -v --user "$USERNAME:$PASSWORD" --upload-file ${file} http://nexus:8081/repository/${REPO_NAME}/${file}
done;

for file in plugins/*
do
	curl -v --user "$USERNAME:$PASSWORD" --upload-file ${file} http://nexus:8081/repository/${REPO_NAME}/${file}
done;
