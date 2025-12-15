FROM node:20-bullseye AS assets
WORKDIR /app
COPY package.json package-lock.json* ./ 
COPY static ./static
COPY tailwind.config.js .
RUN npm install && npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY dashboard /app/dashboard
COPY data /app/data
COPY --from=assets /app/static/css/main.css /app/dashboard/static/css/main.css

ENV PORT=5000
CMD ["python", "dashboard/app.py"]
