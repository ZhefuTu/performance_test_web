#!/bin/bash

ps x | grep 8000 | grep -v grep | awk '{print $1}' | xargs kill -9
