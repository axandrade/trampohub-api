# Estágio 1: build e testes
FROM python:3.14-slim AS builder

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

RUN pytest

# Estágio 2: imagem final, só produção
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]