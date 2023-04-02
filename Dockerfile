FROM node

# create app directory
WORKDIR /usr/src/app/demo

# install dependencies
ADD package*.json /usr/src/app/demo/
RUN npm install

COPY demo/ /usr/src/app/demo

# run application
EXPOSE 8000
CMD npm start