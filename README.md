# Sign-up to a Netatmo Developer Account

Here: https://auth.netatmo.com/en-gb/access/signup

Create an app after signing up, this will provide you with API keys: https://dev.netatmo.com/apps/createanapp

# Add API keys to Auth File

  - Add .netatmo.credentials.json file to the directory where this repo is cloned.

  - File format located at: /home/ewalsh/hm_home/test/netatmo_auth/.netatmo.credentials.json

  - Edit this file to include a CLIENT_ID, CLIENT_SECRET, and REFRESH_TOKEN keys.

# To be Explained..

add path to conda.sh on the local machine to the bash file in the directory - point to ewalsh miniforge directory and see if that works.

install python 3.12.6 and then conda install pip

conda install -c conda-forge cfgrib
