from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predict import predict

rng = np.random.default_rng()

rows = pd.DataFrame({
    "FSR1": rng.integers(0, 4096, 10),
    "FSR2": rng.integers(0, 4096, 10),
    "FSR3": rng.integers(0, 4096, 10),
    "FSR4": rng.integers(0, 4096, 10),
    "Temperature": np.round(rng.uniform(28.0, 38.0, 10), 2),
})

result = predict(rows)
output = pd.concat([rows, result], axis=1)

print(output.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
