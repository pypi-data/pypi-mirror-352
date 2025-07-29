

from efficient_classifier.pipeline.pipeline import Pipeline
from efficient_classifier.phases.phases_implementation.modelling.shallow.model_definition.model_base import Model

from efficient_classifier.utils.decorators.timer import timer

import joblib
import pickle
import os

from abc import ABC, abstractmethod
import time

class Serialization:
      """ This class is responsible for serializing the pipelines and models. """
      def __init__(self):
            pass
      if not os.path.exists("results/serialization"):
            os.makedirs("results/serialization")
            os.makedirs("results/serialization/models")
            os.makedirs("results/serialization/pipelines")
      
      @timer("Serializing pipelines")
      def serialize_pipelines(self, all_pipelines: dict[str, dict[str, Pipeline]], pipelines_to_serialize: list[str]):
            for category in all_pipelines:
                  for pipeline_name in all_pipelines[category]:
                        if pipeline_name in pipelines_to_serialize:
                              self._serialize_pipeline(all_pipelines[category][pipeline_name], pipeline_name)

      @abstractmethod
      def _serialize_pipeline(self, pipeline: Pipeline, pipeline_name: str):
            pass
      
      @timer("Serializing models")
      def serialize_models(self, all_models: dict[str, Model], models_to_serialize: list[str]):
            for model_name in all_models:
                  if model_name in models_to_serialize:
                        self._serialize_model(all_models[model_name], model_name)

      @abstractmethod
      def _serialize_model(self, model: Model, model_name: str):
            pass


class SerializationJoblib(Serialization):
      def __init__(self):
            super().__init__()
      
      def _serialize_pipeline(self, pipeline: Pipeline, pipeline_name: str):
            assert isinstance(pipeline, Pipeline), "Pipeline must be an instance of Pipeline"
            joblib.dump(pipeline, f"results/serialization/pipelines/{pipeline_name}_{time.time()}.joblib")
      
      def _serialize_model(self, model: Model, model_name: str):
            assert isinstance(model, Model), "Model must be an instance of Model"
            print(f"Model is {model}")

            joblib.dump(model, f"results/serialization/models/{model_name}_{time.time()}.joblib")
      

class SerializationPickle(Serialization):
      def __init__(self):
            super().__init__()
      
      def _serialize_pipeline(self, pipeline: Pipeline, pipeline_name: str):
            assert isinstance(pipeline, Pipeline), "Pipeline must be an instance of Pipeline"
            pickle.dump(pipeline, open(f"results/pipelines/{pipeline_name}_{time.time()}.pkl", "wb"))
      
      def _serialize_model(self, model: Model, model_name: str):
            assert isinstance(model, Model), "Model must be an instance of Model"
            pickle.dump(model, open(f"results/models/{model_name}_{time.time()}.pkl", "wb"))
      
