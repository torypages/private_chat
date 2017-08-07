#!/bin/bash

# THIS SCRIPT REMOVES USERS AND FILES, CAREFUL!!!!

apt-get update
apt-get -y upgrade
apt-get -y install python3 python3-pip nginx git

deluser clin || true
rm /home/clin -rf || true

adduser --system  --disabled-password --shell /bin/bash clin
pip3 install virtualenv
pip3 install --upgrade pip

sudo -u clin -i git clone https://github.com/torypages/private_chat.git /home/clin/private_chat
sudo -u clin -i virtualenv -p /usr/bin/python3 /home/clin/private_chat_venv
sudo -u clin -i /home/clin/private_chat_venv/bin/pip3 install -r private_chat/requirements.txt

cp /home/clin/private_chat/private_chat.nginx /etc/nginx/sites-available/private_chat.nginx
cd /etc/nginx/sites-enabled/
rm default || true
rm private_chat.nginx || true
ln -s /etc/sites-available/private_chat.nginx
service nginx restart