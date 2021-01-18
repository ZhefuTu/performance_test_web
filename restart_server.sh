#!/bin/bash
ps x | grep 8000 | grep -v 'grep' | awk '{print $1}' | xargs kill -9
nohup python manage.py runserver 0.0.0.0:8000 &
