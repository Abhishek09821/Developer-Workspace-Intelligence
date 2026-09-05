# syntax=docker/dockerfile:1
FROM node:20-alpine AS base

WORKDIR /app/apps/web

# Copy manifests first for layer caching — lock file may not exist yet
COPY apps/web/package.json ./
COPY apps/web/package-lock.json* ./

RUN npm install

# Copy source
COPY apps/web ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
