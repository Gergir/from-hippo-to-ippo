FROM python:3.12-alpine
# Install PostgreSQL development libraries and any other dependencies
RUN apk update && \
    apk add --no-cache postgresql-dev gcc musl-dev && \
    apk add --no-cache python3-dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
