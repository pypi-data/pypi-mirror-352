from wowool.sdk import Pipeline

pipelines = {}


def discovery(pipeline_desc: str, text: str):
    if pipeline_desc not in pipelines:
        pipelines[pipeline_desc] = Pipeline(pipeline_desc)
    return pipelines[pipeline_desc](text)


def run_discovery_worker(pipeline_desc: str, text: str):
    return discovery(pipeline_desc, text)
