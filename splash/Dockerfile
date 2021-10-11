FROM scrapinghub/splash

ARG PORT=80
ENV PORT=${PORT}

# ================ FUNCIONA ================
ENTRYPOINT []
# ENTRYPOINT python3 \
#     /app/bin/splash \
#     --proxy-profiles-path /etc/splash/proxy-profiles \
#     --js-profiles-path /etc/splash/js-profiles \
#     --filters-path /etc/splash/filters \
#     --lua-package-path /etc/splash/lua_modules/?.lua \
#     --port $PORT \
#     --disable-private-mode

# ================ CMD TEST ================

# CMD [ \
#     "python3", \
#     "/app/bin/splash", \
#     "--proxy-profiles-path", "/etc/splash/proxy-profiles", \
#     "--js-profiles-path", "/etc/splash/js-profiles", \
#     "--filters-path", "/etc/splash/filters", \
#     "--lua-package-path", "/etc/splash/lua_modules/?.lua", \
#     "--port", "$PORT" \
# ]

CMD python3 /app/bin/splash \
    --proxy-profiles-path /etc/splash/proxy-profiles \
    --js-profiles-path /etc/splash/js-profiles \
    --filters-path /etc/splash/filters  \
    --lua-package-path /etc/splash/lua_modules/?.lua \
    --port $PORT

# Command Example
# docker run -p 80:80 pcts-scrapers-splash
