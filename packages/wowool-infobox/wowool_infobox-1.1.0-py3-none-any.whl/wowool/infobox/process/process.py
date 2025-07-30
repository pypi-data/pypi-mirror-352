from wowool.native.core.pipeline import Pipeline
from multiprocessing import Process, Manager
from json import dumps as json_dumps
from json import loads as json_loads
from wowool.document.analysis.analysis import Analysis

pipelines = {}


def discovery(pipeline_desc: str, text: str):
    if pipeline_desc not in pipelines:
        pipelines[pipeline_desc] = Pipeline(pipeline_desc)
    return pipelines[pipeline_desc](text)


manager = Manager()
process_input_queue = manager.Queue()
process_output_queue = manager.Queue()
sub_process_started = manager.Value("b", False)
ib_sub_process = None


class NoDaemonProcess(Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


def discovery_worker(input_queue, output_queue):
    while True:
        pipeline_desc, text = input_queue.get()
        if pipeline_desc == "exit":
            return
        doc = discovery(pipeline_desc, text)
        output_queue.put(json_dumps(doc.to_json()))


def run_discovery_worker(pipeline_desc: str, text: str):
    global ib_sub_process

    if not sub_process_started.value:
        ib_sub_process = NoDaemonProcess(target=discovery_worker, args=(process_input_queue, process_output_queue))
        ib_sub_process.start()
        sub_process_started.value = True

    process_input_queue.put((pipeline_desc, text))
    json_str = process_output_queue.get()
    jo = json_loads(json_str)
    doc = Analysis.parse(jo["apps"]["wowool_analysis"]["results"])
    return doc


def stop_discovery_process():

    if ib_sub_process is not None and sub_process_started.value:
        process_input_queue.put(("exit", ""))
        ib_sub_process.join()
        sub_process_started.value = False
        while not process_input_queue.empty():
            process_input_queue.get()
        while not process_output_queue.empty():
            process_output_queue.get()


# def run_document(pipeline_desc: str, text: str):
#     pipeline = Pipeline(pipeline_desc)
#     return pipeline(text)


# # must be a global function
# def mt_process(q, pipeline_desc: str, text: str):
#     doc = run_document(pipeline_desc, text)
#     q.put(json_dumps(doc.to_json()))


# def process(pipeline_desc: str, text: str):
#     doc = run_document(pipeline_desc, text)
#     # queue = Queue()
#     # p = Process(target=mt_process, args=(queue, pipeline_desc, text))
#     # p.start()
#     # p.join()  # this blocks until the process terminates
#     # json_str = queue.get()
#     # jo = json_loads(json_str)
#     # doc = Analysis.parse(jo["apps"]["wowool_analysis"]["results"])

#     return doc
