#!/bin/bash
# Gather citizen data from both netatmo weather stations and the weather underground website
# Author: Eoin Walsh
# Date: 2025-01-29

Date="2024-10-28" #YYYY-MM-DD

Directory="/home/ewalsh/Documents/projects/dublin_temps/grib" #directory address to the HECTOR grib files

source ~/miniconda3/etc/profile.d/conda.sh

conda activate netatmo

# python netatmo_V2_EOIN.py $Date

# python wundermap_data_acq.py $Date

python get_2m_temp_field.py $Date $Directory

