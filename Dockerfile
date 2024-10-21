ARG NODE_VERSION=22
FROM node:${NODE_VERSION}-alpine AS base
WORKDIR /app
ENV NODE_ENV="production"
FROM base AS build
RUN apk -U add build-base gyp pkgconfig python3
COPY --link package-lock.json package.json ./
RUN npm ci --include=dev
RUN npm install --production
COPY --link . .
RUN npm run build
RUN npm prune --omit=dev
FROM base AS run
COPY --from=build /app /usr/src/app
EXPOSE 3000
CMD [ "npm", "run", "start" ]





# Copy built app


# Run the app
