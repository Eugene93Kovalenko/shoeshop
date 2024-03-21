#FROM nginx:1.25-bookworm
#RUN rm /etc/nginx/conf.d/default.conf
#COPY nginx.conf /etc/nginx/conf.d

FROM jwilder/nginx-proxy:1.5

COPY default_location /etc/nginx/vhost.d/default_location