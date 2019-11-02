import os
from urllib.parse import urlparse

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision.datasets.utils import download_url

class UCIDatasets(Dataset):

    uci_dataset_configs = {
        'yacht': {
            'url': "http://archive.ics.uci.edu/ml/machine-learning-databases/00243/yacht_hydrodynamics.data",
            'features': np.arange(6),
            'targets': [6],
        }
    }

    def __init__(self, dataset_name, root_dir, transform=None, download=True):

        self.dataset_name = dataset_name
        self.root_dir = root_dir
        self.transform = transform

        # Get the url and file name for the requested dataset_name
        self.url = self.uci_dataset_configs[self.dataset_name]['url']
        self.filename = os.path.basename(urlparse(self.url).path)

        if download:
            self.download()

        # Process the downloaded data
        fp = os.path.join(self.root_dir, self.filename)
        self.data = np.loadtxt(fp)

        # Store feature / target columns
        self.features = self.uci_dataset_configs[self.dataset_name]['features']
        self.targets = self.uci_dataset_configs[self.dataset_name]['targets']

    def __len__(self):
        return len(self.landmarks_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        sample = (self.data[idx][self.features], self.data[idx][self.targets])

        return sample

    def download(self):
        download_url(self.url, self.root_dir, self.filename)
