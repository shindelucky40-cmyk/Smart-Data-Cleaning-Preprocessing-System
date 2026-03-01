# Smart Data Cleaning & Preprocessing System 🧹📊

![Web App Preview](https://img.shields.io/badge/Status-Live%20on%20Render-success?style=for-the-badge&logo=render)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black?style=for-the-badge&logo=flask)
![Pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikit-learn)

**Live Demo:** [Smart Data Cleaning System on Render](https://smart-data-cleaning-preprocessing-system-y2jw.onrender.com)

A powerful, user-friendly web application that allows users to seamlessly upload, analyze, clean, and preprocess their tabular datasets. From handling missing values and duplicate rows to encoding and scaling for machine learning, this system takes the heavy lifting out of data preprocessing.

---

## ✨ Features

### 📁 File Support
Robust parsing for a variety of tabular formats including `.csv`, `.tsv`, `.xlsx`, `.xls`, `.json`, `.parquet`, and `.xml`.

### 🔍 Automated Data Analysis
Simply drop a file, and the app instantly provides:
- Exact row and column count.
- Data types for every column.
- Automatically flags columns with missing values.
- Issues related to outliers, exact duplicates, and leading/trailing whitespace.
- A beautiful and quick data preview!

### 🧹 Smart Data Cleaning
Empower your dataset with the following tools:
- **Handle Missing Data**: Select a strategy (Drop rows, Mean, Median, Mode, or KNN Imputation).
- **Remove Duplicates**: Instantly nuke repeated rows.
- **Outlier Treatments**: Automatically cap or remove outliers per numeric column.
- **Clean Text**: Easily strip out hidden trailing or leading whitespaces.
- **Drop Useless Columns**: Autodetect and drop constant (single-value) columns.

### ⚙️ Advanced ML Preprocessing
Get your data ready for scikit-learn or PyTorch!
- **Encode Categoricals**: Convert text labels using Label Encoding or One-Hot Encoding.
- **Scale Numerics**: Standard Scaler (Z-Score) or Min-Max Scaler (0 to 1).
- **Date/Time Extraction**: Convert datetime strings to features `Year`, `Month`, `Day`, and `DayOfWeek`.
- **Log Transforms**: Auto log-transform highly skewed positive numerical features.
- **Text Clean-ups**: Rapidly convert string columns to lowercase and remove punctuation.

### 📈 Data Visualization
- **Histograms** for numeric columns to visualize distribution.
- **Bar Charts** to summarize high-count categories.
- **Correlation Matrix** to rapidly figure out linear relationships among attributes.

### 📥 Download Processed Data
Easily export the fully prepared and cleaned dataset securely to your local machine as `.csv`, `.xlsx`, or `.json`.

---

## 🚀 How to Run Locally

If you'd like to spin it up natively on your machine:

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/smart-data-cleaning-preprocessing.git
   cd smart-data-cleaning-preprocessing
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask App**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000` to start cleaning!

---

## ☁️ Deployment (Render)

This project has been specifically configured to easily deploy onto [Render.com](https://render.com/).

To deploy your own copy:
1. Connect your GitHub branch to a new **Web Service** on Render.
2. The provided `render.yaml` ensures Render recognizes the environment as Python, loads `requirements.txt`, and uses the start command `python app.py`.
3. Sit back, deploy, and verify it!

---

## 📁 Project Structure

```text
├── app.py                # Flask server, routing, REST API 
├── data_processor.py     # Core Engine: Pandas parsing, sklearn transforms
├── render.yaml           # Deployment configuration file
├── requirements.txt      # Python dependencies
└── static/
    ├── index.html        # Frontend user interface
    ├── default.css       # Custom styling/aesthetic 
    └── app.js            # Frontend logic to hit endpoints
```
