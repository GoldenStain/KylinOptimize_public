#!/bin/bash

sudo python3 main.py -p 5000 &
python3 -m webbrowser -t http://localhost:5000
