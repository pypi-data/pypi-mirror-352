#!/bin/bash
set -e
python manage.py initdb std demo_users csv2db checkdata checksummaries
# python manage.py initdb std demo_users csv2db demo2 checkdata checksummaries
# python manage.py initdb std demo_users csv2db demo2
