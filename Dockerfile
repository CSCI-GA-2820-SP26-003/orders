##################################################
# Create production image
##################################################
FROM quay.io/rofrano/python:3.12-slim

# Set up the Python production environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --deploy

# Copy the application contents
COPY wsgi.py .
COPY service ./service

# Expose any ports the app is expecting in the environment
ENV FLASK_APP="wsgi:app"
ENV PORT=8080
EXPOSE $PORT

ENV GUNICORN_BIND=0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "wsgi:app"]