#! /bin/bash
sudo apt update && apt upgrade -y
sudo apt install libvoikko1 voikko-fi -y
curl https://sh.rustup.rs -sSf | sh -s -- -y
rustup override set 1.79.0
rustup default 1.79.0
pip install --upgrade pip
pip install -r requirements.txt
python -m nltk.downloader -d all