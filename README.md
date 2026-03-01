# ✨ Smart Data Cleaning & Preprocessing System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)
![HTML](https://img.shields.io/badge/HTML5-Frontend-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-Styled-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Interactive-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

**Upload · Detect · Clean · Download — ready for ML in minutes**

### 🚀 [Live Demo → smart-data-cleaning-preprocessing-system-y2jw.onrender.com](https://smart-data-cleaning-preprocessing-system-y2jw.onrender.com)

</div>

---

## 📖 About

The **Smart Data Cleaning & Preprocessing System** is a web-based tool that helps data scientists, analysts, and ML engineers clean and preprocess messy datasets — without writing a single line of code.

Simply upload your file, review detected issues, configure your cleaning options, and download the cleaned data in your preferred format. The entire pipeline runs in **4 intuitive steps**.

---

## 🖼️ Preview

| Step | Description |
|------|-------------|
| **1. Upload** | Drop a CSV, Excel, or JSON file |
| **2. Preview** | View raw data, detected issues, and auto-generated visualizations |
| **3. Configure** | Select cleaning and preprocessing options |
| **4. Results** | Review the change report and download your cleaned dataset |

---

## ✅ Features

### 🧹 Data Cleaning
- **Missing Values** — Fill with Mean / Median / Mode, KNN Imputation, or Drop Rows
- **Remove Duplicates** — Automatically detect and remove duplicate rows
- **Trim Whitespace** — Strip leading/trailing spaces from string columns
- **Outlier Handling** — Cap using IQR method or remove outlier rows entirely
- **Constant Columns** — Drop columns with zero variance
- **Clean Text Data** — Normalize and sanitize text fields

### 🔬 Preprocessing
- **Encode Categoricals** — Label Encoding or One-Hot Encoding
- **Scale Numerics** — Standard Scaler or Min-Max Scaler
- **Extract Datetime** — Decompose datetime columns into day, month, year, etc.
- **Log Transform** — Apply Log1p transformation for skewed numeric features

### 📊 Data Insights
- Auto-detects dataset issues on upload
- Interactive data visualizations
- Raw data preview (first 100 rows)
- Full changes report after cleaning

### 📥 Export Options
Download your cleaned dataset as:
- **CSV**
- **Excel (.xlsx)**
- **JSON**

---

## 📂 Supported Input Formats

| Format | Extension |
|--------|-----------|
| CSV | `.csv` |
| Excel | `.xlsx`, `.xls` |
| JSON | `.json` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Data Processing | Pandas, NumPy, Scikit-learn |
| Deployment | Render |

---

## 🚀 Getting Started (Run Locally)

### 1. Clone the repository
```bash
git clone https://github.com/shindelucky40-cmyk/Smart-Data-Cleaning-Preprocessing-System.git
cd "Smart-Data-Cleaning-Preprocessing-System/Smart Data Cleaning & Preprocessing System"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🌐 Deployment

This project is deployed on **Render**.

🔗 **Live URL:** [https://smart-data-cleaning-preprocessing-system-y2jw.onrender.com](https://smart-data-cleaning-preprocessing-system-y2jw.onrender.com)

> ⚠️ Note: The app may take ~30–60 seconds to wake up on first load since it runs on Render's free tier (spins down during inactivity).

---

## 📋 How to Use

1. **Go to the live app** or run it locally
2. **Upload** your dataset (CSV / Excel / JSON)
3. **Preview** detected issues and data charts
4. **Configure** your cleaning and preprocessing options
5. **Run Cleaning** and review the applied changes
6. **Download** the cleaned file in your preferred format

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
## Author 

   Lalit shinde 

---
   
## 📄 License

This project is open source. Feel free to use and modify it.

---

<div align="center">
Made with ❤️ by <a href="https://github.com/shindelucky40-cmyk">shindelucky40-cmyk</a>
</div>
