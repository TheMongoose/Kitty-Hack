!#/bin/bash
sudo apt install python3-full git
git clone https://github.com/TheMongoose/Kitty-Hack
cd Kitty-Hack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 download.py
