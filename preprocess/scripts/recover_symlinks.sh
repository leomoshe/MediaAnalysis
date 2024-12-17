#!/bin/bash

# Text file containing symbolic link information
symlinks_file="./symlinks.txt"

# Iterate through the text file and recreate symbolic links
while read -r line; do
  # Extract symbolic link name and target path
  symbolic_link=$(echo "$line" | cut -d' ' -f1)
  target_path=$(echo "$line" | cut -d' ' -f2-)

  # Recreate the symbolic link in the new system
  ln -s "$target_path" "$symbolic_link"
done < "$symbolic_links_file"
