"""
Class:
- CNNModel: 1D CNN with two convolutional layers and one adaptive fully connected layer.
  Automatically initializes fully connected layer based on feature dimensions during first forward pass.
"""

import torch
import torch.nn as nn

class CNNModel(nn.Module):
    def __init__(self, num_filters1=16, num_filters2=32, fc1_size=64):
        super().__init__()
        self.conv1 = nn.Conv1d(1, num_filters1, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(num_filters1, num_filters2, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.fc1 = None
        self.fc2 = nn.Linear(fc1_size, 1)

    def _initialize_fc(self, x, fc1_size):
        with torch.no_grad():
            x = self.relu(self.conv1(x))
            x = self.relu(self.conv2(x))
            x = x.view(x.size(0), -1)
            self.fc1 = nn.Linear(x.shape[1], fc1_size).to(x.device)
            self.fc2 = nn.Linear(fc1_size, 1).to(x.device)

    def forward(self, x):
        if self.fc1 is None:
            self._initialize_fc(x, self.fc2.in_features)
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        return self.fc2(x)