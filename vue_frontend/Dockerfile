# Use an official Node.js runtime as a parent image
FROM node:23-alpine AS builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Command to run the application
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist/ /app
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
