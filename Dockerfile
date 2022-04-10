FROM python:3.9-buster
WORKDIR /usr/src/server
COPY . .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN pip install git+https://github.com/Desklop/Uk_Stemmer

CMD ["uvicorn", "src.endpoints:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]