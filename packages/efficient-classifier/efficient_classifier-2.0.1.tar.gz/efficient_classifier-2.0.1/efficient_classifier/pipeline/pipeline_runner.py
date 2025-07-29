"""

This file runs the pipeline code. Its the full automation of all the pipelines' code

"""

import logging
import time
import os

from efficient_classifier.pipeline.pipeline import Pipeline
from efficient_classifier.pipeline.pipeline_manager import PipelineManager

# Runners
from efficient_classifier.phases.runners.dataset_runner import DatasetRunner
from efficient_classifier.phases.runners.featureAnalysis_runner import FeatureAnalysisRunner
from efficient_classifier.phases.runners.dataPreprocessing_runner import DataPreprocessingRunner
from efficient_classifier.phases.runners.modelling.modelling_runner import ModellingRunner

# Utils
from efficient_classifier.utils.decorators.timer import timer
from efficient_classifier.phases.phases_implementation.dev_ops.slackBot.bot import SlackBot
from efficient_classifier.utils.miscellaneous.dag import DAG


class PipelineRunner:
      def __init__(self, 
                   dataset_path: str, 
                   model_task: str,
                   pipelines_names: dict[str, list[str]],
                   include_plots: bool = True,
                   variables: dict = None
                   ) -> None:
            self.dataset_path = dataset_path
            self.model_task = model_task
            self.variables = variables
            self.phases = ["dataset", "data_preprocessing", "feature_analysis", "modelling"]
            self._set_up_folders()
            self._set_up_pipelines(pipelines_names)
            self._set_up_logger()

            self.phase_runners = {
                  "dataset": DatasetRunner(self.pipeline_manager,
                                            include_plots=include_plots,
                                            save_path=self.plots_path + "dataset/"),
                  "data_preprocessing": DataPreprocessingRunner(self.pipeline_manager,
                                                            include_plots=include_plots,
                                                            save_path=self.plots_path + "data_preprocessing/"),
                  "feature_analysis": FeatureAnalysisRunner(self.pipeline_manager,
                                                            include_plots=include_plots,
                                                            save_path=self.plots_path + "feature_analysis/"),
                  "modelling": ModellingRunner(self.pipeline_manager,
                                                include_plots=include_plots,
                                                save_path=self.plots_path + "modelling/",
                                               )  
            }
            if self.variables["bot"]["include_bot"]:
                  self.slack_bot = SlackBot()

      def _set_up_folders(self) -> None:
            """
            Set ups the folders for the pipeline runner.

            Parameters
            ----------
            None

            Returns
            -------
            None
            """
            if not os.path.exists("results/model_evaluation/"):
                  os.makedirs("results/model_evaluation/", exist_ok=True)
            self.model_results_path = "results/model_evaluation/results.csv"

            if not os.path.exists("results/plots/"):
                  os.makedirs("results/plots/", exist_ok=True)
            self.plots_path = "results/plots/"

            if not os.path.exists("results/logs/"):
                  os.makedirs("results/logs/", exist_ok=True)
            self.logs_path = "results/logs/"
      
      def _clean_dataset_set_up_dataset_specific(self, default_pipeline: Pipeline) -> None:
            """
            Set ups the dataset specific set-up.
            """
            # default_pipeline.dataset.df.drop(columns=["Family", "Hash"], inplace=True) # We have decided to use only category as target variable; Hash is temporary while im debugging (it will be deleted in EDA)
            # default_pipeline.dataset.df.drop(default_pipeline.dataset.df[default_pipeline.dataset.df["Category"] == "Zero_Day"].index, inplace=True)
            # default_pipeline.dataset.df.drop(default_pipeline.dataset.df[default_pipeline.dataset.df["Category"] == "No_Category"].index, inplace=True)
            # default_pipeline.dataset.df.drop(default_pipeline.dataset.df[default_pipeline.dataset.df["Category"] == "Adware"].index, inplace=True)
            # default_pipeline.dataset.df.drop(default_pipeline.dataset.df[default_pipeline.dataset.df["Category"] == "Trojan"].index, inplace=True)
            default_pipeline.dataset.df.drop(columns=["Id"], inplace=True)
            

      def _dag_set_up(self):
            dag_pipelines = {}
            for category in self.variables["general"]["pipelines_names"]:
                  for pipeline in self.variables["general"]["pipelines_names"][category]:
                        if pipeline == "stacking":
                              continue
                        print(f"Pipeline name is: {pipeline}")
                        dag_pipelines[pipeline] = {model for model in self.variables["phase_runners"]["modelling_runner"]["models_to_include"][category][pipeline]}
            
            phases = [phase for phase in self.phases]
            return DAG(dag_pipelines, phases)
      
      def _set_up_pipelines(self, pipelines_names: dict[str, list[str]]) -> None:
            """
            Set ups the pipelines and initializes the pipeline manager. Also does general pipeline-wide set-up.
            Originally all pipelines are the same, then we start diverging them as we consider. 

            Parameters
            ----------
            pipelines_names: dict[str, list[str]]
                  The names of the pipelines to run. Key is the name of the category, value is the list of all the pipeleines names in that category.

            Returns
            -------
            None
            """
            print(f"Setting up pipelines for {self.model_task} model task")
            combined_pipelines = {}
            default_pipeline = Pipeline(self.dataset_path, self.model_results_path, self.model_task)            
            #self._clean_dataset_set_up_dataset_specific(default_pipeline)

            for category_name, pipelines in pipelines_names.items():
                  combined_pipelines[category_name] = {}
                  for pipeline_name in pipelines:
                        combined_pipelines[category_name][pipeline_name] = default_pipeline

            dag = self._dag_set_up()
            self.pipeline_manager = PipelineManager(combined_pipelines, dag=dag, variables=self.variables)

      
      def _set_up_logger(self) -> None:
            """
            Set ups the logger for the pipeline runner.

            Xarameters
            ----------
            None

            Returns
            -------
            None
            """
            log_file = self.logs_path + "pipeline_runner.log"
            logger = logging.getLogger("my_logger")
            logger.setLevel(logging.INFO)

            file_handler = logging.FileHandler(log_file, mode="w") # At each run the logger is overwritten
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"Pipeline runner started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger = logger


      def run(self):
                  """
                  All the runners have a .run method. We execute them sequentially for each of the phase runners in phase_runners dictionary. 
                  We then also send a message to the slack channel with the results and write to the log file.

                  Parameters
                  ----------
                  None

                  Returns
                  -------
                  None
                  """
                  error_occured = False
                  for phase_name, phase_runner in self.phase_runners.items():
                        @timer(phase_name)
                        def run_phase():
                              try:
                                    start_time = time.time()
                                    phase_result = phase_runner.run()
                                    #self.logger.info(f"Phase '{phase_name}' completed in {time.time() - start_time} seconds at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                                    if phase_result is not None:
                                          self.logger.info(f"'{phase_name}' returned: {phase_result}")
                                          if self.variables["bot"]["include_bot"]:
                                                time.sleep(1) # This is to avoid sending too many messages to the slack channel at once 
                                                self.slack_bot.send_message(f"Phase '{phase_name}' completed in {time.time() - start_time} seconds at {time.strftime('%Y-%m-%d %H:%M:%S')}\
                                                                        Result: {str(phase_result)}",
                                                                        channel=self.variables["bot"]["channel"])
                              except Exception as e:
                                    self.logger.error(f"Error running phase '{phase_name}': {e}")
                                    print(f"ERROR RUNNING PHASE '{phase_name}': {e}")
                                    if self.variables["bot"]["include_bot"]:
                                          self.slack_bot.send_message(f"🚨 Error running phase '{phase_name}': {e}",
                                                                  channel=self.variables["bot"]["channel"])
                                    raise e

                        run_phase()
                  print("-"*30)
                  print("PIPELINE COMPLETED SUCCESSFULLY")
                  print("-"*30)

                  # Store DAG
                  self.pipeline_manager.dag.render()
                  if self.variables["bot"]["send_images"] and self.variables["bot"]["include_bot"]:
                        self.slack_bot_send_images()

      def slack_bot_send_images(self):
            try:
                  #Send slack bot all the images in the results/plots folder
                  for root, dirs, files in os.walk(self.plots_path):
                        for file in files:
                              file_path = os.path.join(root, file)
                              time.sleep(1) # This is to avoid sending too many messages to the slack channel at once 
                              self.slack_bot.send_file(file_path,
                                                            channel=self.variables["bot"]["channel"],
                                                            title=file,
                                                            initial_comment="")
                  # Send slack bot the results progress
                  self.slack_bot.send_file(self.model_results_path,
                                                            channel=self.variables["bot"]["channel"],
                                                            title=self.model_results_path,
                                                            initial_comment="Here is the results progress log")
            except Exception as e:
                  self.logger.error(f"Error sending slack bot the results progress: {e}")
                  self.slack_bot.send_message(f"🚨 Error sending slack bot the results progress: {e}",
                                                            channel=self.variables["bot"]["channel"])



