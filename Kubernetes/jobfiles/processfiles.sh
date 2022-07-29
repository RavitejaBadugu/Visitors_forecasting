#!/bin/sh
aws configure import --csv file://restaurant-project-user_accessKeys.csv
python get_data_from_s3.py
python preprocess.py
python insert_into_tables.py
python inference-of-restaurants-visitors.py