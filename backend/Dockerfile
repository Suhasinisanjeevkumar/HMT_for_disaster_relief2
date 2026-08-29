# Repo root becomes /app in the image so the existing relative
# sys.path.insert(...,"..","..","..","src") calls in backend/app/services/
# and the "..","..","data"/"outputs" paths in src/ resolve exactly the
# same way they do outside Docker -- no path-handling code was written
# differently for containerized vs. local use.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY backend/ ./backend/

WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
