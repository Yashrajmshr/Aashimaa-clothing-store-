FROM node:24-alpine AS static_build

WORKDIR /workspace
COPY scripts/build-frontend.mjs /workspace/scripts/build-frontend.mjs

COPY apps/customer-web/index.html /workspace/apps/customer-web/index.html
COPY apps/customer-web/src /workspace/apps/customer-web/src
COPY apps/customer-web/public /workspace/apps/customer-web/public
COPY apps/admin-web/index.html /workspace/apps/admin-web/index.html
COPY apps/admin-web/src /workspace/apps/admin-web/src
COPY apps/admin-web/public /workspace/apps/admin-web/public
COPY apps/mobile/index.html /workspace/apps/mobile/index.html
COPY apps/mobile/src /workspace/apps/mobile/src

RUN node scripts/build-frontend.mjs customer-web \
    && node scripts/build-frontend.mjs admin-web \
    && node scripts/build-frontend.mjs mobile

FROM nginx:alpine

COPY --from=static_build /workspace/apps/customer-web/dist/ /usr/share/nginx/html/customer/
COPY --from=static_build /workspace/apps/admin-web/dist/ /usr/share/nginx/html/admin/
COPY --from=static_build /workspace/apps/mobile/dist/ /usr/share/nginx/html/mobile/
COPY infrastructure/nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
