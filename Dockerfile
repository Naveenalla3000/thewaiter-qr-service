FROM python:3.9 AS builder
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app
EXPOSE 5050
CMD ["python", "run.py"]