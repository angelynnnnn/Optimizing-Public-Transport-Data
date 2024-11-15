# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Define the default command to run your main application
CMD ["streamlit", "run", "simulation.py", "--server.port=8501", "--server.address=0.0.0.0"]
