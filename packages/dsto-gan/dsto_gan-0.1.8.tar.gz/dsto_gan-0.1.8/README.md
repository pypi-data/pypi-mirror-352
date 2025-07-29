# DSTO-GAN: Balancing Data with GAN

**DSTO-GAN** is a Python library that uses a Generative Adversarial Network (GAN) to generate synthetic samples and balance imbalanced datasets. It is beneficial for classification problems where classes are disproportionate.

---

## Features

1. **Generating synthetic samples** for class balancing.
2. **Training a custom GAN** for tabular data.
3. **Saving the balanced dataset** to a `.csv` file.

---

## Prerequisites

- **Python 3.7 or higher**.
- **`pip` package manager**.

## Installation

You can install the library directly via `pip`:

```bash
pip install dsto-gan
```

### Dependencies

The dependencies will be installed automatically during the installation. If you prefer to install manually, run:

```bash
pip install numpy torch pandas scikit-learn xgboost scikit-optimize
```

## How to Use

### 1. Import and Initialization

First, import the DSTO_GAN class and initialize the object:

from dsto_gan import DSTO_GAN

# Initialize DSTO-GAN
```bash
dsto_gan = DSTO_GAN(dim_h=64, n_z=10, lr=0.0002, epochs=100, batch_size=64)

```

### 2. Balancing Data

Use the fit_resample method to balance the data:

```bash
# Imbalanced data
X = ... # Features (numpy array or pandas DataFrame)
y = ... # Labels (numpy array or pandas Series)

# Balance the data
X_resampled, y_resampled = dsto_gan.fit_resample(X, y)

print(f"Shape of the balanced data: {X_resampled.shape}, {y_resampled.shape}")
```

### 3. Integration with Scikit-Learn

DSTO_GAN is compatible with Scikit-Learn pipelines. You can use it as part of a preprocessing pipeline:

```bash
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Split the data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a pipeline with DSTO-GAN and a classifier
pipeline = Pipeline([
('dsto_gan', DSTO_GAN()), # Balancing with DSTO-GAN
('classifier', RandomForestClassifier()) # Classifier
])

# Train the model
pipeline.fit(X_train, y_train)

# Evaluate the model
accuracy = pipeline.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.2f}")

---

## Usage Example

Here is a complete usage example of DSTO-GAN:

```bash
import pandas as pd
from sklearn.model_selection import train_test_split
from dsto_gan import DSTO_GAN

# 1. Load imbalanced data
file_path = "path/to/imbalanced.csv"
df = pd.read_csv(file_path)

# 2. Separate features (X) and labels (y)
X = df.iloc[:, :-1].values ​​# All columns except the last one
y = df.iloc[:, -1].values ​​# Last column is the class

# 3. Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Balance training data with DSTO-GAN
dsto_gan = DSTO_GAN()
X_train_resampled, y_train_resampled = dsto_gan.fit_resample(X_train, y_train)

print(f"Shape of balanced data: {X_train_resampled.shape}, {y_train_resampled.shape}")
```
---

## Project Structure

```
dsto_gan/
│
├── dsto_gan/ # Main package
│ ├── __init__.py # Package initialization
│ ├── dsto_gan.py # Core code for data balancing
├── setup.py # Package configuration
├── README.md # Project documentation
└── LICENSE # Project license
```

---

## Contribution

Contributions are welcome! If you encounter problems or have suggestions for improvements, feel free to open an issue or submit a pull request.
---

## License

This project is licensed under the **MIT License**. See the [LICENSE] file for more details.

---

## Contact

- **Author**: Erika Assis
- **Email**: dudabh@gmail.com
- **Repository**: [GitHub](https://github.com/erikaduda/dsto_gan)

---

## Acknowledgements

This project was developed as part of research on data balancing using GANs. The open-source community provided the libraries used.