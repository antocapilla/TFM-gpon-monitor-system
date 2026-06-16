# ---- Build stage ----
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

# URL del backend, inyectada en el bundle en tiempo de build.
# Railway/Render pasan las variables del servicio como build args.
ARG REACT_APP_API_BASE_URL
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

COPY . .
RUN npm run build

# ---- Runtime stage ----
FROM node:18-alpine

WORKDIR /app
RUN npm install -g serve

COPY --from=build /app/build ./build

# Sirve el build estático en el puerto que asigne la plataforma ($PORT) o 3000.
ENV PORT=3000
CMD ["sh", "-c", "serve -s build -l ${PORT:-3000}"]
