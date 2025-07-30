#! /bin/bash

DEBUG=false
# set -x

get_parent_hashes() {
	hash=$1
	git cat-file -p ${hash}^{commit} | grep '^parent' | awk '{print $2}'
}

get_files_for_hash() {
	hash=$1
	git diff --name-only  ${hash}~ ${hash} | cat
}

# @TODO also checked for tagged?
# PRO MEMORI: git describe --exact-match ${hash}
is_empty_commit() {
	hash=$1
	if [ -z "$(git diff --numstat ${hash}~ ${hash})" ] ; then
		return 0
	else
		return 1
	fi
}

find_change_for_path() {
	hash=$1
	path=$2

	if ${DEBUG}; then
		echo ${hash}
		get_files_for_hash ${hash}
	fi

	if get_files_for_hash ${hash} | grep "^${path}" 2>&1 > /dev/null ||
		is_empty_commit ${hash}; then
		echo ${hash}
		return 0
	fi

	for parentHash in `get_parent_hashes ${hash}`; do
		if find_change_for_path ${parentHash} ${path}; then
			return 0
		fi
	done

	return 1; # not found
}

set -e

target_repo=$1
start_commit_hash=$2
path=$3

if [ "${path}" = "." ] ; then
	echo "${start_commit_hash}"
	exit 0
fi

cd ${target_repo}

# Check if path exists ; cannot search for changes in non-existent path
git show ${start_commit_hash}:${path} > /dev/null || exit 1

find_change_for_path ${start_commit_hash} ${path}
