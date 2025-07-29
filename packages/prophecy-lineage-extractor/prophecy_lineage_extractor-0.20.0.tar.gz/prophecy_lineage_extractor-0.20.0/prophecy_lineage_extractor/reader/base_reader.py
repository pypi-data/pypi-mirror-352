from datetime import datetime

from prophecy_lineage_extractor.writer import get_writer


class BasePipelineProcessor:
    def __init__(self, project_id, branch, output_dir, send_email, recursive_extract, run_for_all, fmt='excel', pipeline_id_str=None):
        self.project_id = project_id
        pipeline_id_list = []
        for pipeline_id in pipeline_id_str.split(","):
            if pipeline_id.startswith(f"{project_id}/pipelines"):
                pipeline_id_list.append(pipeline_id)
            else:
                pipeline_id_list.append(f"{project_id}/pipelines/{pipeline_id}")
        self.pipeline_id_list = pipeline_id_list
        self.branch = branch
        self.output_dir = output_dir
        self.send_email = send_email
        self.recursive_extract = recursive_extract.lower() == "true"
        self.last_meaningful_message_time = datetime.now()
        self.ws = None
        self.run_for_all = run_for_all.lower() == "true"
        self.writer = get_writer(fmt)(
                project_id=self.project_id,
                pipeline_id_list= self.pipeline_id_list,
                output_dir=self.output_dir,
                run_for_all=self.run_for_all
            )
        self.KEEP_RUNNING = True

    def process(self):
        raise NotImplementedError("process() not defined")