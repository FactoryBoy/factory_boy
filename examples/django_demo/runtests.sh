#!/bin/sh

cd $(dirname $0)
python manage.py test;
