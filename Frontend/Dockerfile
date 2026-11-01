FROM nginx:alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend static files
COPY index.html styles.css script.js /usr/share/nginx/html/

EXPOSE 80
