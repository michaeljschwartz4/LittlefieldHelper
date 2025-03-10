#!/bin/bash
# Author: Michael Schwartz @mjschwa; UWB C/O 2025

# This script installs Homebrew (if needed), Python3, creates a virtual environment,
# installs required Python packages, and sets up a cron job to run littlefield-script.py hourly.
set -e

# Install Homebrew if not installed
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew is already installed."
fi

# Install Python3 if not installed
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 not found. Installing Python3 via Homebrew..."
  brew install python
else
  echo "Python3 is already installed."
fi

# Create a virtual environment in the current directory
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in ./$VENV_DIR ..."
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment '$VENV_DIR' already exists."
fi

# Activate the virtual environment and install required packages
echo "Activating virtual environment and installing required packages..."
source "$VENV_DIR/bin/activate"
pip3 install --upgrade pip
pip3 install mechanize beautifulsoup4 pandas openpyxl
deactivate

# Receive login credentials for the Littlefield team
read -p "Please enter your team's name: " team_name
read -p "Please enter your team's password: " password
# Set up a cron job to run the littlefield script every hour
# Get the absolute path of the current directory
SCRIPT_DIR=$(pwd)
CRON_JOB="0 * * * * cd $SCRIPT_DIR && ./venv/bin/python3 littlefield-script.py $team_name $password >> littlefield.log 2>&1"

# Check if the cron job already exists. If not, add it.
echo "Checking if cron job is already set up..."
(crontab -l 2>/dev/null | grep -F "$SCRIPT_DIR/venv/bin/python3 littlefield-script.py $team_name $password") && \
  echo "Cron job already exists." || \
  ( (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab - )

echo "Setup complete. The littlefield-script.py will run hourly via cron with credentials team_name: $team_name and password: $password."
