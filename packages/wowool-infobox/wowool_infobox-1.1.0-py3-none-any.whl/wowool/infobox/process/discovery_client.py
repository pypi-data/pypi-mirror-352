# import requests
# from os import environ
# from json import loads as json_loads
# from wowool.document.analysis.analysis import Analysis

# WOWOOL_NLP_HOST = environ.get("WOWOOL_NLP_HOST", "http://localhost:5000")


# def run_discovery_worker(pipeline_desc: str, text: str):
#     url = f"{WOWOOL_NLP_HOST}/nlp/v1/pipeline/run"
#     data = {
#         "pipeline": pipeline_desc,
#         "documents": [
#             {"data": text, "id": "discovery"},
#         ],
#     }
#     response = requests.post(url, json=data)
#     jo = json_loads(response.text)
#     doc = Analysis.parse(jo["documents"][0]["apps"]["wowool_analysis"]["results"])
#     return doc
