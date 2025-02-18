FROM python:3.10 AS builder
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app
EXPOSE 5050

# Verify if run.py exists
RUN ls -la /app

ENTRYPOINT [ "python", "run.py" ]
