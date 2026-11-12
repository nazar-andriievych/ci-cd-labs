# Multi-stage Dockerfile
FROM python:3.12-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# venv without its own pip; the base image's pip installs into it
RUN python -m venv --without-pip /opt/venv

COPY requirements.txt .
RUN pip --python /opt/venv/bin/python install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim
# PYTHONDONTWRITEBYTECODE: running pip would otherwise leave ~2.7MB of stdlib .pyc in this layer
RUN PYTHONDONTWRITEBYTECODE=1 pip uninstall -y pip \
 && useradd --create-home --uid 10001 app \
 && mkdir -p /data && chown app:app /data

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY app.py .

USER app
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=2).status==200 else 1)"
CMD ["python", "app.py"]