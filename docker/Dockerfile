FROM python:3.12-slim

LABEL maintainer="Suneel Bose K <https://github.com/bosekarmegam>"
LABEL description="stepcast self-hosted team dashboard (Model B)"

WORKDIR /app

# Install stepcast with dashboard extras
COPY pyproject.toml .
COPY stepcast/ stepcast/
RUN pip install --no-cache-dir ".[dashboard]"

# Expose dashboard port
EXPOSE 4321

# Data directory for SQLite run history
VOLUME ["/data"]

ENV STEPCAST_HOST=0.0.0.0
ENV STEPCAST_PORT=4321
ENV STEPCAST_DB_PATH=/data/runs.db

CMD ["stepcast", "serve", "--host", "0.0.0.0", "--port", "4321", "--no-browser"]
