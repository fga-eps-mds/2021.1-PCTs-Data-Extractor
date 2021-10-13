FROM python:3.8

COPY . /app

WORKDIR /app

RUN apt-get update &&\
    apt-get install -y python3-pip &&\
    pip install -r requirements.txt

# Prepare chrome for selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - &&\
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' &&\
    apt-get -y update &&\
    apt-get install -y google-chrome-stable


# Heroku
CMD ./scripts/start_prod.sh
