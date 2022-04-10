FROM python:3.9-buster
WORKDIR /usr/src/server
ADD requirements.txt .

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["uvicorn", "endpoints:app", "--reload", "--host", "0.0.0.0", "--port", "80"]