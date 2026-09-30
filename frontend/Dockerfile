FROM node:22.23.3-alpine AS dev

RUN corepack enable && corepack prepare pnpm@10.18.2 --activate
WORKDIR /app
ENV NUXT_TELEMETRY_DISABLED=1 \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    HOST=0.0.0.0 \
    PORT=3000

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --ignore-scripts \
    && pnpm rebuild esbuild unrs-resolver
COPY . .
RUN pnpm exec nuxt prepare
EXPOSE 3000
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]

FROM dev AS build

RUN pnpm build

FROM node:22.23.3-alpine AS runtime

WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOST=0.0.0.0 \
    NUXT_TELEMETRY_DISABLED=1
COPY --from=build /app/.output ./.output
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD wget -qO- http://127.0.0.1:3000/ >/dev/null || exit 1
CMD ["node", ".output/server/index.mjs"]
