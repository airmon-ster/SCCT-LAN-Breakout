#!/bin/bash
# Make sure you have jq and unzip installed: These tools are used for parsing JSON and extracting ZIP files, respectively. Install them using your package manager if not already installed (e.g., sudo apt install jq unzip on Debian/Ubuntu).
# Save the script: Copy the above script into a file, for example, update_script.sh.
# Make it executable: Run chmod +x update_script.sh to make your script executable.
# Execute the script: Run ./update_script.sh to execute the script.
# Set the repository owner and repository name
# ---
REPO_OWNER="airmon-ster"
REPO_NAME="SCCT-LAN-Breakout"

# GitHub API URL to fetch the latest release
API_URL="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"

# Use curl to fetch the latest release data
# Extracting the browser_download_url and the release name
DOWNLOAD_URL=$(curl -s $API_URL | jq -r '.assets[0].browser_download_url')
LATEST_RELEASE=$(curl -s $API_URL | jq -r '.assets[0].name')

# Check if download URL is found
if [ -z "$DOWNLOAD_URL" ]; then
  echo "No download URL found. Exiting."
  exit 1
fi

# Read the current release file name from the 'release' file if it exists
if [ -f "release" ]; then
  read -r CURRENT_RELEASE < release
else
  CURRENT_RELEASE="NONE"
fi

# Print the current and latest release names
echo "CURRENT_RELEASE: $CURRENT_RELEASE"
echo "LATEST_RELEASE: $LATEST_RELEASE"

# Compare the current release with the latest release
if [ "$CURRENT_RELEASE" = "$LATEST_RELEASE" ]; then
  echo "Current release is up to date."
  exit 0
fi

# Echo the download URL (for verification)
echo "Download URL: $DOWNLOAD_URL"

# Download the zip file
echo "Downloading latest release..."
curl -L $DOWNLOAD_URL -o "$LATEST_RELEASE"

# Unzip the file into the current directory
echo "Extracting the archive..."
unzip -o "$LATEST_RELEASE"

# Cleanup
echo "Cleanup done. Removing downloaded zip file..."
rm "$LATEST_RELEASE"

# Update the 'release' file with the new release name
echo "$LATEST_RELEASE" > release

echo "Your folder has been updated."

sleep 3