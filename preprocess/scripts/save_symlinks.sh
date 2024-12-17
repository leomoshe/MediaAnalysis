#!/bin/bash

# Source directory to process
source_directory="/home/leoz/.cache/huggingface/hub/models--ivrit-ai--whisper-large-v2-tuned/snapshots/53796d8dafd68c6ea2a189d1e4b8715afe36628f/"

# Output file to store symbolic links
symlinks_file="./symlinks.txt"

# Recursively traverse the directory structure
find "$source_directory" -type l | while read -r symbolic_link; do
  # Get the absolute path of the symbolic link
  absolute_path=$(realpath "$symbolic_link")

  # Store the absolute path of the symbolic link in the output file
  echo "$symbolic_link -> $absolute_path" >> "$symlinks_file"
done
