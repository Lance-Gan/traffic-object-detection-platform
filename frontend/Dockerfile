# syntax=docker/dockerfile:1.8

FROM node:24-alpine3.24 AS build

WORKDIR /workspace/frontend

COPY package.json \
    package-lock.json \
    ./

RUN npm ci

COPY . .

ARG VITE_API_BASE_URL=/api/v1
ARG VITE_MAX_IMAGE_UPLOAD_BYTES=26214400
ARG VITE_MAX_VIDEO_UPLOAD_BYTES=262144000
ARG VITE_MAX_VIDEO_DURATION_SECONDS=120

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_MAX_IMAGE_UPLOAD_BYTES=$VITE_MAX_IMAGE_UPLOAD_BYTES
ENV VITE_MAX_VIDEO_UPLOAD_BYTES=$VITE_MAX_VIDEO_UPLOAD_BYTES
ENV VITE_MAX_VIDEO_DURATION_SECONDS=$VITE_MAX_VIDEO_DURATION_SECONDS

RUN npm run build


FROM nginx:stable-alpine AS runtime

RUN rm -f \
        /etc/nginx/conf.d/default.conf \
    && mkdir -p \
        /srv/media \
        /tmp/client_temp \
        /tmp/proxy_temp \
        /tmp/fastcgi_temp \
        /tmp/uwsgi_temp \
        /tmp/scgi_temp \
    && chown -R \
        nginx:nginx \
        /srv/media \
        /tmp \
        /usr/share/nginx/html

COPY nginx/nginx.conf \
    /etc/nginx/nginx.conf

COPY --from=build \
    /workspace/frontend/dist \
    /usr/share/nginx/html

USER nginx

EXPOSE 8080

HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD wget \
        --quiet \
        --output-document=- \
        http://127.0.0.1:8080/healthz \
        > /dev/null \
        || exit 1

CMD ["nginx", "-g", "daemon off;"]