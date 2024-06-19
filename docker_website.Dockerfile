FROM node:22

RUN mkdir /website
COPY ./website /website
WORKDIR /website

RUN yarn && yarn build-local

CMD [ "yarn", "preview", "--host", "0.0.0.0"]