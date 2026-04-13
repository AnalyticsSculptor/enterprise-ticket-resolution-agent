# 1. Use an official, lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the requirements first (to cache the installation step)
COPY requirements.txt .

# 4. Install the enterprise dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your code and the ChromaDB folder into the container
COPY . .

# 6. Expose the port the app runs on
EXPOSE 8000

# 7. Start the FastAPI server using the dynamic Cloud Port
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}