#!/usr/bin/env bash
pip freeze > requirements.txt

sed -e '/dokidokimd/d' -i ./requirements.txt