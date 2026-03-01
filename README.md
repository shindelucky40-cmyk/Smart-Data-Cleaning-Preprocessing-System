# Smart Data Cleaning & Preprocessing System

A robust Flask-based web application designed to streamline the process of analyzing, cleaning, and preprocessing tabular data.

## 🚀 Features

### 1. Data Upload
- Supports **CSV**, **Excel** (`.xls`, `.xlsx`), and **JSON** formats.
- Secure file handling with UUID-based sessions.

### 2. Automated Analysis
- **Missing Values**: Detects missing data and calculates percentages.
- **Duplicate Rows**: Identifies duplicate entries.
- **Constant Columns**: Finds columns with a single unique value.
- **Outliers**: Detects outliers using the Interquartile Range (IQR) method.
- **Whitespace Issues**: Checks for leading/trailing whitespace in text columns.

### 3. Data Cleaning
- **Trim Whitespace**: Automatically trim whitespace from string columns.
- **Remove Duplicates**: Drop duplicate rows.
- **Handle Missing Values**: Impute using Mean, Median, Mode, or Drop rows.
- **Handle Outliers**: Cap outliers to IQR bounds or remove them.
- **Remove Constant Columns**: Drop columns that provide no information.

### 4. Preprocessing
- **Datetime Extraction**: Extract Year, Month, Day, and DayOfWeek from datetime columns.
- **Categorical Encoding**: Support for Label Encoding and One-Hot Encoding.
- **Numeric Scaling**: Standardize (Z-score) or Normalize (MinMax) numeric features.

### 5. Export
- Download the processed dataset in **CSV**, **Excel**, or **JSON** format.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd "Smart Data Cleaning & Preprocessing System"
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. **Run the application**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   Open your browser and navigate to `http://localhost:5000`.

3. **Workflow**
   - Upload your dataset.
   - Review the automated analysis report.
   - Select cleaning and preprocessing options.
   - Click "Apply Cleaning".
   - Download the cleaned dataset.

## 📂 Project Structure

```
Smart Data Cleaning & Preprocessing System/
├── app.py                 # Main Flask application entry point
├── data_processor.py      # Core data analysis and cleaning logic
├── requirements.txt       # Python dependencies
├── static/
│   ├── index.html         # Main user interface
│   ├── style.css          # Styling
│   └── app.js             # Frontend logic
└── uploads/               # Temporary storage for uploaded files
```

---
**Note**: This project is intended for educational and development purposes.
