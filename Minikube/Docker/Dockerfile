# Use python3 as parent image
FROM python:3.5-slim
WORKDIR /app
ADD ./Flask /app
RUN pip install --trusted-host pypi.python.org Flask
CMD ["python", "app.py"]