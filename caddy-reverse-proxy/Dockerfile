FROM caddy:2.4.6-builder-windowsservercore-1809 AS builder

RUN ./xcaddy.exe build \
    --with github.com/lucaslorentz/caddy-docker-proxy/plugin

FROM caddy:2.4.6-windowsservercore-1809

COPY --from=builder c:/caddy.exe c:/caddy.exe

CMD ["caddy", "docker-proxy"]