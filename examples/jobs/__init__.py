from engine.pipeline_executor import PipelineExecutor

from . import job_1
from . import job_2


def run():
    executor = PipelineExecutor()
    executor.run()
