from engine import PipelineExecutor

import job_1, job_2


if __name__ == "__main__":
    executor = PipelineExecutor()
    executor.run()
