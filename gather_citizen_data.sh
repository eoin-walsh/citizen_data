#!/bin/bash
# Gather citizen data from both netatmo weather stations and the weather underground website
# Author: Eoin Walsh
# Date: 2025-01-29

Date="2025-01-01" #YYYY-MM-DD

source ~/miniconda3/etc/profile.d/conda.sh

conda activate netatmo

python netatmo_V2_EOIN.py $Date

python wundermap_data_acq.py $Date

