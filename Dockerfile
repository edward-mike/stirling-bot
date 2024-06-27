# Set base image with python
FROM python:3.12

# Set Working directory
WORKDIR /BOT

# Copy package required from local req. to Docker image req. file
COPY requirements.txt ./requirements.txt

# Run command line instructions
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all files from local project to Docker image
COPY . .

# Expose Port
EXPOSE 8501

# Command to run StreamLit App
CMD ["streamlit","run", "main.py","--server.port=8501", "--server.address=0.0.0.0","--server.enableCORS=false", "--server.enableXsrfProtection=false"]
