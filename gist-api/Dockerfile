FROM python:3.12-slim

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs appear immediately in Docker logs
ENV PYTHONUNBUFFERED=1

# Running as app inside containers for security reasons
RUN addgroup --system app && adduser --system --ingroup app app

# Working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# chown ensures the app user owns the files
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Expose application port
EXPOSE 8080

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]