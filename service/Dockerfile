# No install step, so the image builds and runs with no network at all.
FROM node:24-alpine
WORKDIR /app
COPY . .
ENV PORT=3000 NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=5s --timeout=3s --start-period=2s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "server.js"]
