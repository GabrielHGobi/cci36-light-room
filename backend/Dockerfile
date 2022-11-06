FROM python:3.8-alpine

RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk --no-cache --update-cache add gcc gfortran build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install numpy

WORKDIR /usr/src/app

RUN apk add --update nodejs npm

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "node", "index.js" ]
