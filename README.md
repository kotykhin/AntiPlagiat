# AntiPlagiat

## For this project you need to setup Elasticsearch
Check out [Elasticsearch setup](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) \
The cluster name and node name doesn't matter. Just choose port 9200(default one)\

## All needed python packages can be found in requirements.txt

## User guide
run eclipse as administrator \

run endpoints.py file \
or run in powershell:
```
uvicorn endpoints:app --reload
```

You are ready to use api. To check endpoints go http://127.0.0.1:8000/docs
