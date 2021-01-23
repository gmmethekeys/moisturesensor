#!/bin/sh

echo "Starting plant monitor..."

while :
do
	now=$(date +"%T")
	python insert.py
	echo "Plant sensor info updated at $now."
	sleep 1h
done
