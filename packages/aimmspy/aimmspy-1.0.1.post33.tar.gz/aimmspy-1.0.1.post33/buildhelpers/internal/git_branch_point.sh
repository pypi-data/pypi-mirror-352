#! /bin/bash

DEBUG=false
# set -x

target_repo=$1
branch_name=$2
parent_branch_name=$3

cd ${target_repo}

diff -u <(git rev-list --first-parent ${branch_name}) <(git rev-list --first-parent ${parent_branch_name}) \
	| sed -ne 's/^ //p' \
	| head -1
