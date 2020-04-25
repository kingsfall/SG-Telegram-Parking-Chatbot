FROM nodered/node-red

USER root

RUN sed -i 's/http\:\/\/dl-cdn.alpinelinux.org/https\:\/\/alpine.global.ssl.fastly.net/g' /etc/apk/repositories

RUN set -xe && \
    apk update && \
    apk add py-pip

RUN python3.8 -m pip install --upgrade pip && \
    python3.8 -m pip install --no-cache-dir argparse requests

COPY combinedCarparkDB.txt copiedFiles/
COPY getlatlong_nouserinput.py copiedFiles/

RUN npm install node-red-contrib-telegrambot && \
    npm install node-red-dashboard

COPY flows.json /data/flows.json

# Start the container normally
CMD ["npm", "start"]
