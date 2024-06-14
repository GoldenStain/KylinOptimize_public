#!/bin/bash

npm run build
rm -r ../static/*
mv dist/* ../static