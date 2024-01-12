#!/bin/bash

src_dir="."
backup_dir="../backup"

current_date=$(date +"%Y%m%d")

echo "Starting backup process"
echo "------------------------------------------------"

# Check if backup directory exists, create if does not exist
if [ ! -d "$backup_dir" ]; then
    echo "Creating backup directory at $backup_dir"
    mkdir -p "$backup_dir"
fi

echo "Backing up project files from $src_dir to $backup_dir"
tar -czf "$backup_dir/backup_$current_date.tar.gz" -C "$src_dir" .
if [ $? -eq 0 ]; then echo "Backup successful"; else echo "Backup failed"; exit 1; fi
echo "------------------------------------------------"

echo "Backup Process Completed Successfully"
