FROM python:3.10 AS builder
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app
EXPOSE 5050
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "src.app:app"]