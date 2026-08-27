#!/bin/sh
set -eu

: "${PORT:=8080}"
: "${PUBLIC_BASE_URL:=http://localhost:${PORT}}"
: "${EUDI_API_URL:=http://localhost:${PORT}}"

export PORT PUBLIC_BASE_URL EUDI_API_URL

envsubst '${PORT}' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
