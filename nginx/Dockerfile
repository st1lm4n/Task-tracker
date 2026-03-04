FROM nginx:1.25-alpine

# Удаляем дефолтную конфигурацию nginx
RUN rm /etc/nginx/conf.d/default.conf
# Копируем нашу собственную конфигурацию
COPY nginx.conf /etc/nginx/conf.d