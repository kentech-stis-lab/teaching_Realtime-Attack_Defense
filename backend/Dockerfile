FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    iputils-ping \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir paramiko mysql-connector-python

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN find /app -name "*.sh" -exec dos2unix {} \;

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
