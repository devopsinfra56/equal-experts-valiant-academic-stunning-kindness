# Based on the official Python image, which includes a slimmed-down version of Debian with Python installed. This provides a lightweight and secure base for our application.
FROM python:3.12-slim

# Prevent Python from generating .pyc files, which are unnecessary in a containerized environment and can take up extra space. 
#These files are not needed since the application will be run in a read-only filesystem and we want to minimize the number of files generated at runtime.
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs appear immediately in Docker logs
ENV PYTHONUNBUFFERED=1

# Running as app inside containers for security reasons
RUN addgroup --system app && adduser --system --ingroup app app

# Working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .

# --no-cache-dir ensures that pip does not store the downloaded packages in the cache, which helps to reduce the size of the final image. 
# This is important in a containerized environment where we want to keep the image as small as possible for faster deployment and reduced attack surface.
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