from enum import Enum


class TrainingTask(str, Enum):
    Classification = "classification"
    TextGeneration = "text_generation"
