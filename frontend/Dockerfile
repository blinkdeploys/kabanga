FROM node:14.17.3

WORKDIR /

COPY package*.json ./

RUN yarn install

COPY . .

EXPOSE 8083

# CMD [ "yarn", "start" ]
