# Use an official Node.js runtime as a parent image
FROM node:18-alpine as build-stage

RUN npm install -g http-server

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
RUN ["npm", "run", "build"]
CMD [ "http-server", "-P", "http://0.0.0.0:8080?", "dist", "--cors" ]