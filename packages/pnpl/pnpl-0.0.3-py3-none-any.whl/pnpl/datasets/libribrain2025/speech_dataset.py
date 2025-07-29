import os
import warnings
import numpy as np
import pandas as pd
import torch
from pnpl.datasets.libribrain2025.base import LibriBrainBase


class LibriBrainSpeech(LibriBrainBase):

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
                self.speech_labels = self.get_speech_silence_labels_for_session(
                    subject, session, task, run)
                if self.oversample_silence_jitter > 0:
                    self._collect_speech_over_samples(
                        subject, session, task, run, self.speech_labels, self.oversample_silence_jitter)
                else:
                    self._collect_speech_samples(
                        subject, session, task, run, self.speech_labels, stride=self.stride)
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

    def get_speech_silence_labels_for_session(self, subject, session, task, run):
        df = self._load_events(subject, session, task, run)

        # Convert times to samples, handling errors
        df['timemeg_samples'] = (pd.to_numeric(
            df['timemeg'], errors='coerce') * self.sfreq).astype(int)
        df['duration_samples'] = (pd.to_numeric(
            df['duration'], errors='coerce') * self.sfreq).astype(int)

        # Filter for silence entries
        silence_df = df[df['kind'] == 'silence']

        if silence_df.empty or silence_df['timemeg_samples'].isnull().all() or silence_df['duration_samples'].isnull().all():
            print("Warning: No valid silence entries found. Returning None.")
            return None

        words_df = df[df['kind'] == 'word']

        max_word_sample_time = (words_df['timemeg_samples'] +
                      words_df['duration_samples']).max()

        max_silence_sample_time = (silence_df['timemeg_samples'] +
                      silence_df['duration_samples']).max()

        # Create the array, initialize with 1s (assuming everything is speech initially)
        speech_labels = np.ones(max(max_word_sample_time,max_silence_sample_time) + 1, dtype=int)

        # Fill in 0s for silence spans
        for index, row in silence_df.iterrows():
            start_sample = row['timemeg_samples']
            duration_samples = row['duration_samples']
            if not np.isnan(start_sample) and not np.isnan(duration_samples):
                end_sample = start_sample + duration_samples
                speech_labels[start_sample:end_sample] = 0

        return speech_labels

    def _collect_speech_samples(self, subject, session, task, run, speech_labels, stride = None):
        # Calculate the number of samples in the time window
        time_window_samples = int((self.tmax - self.tmin) * self.sfreq)

        if stride is None:
            stride = time_window_samples

        for i in range(0, len(speech_labels), stride):
            sample_labels = speech_labels[i:i+time_window_samples]
            if len(sample_labels) < time_window_samples:
                continue
            self.samples.append(
                (subject, session, task, run, i / self.sfreq, sample_labels))

    def _collect_speech_over_samples(self, subject, session, task, run, speech_labels, silence_jitter=7, over_sample_category=1):
        # Calculate the number of samples in the time window
        time_window_samples = int((self.tmax - self.tmin) * self.sfreq)

        # first collect the normal samples
        for i in range(0, len(speech_labels), time_window_samples):
            sample_labels = speech_labels[i:i+time_window_samples]
            if len(sample_labels) < time_window_samples:
                continue
            self.samples.append(
                (subject, session, task, run, i / self.sfreq, sample_labels))

        # now collect the over samples
        samples_step_size = time_window_samples
        i = 0
        self.segments_with_speech_counter = 0
        jitter_around_silence = False
        # Make sure to jitter around silence whenever a silence is found in the samples iteration
        while i < len(speech_labels):
            speech_label_segment = speech_labels[i:i + time_window_samples]
            # found rare silence, iterate sample at a time to oversample silence
            if speech_label_segment.sum() < time_window_samples and jitter_around_silence == False:
                jitter_around_silence = True
                first_zero_index = np.argmax(speech_label_segment == 0)
                i = i - ((time_window_samples - first_zero_index) - 1)
                samples_step_size = silence_jitter
            # back to no silence, so let's go back to 200 sampling rate step size
            if speech_label_segment.sum() == time_window_samples and jitter_around_silence == True:
                samples_step_size = time_window_samples
                jitter_around_silence = False

            sample_labels = speech_labels[i:i+time_window_samples]
            if len(sample_labels) < time_window_samples:
                break
            i += samples_step_size

            if over_sample_category == 1:
                if 0.3 < sample_labels.sum() / sample_labels.shape[0] < 0.5:
                    self.samples.append(
                        (subject, session, task, run, i / self.sfreq, sample_labels))
                if sample_labels.sum() == 0:
                    self.samples.append(
                        (subject, session, task, run, i / self.sfreq, sample_labels))

    def __getitem__(self, idx):
        # returns channels x time
        data, label, info = super().__getitem__(idx)
        if self.include_info:
            return [data, torch.tensor(label), info]
        return [data, torch.tensor(label)]


if __name__ == "__main__":
    import time

    start_time = time.time()
    dataset = LibriBrainSpeech(
        data_path="/Users/mirgan/LibriBrain/serialized/",
        preprocessing_str="bads+headpos+sss+notch+bp+ds",
        exclude_run_keys=[['0', '11', 'Sherlock1', '2'],
                          ['0', '12', 'Sherlock1', '2']],
        include_run_keys=[['0', '1', 'Sherlock1', '1'], ['0', '2', 'Sherlock1', '1'], ['0', '3', 'Sherlock1', '1'],
                          ['0', '4', 'Sherlock1', '1'], ['0', '5', 'Sherlock1', '1'], [
                              '0', '6', 'Sherlock1', '1'],
                          ['0', '7', 'Sherlock1', '1'], ['0', '8', 'Sherlock1', '1'], [
                              '0', '9', 'Sherlock1', '1'],
                          ['0', '10', 'Sherlock1', '1']],
    )
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=100, shuffle=True)
    batch = next(iter(loader))
    label_counts = torch.zeros(2)
    start_time = time.time()
    for i in range(len(dataset)):
        _, label = dataset[i]
        label_counts[label] += 1
        if i % 1000 == 0:
            print(time.time() - start_time)
            start_time = time.time()
    print(label_counts)
