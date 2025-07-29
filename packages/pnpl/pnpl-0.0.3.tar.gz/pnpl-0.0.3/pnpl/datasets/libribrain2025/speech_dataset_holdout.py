import os
import warnings
import numpy as np
import pandas as pd
import torch
from pnpl.datasets.libribrain2025.base import LibriBrainBase
from pnpl.datasets.libribrain2025.constants import PHONEME_CLASSES, SPEECH_CLASSES, PHONEME_HOLDOUT_PREDICTIONS, SPEECH_HOLDOUT_PREDICTIONS


class LibriBrainSpeechHoldout(LibriBrainBase):

    def __init__(
        self,
        data_path: str,
        partition: str | None = None,
        preprocessing_str: str | None = "bads+headpos+sss+notch+bp+ds",
        tmin: float = 0.0,
        tmax: float = 0.5,
        include_run_keys: list[str] = [],
        exclude_run_keys: list[str] = [],
        exclude_tasks: list[str] = [],
        standardize: bool = True,
        clipping_boundary: float | None = 10,
        channel_means: np.ndarray | None = None,
        channel_stds: np.ndarray | None = None,
        include_info: bool = False,
        oversample_silence_jitter: int = 0,
        preload_files: bool = False,
        stride=None
    ):
        """
        data_path: path to serialized dataset. 
        preprocessing_str: Preprocessing string in the file name. Indicates Preprocessing steps applied to the data.
        tmin: start time of the sample in seconds in reference to the onset of the phoneme.
        tmax: end time of the sample in seconds in reference to the onset of the phoneme.
        standardize: Whether to standardize the data. Uses channel_means and channel_stds if provided. Otherwise it calculates mean and std for each channel of the dataset. 
        clipping_boundary: Min and max values to clip the data by.
        channel_means: Standardize using these channel means.
        channel_stds: Standardize using these channel stds.
        include_info: Whether to include info dict in the output. Info dict contains dataset name, subject, session, task, run, onset time of the sample, and full phoneme label that indicates if a phoneme is at the onset or offset of a word.
        oversample_silence_jitter: Over sample silence by this factor.
        preload_files: If true start parallel downloads of all sessions and runs into data_path. Otherwise it will download files as they are needed.

        returns Channels x Time
        """
        super().__init__(
            data_path=data_path,
            partition=partition,
            preprocessing_str=preprocessing_str,
            tmin=tmin,
            tmax=tmax,
            include_run_keys=include_run_keys,
            exclude_run_keys=exclude_run_keys,
            exclude_tasks=exclude_tasks,
            standardize=standardize,
            clipping_boundary=clipping_boundary,
            channel_means=channel_means,
            channel_stds=channel_stds,
            include_info=include_info,
            preload_files=preload_files,
        )

        if not os.path.exists(data_path):
            raise ValueError(f"Path {data_path} does not exist.")
        self.oversample_silence_jitter = oversample_silence_jitter

        self.stride = stride
        self.samples = []
        run_keys_missing = []
        self.run_keys = []
        for run_key in self.intended_run_keys:
            try:
                subject, session, task, run = run_key
                self._collect_speech_samples(
                    subject, session, task, run, SPEECH_HOLDOUT_PREDICTIONS, stride=self.stride)
                self.run_keys.append(run_key)
            except FileNotFoundError:
                run_keys_missing.append(run_key)
                warnings.warn(
                    f"File not found for run key {run_key}. Skipping")
                continue

        if len(run_keys_missing) > 0:
            warnings.warn(
                f"Run keys {run_keys_missing} not found in dataset. Present run keys: {self.run_keys}")

        if len(self.samples) == 0:
            raise ValueError("No samples found.")

        if (self.standardize and channel_means is None and channel_stds is None):
            self._calculate_standardization_params()
        elif (self.standardize and (channel_means is not None and channel_stds is not None)):
            self.channel_means = channel_means
            self.channel_stds = channel_stds
            self.broadcasted_stds = np.tile(
                self.channel_stds, (self.points_per_sample, 1)).T
            self.broadcasted_means = np.tile(
                self.channel_means, (self.points_per_sample, 1)).T


    def _collect_speech_samples(self, subject, session, task, run, speech_segments, stride = None):
        # Calculate the number of samples in the time window
        time_window_samples = int((self.tmax - self.tmin) * self.sfreq)

        if stride is None:
            stride = time_window_samples

        for i in range(0, speech_segments, stride):
            self.samples.append(
                (subject, session, task, run, i / self.sfreq, []))


    def __getitem__(self, idx):
        # returns channels x time
        data, _, info = super().__getitem__(idx)
        if self.include_info:
            return [data, info]
        return data
