import os
from torch.utils.data import Dataset
import torch

from pnpl.datasets import LibriBrainSpeech
from pnpl.datasets.libribrain2025.constants import PHONEME_CLASSES, SPEECH_CLASSES, PHONEME_HOLDOUT_PREDICTIONS, SPEECH_HOLDOUT_PREDICTIONS
import csv
import torch
import warnings
from torch.utils.data import DataLoader
from pnpl.datasets.libribrain2025.speech_dataset_holdout import LibriBrainSpeechHoldout
from tqdm import tqdm
import pandas as pd
import numpy as np

class LibriBrainCompetitionHoldout(Dataset):
    def __init__(self, data_path,
                 tmin: float = 0.0,
                 tmax: float = 0.8,
                 standardize=True,
                 clipping_boundary=10,
                 stride=1,
                 task: str = "speech"):
        # Path to the data
        self.data_path = data_path
        self.task = task
        self.dataset = None
        if task == "speech":
            try:
                self.dataset = LibriBrainSpeechHoldout(
                    data_path=self.data_path,
                    tmin = tmin,
                    tmax = tmax,
                    include_run_keys=[("0", "2025", "COMPETITION_HOLDOUT", "1")],
                    standardize=standardize,
                    clipping_boundary=clipping_boundary,
                    # preprocessing_str=None,
                    preprocessing_str="bads+headpos+sss+notch+bp+ds",
                    preload_files=False,
                    include_info=True,
                    # Important parameter - stride is 100 to get us 2087 samples for the holdout
                    stride=stride
                )
                self.samples = self.dataset.samples
            except Exception as e:
                warnings.warn(f"Failed to load speech dataset: {e}")
                raise RuntimeError("Failed to load speech dataset. Check the data path and parameters.")
        if task == "phoneme":
            raise NotImplementedError(f"Task '{task}' is not supported yet.")


    def generate_submission_in_csv(self, predictions, output_path: str):
        """
        Generates a submission file in CSV format for the LibriBrain competition.
        The file contains the run keys and the corresponding labels.
        Args:
            predictions (List[Tensor]): List of scalar tensors, each representing a speech probability.
            output_path (str): Path to save the CSV file.
        """
        if self.task == "speech":
            if len(predictions) != SPEECH_HOLDOUT_PREDICTIONS:
                raise (ValueError(
                    "Length of speech predictions does not match number of segments."))
            if predictions[0].shape[0] != SPEECH_CLASSES:
                raise (ValueError(
                    "Speech classes does not match expect size (1)."))

            with open(output_path, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["idx", "speech_prob"])

                for idx, tensor in enumerate(predictions):
                    # Ensure we extract the scalar float from tensor
                    speech_prob = tensor.item() if isinstance(
                        tensor, torch.Tensor) else float(tensor)
                    writer.writerow([idx, speech_prob])


    def speech_labels(self):
        return self.dataset.speech_labels if self.task == "speech" else None

    def __len__(self):
        return len(self.dataset.samples)

    def __getitem__(self, idx):
        # returns channels x time
        return self.dataset[idx]


if __name__ == "__main__":
    output_path = ""

    dataset = LibriBrainCompetitionHoldout(
        data_path = "/Users/gilad/Desktop/Projects/PNPL/LibriBrain/serialized",
        tmax=0.8,
        task="speech")

    # Create a DataLoader for the dataset
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
    segments_to_predict = len(dataset)

    random_predictions = []
    for i, sample in enumerate(tqdm(dataloader)):
        segment = sample[0]
#        prediction = model.predict(segment)  # Assuming model is defined and has a predict method
        random_predictions.append(torch.rand(1))  # Random prediction for each sample
    dataset.generate_submission_in_csv(random_predictions, "holdout_speech_predictions.csv")