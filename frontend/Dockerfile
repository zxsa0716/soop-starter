FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --legacy-peer-deps
COPY . .
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=5 \
    CMD wget -qO- http://localhost:3000 || exit 1
CMD ["npm", "run", "dev"]
