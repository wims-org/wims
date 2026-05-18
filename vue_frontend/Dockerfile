FROM node:25-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build --prod 

FROM nginx:alpine
COPY --from=builder /app/dist/ /app
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
