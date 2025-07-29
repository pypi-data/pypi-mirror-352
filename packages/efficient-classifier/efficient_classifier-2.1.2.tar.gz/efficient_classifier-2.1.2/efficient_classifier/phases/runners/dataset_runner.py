import numpy as np

from efficient_classifier.utils.phase_runner_definition.phase_runner import PhaseRunner
from efficient_classifier.pipeline.pipeline_manager import PipelineManager

class DatasetRunner(PhaseRunner):
      def __init__(self, pipeline_manager: PipelineManager, include_plots: bool = False, save_path: str = "") -> None:
            super().__init__(pipeline_manager, include_plots, save_path)


      def _update_dag_scheme(self, split_shapes):
            for category in self.pipeline_manager.pipelines:
                  for pipeline in self.pipeline_manager.pipelines[category]:
                        if pipeline == "stacking":
                              continue
                        self.pipeline_manager.dag.add_procedure(pipeline, "dataset", "split", split_shapes)

      def run(self) -> None:
            # Select the first pipeline.
            pipelines = list(self.pipeline_manager.pipelines["not_baseline"].values())
            default_pipeline = pipelines[0]

            split_df = default_pipeline.dataset.split.asses_split_classifier(
                        p=self.pipeline_manager.variables["phase_runners"]["dataset_runner"]["split_df"]["p"], 
                        step=self.pipeline_manager.variables["phase_runners"]["dataset_runner"]["split_df"]["step"],
                        save_plots=self.include_plots,
                        save_path=self.save_path
                        )

            split_shapes = default_pipeline.dataset.split.split_data(
                        y_column=self.pipeline_manager.variables["phase_runners"]["dataset_runner"]["encoding"]["y_column"],
                        train_size=self.pipeline_manager.variables["phase_runners"]["dataset_runner"]["encoding"]["train_size"],
                        validation_size=self.pipeline_manager.variables["phase_runners"]["dataset_runner"]["encoding"]["validation_size"],
                        test_size=self.pipeline_manager.variables["phase_runners"]["dataset_runner"]["encoding"]["test_size"],
                        max_plots=self.pipeline_manager.variables["general"]["max_plots_per_function"],
                        save_plots=True, 
                        save_path=self.save_path
                  )
            
            self._update_dag_scheme(split_shapes)
            return split_shapes

