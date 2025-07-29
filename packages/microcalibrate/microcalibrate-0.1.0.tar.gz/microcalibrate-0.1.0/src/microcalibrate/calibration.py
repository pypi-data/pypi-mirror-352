import pandas as pd
import numpy as np


class Calibration:
    def __init__(
        self,
        data: pd.DataFrame,
        weights: np.ndarray,
        targets: np.ndarray,
    ):
        self.data = data
        self.weights = weights
        self.targets = targets

    def calibrate(self):
        from .reweight import reweight

        new_weights, subsample = reweight(
            original_weights=self.weights,
            loss_matrix=self.data,
            targets_array=self.targets,
            epochs=32,
        )

        self.data = self.data.loc[subsample]
        self.weights = new_weights
