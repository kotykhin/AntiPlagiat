FROM python:3.9-buster
WORKDIR /usr/src/server
ADD requirements.txt .
# requirements.txtにリストされたパッケージをインストールする
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# FastAPIを8000ポートで待機
CMD ["uvicorn", "endpoints:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]