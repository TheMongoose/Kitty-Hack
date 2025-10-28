!#/bin/bash
sudo apt install python3-full
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 download.py
