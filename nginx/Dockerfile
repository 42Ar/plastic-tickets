FROM nginx:alpine

ENV SERVER_USER="http"
RUN adduser -D -g "$SERVER_USER" "$SERVER_USER"

ENV APP_PATH=/srv/plastic-tickets
RUN mkdir -p $APP_PATH
WORKDIR $APP_PATH

ENV APP_CONF=/etc/nginx/sites-available/plastic-tickets.conf
RUN mkdir -p $(dirname $APP_CONF)
COPY nginx.conf /etc/nginx/nginx.conf
COPY plastic-tickets-nginx.conf $APP_CONF

RUN rm /etc/nginx/conf.d/default.conf && \
    mkdir -p /etc/nginx/sites-enabled/ && \
    ln -sf $APP_CONF /etc/nginx/sites-enabled/ && \
    mkdir /etc/letsencrypt
