#!/bin/bash
# Gather citizen data from both netatmo weather stations and the weather underground website
# Author: Eoin Walsh
# Date: 2025-01-29

Date="2024-10-28" #YYYY-MM-DD

Directory="/nfs/archive/prod/archive/Harmonie/HECTOR" #directory address to the HECTOR grib files

source ~/miniforge3/etc/profile.d/conda.sh

conda activate test

python netatmo_V2_EOIN.py $Date

python wundermap_data_acq.py $Date

python gridpp_v1.py $Date $Directory

