FROM python:2
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT ["python", "run.py"]
