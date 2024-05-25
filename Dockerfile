FROM python:3.8-slim

RUN apt-get update

COPY ./ app

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN python3 -m pip install --trusted-host pypi.python.org -r /app/requirements.txt

WORKDIR /app
EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]