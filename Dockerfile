FROM python:3.12-slim

WORKDIR /app

# Install system dependencies + setuptools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

EXPOSE 8000

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
