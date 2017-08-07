# Would prefer Ubuntu, but, this is going to run on a cheap VPS.
FROM python:3.5
#RUN apt-get update && apt-get -y install pip3
ADD private_chat private_chat
ADD requirements.txt requirements.txt
# Interacts with system python, but this is fine in this case.
RUN pip3 install -r requirements.txt
EXPOSE 8080
ENTRYPOINT cd private_chat && python3 app.py


