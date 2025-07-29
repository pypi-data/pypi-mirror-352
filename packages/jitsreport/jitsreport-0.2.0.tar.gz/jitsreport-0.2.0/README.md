# JIT Report- Just-In-Time Data Profiling Tool

[![PyPI version](https://badge.fury.io/py/jitsreport.svg)](https://pypi.org/project/jitsreport/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

JIT Report is a powerful Python package for generating comprehensive exploratory data analysis (EDA) reports from Excel files with just one line of code. It automatically analyzes your dataset and produces an interactive HTML report containing detailed statistics, visualizations, and data quality insights.

## Key Features

📊 **Automated Report Generation**  
✅ Single function call creates complete EDA report  
✅ Interactive HTML output with toggleable sections  

🔍 **Comprehensive Data Analysis**  
✔ Descriptive statistics (mean, median, std dev)  
✔ Quantile analysis (percentiles, IQR, range)  
✔ Variable characteristics (missing values, distinct counts)  

📈 **Rich Visualizations**  
📉 Histograms and boxplots for numeric variables  
📊 Bar charts for categorical variables  
🌡 Correlation heatmaps and scatter plots  

🛡 **Data Quality Checks**  
⚠ Missing value analysis  
⚠ Extreme value detection  
⚠ Duplicate row identification  

🖨 **Export-Ready Output**  
🖱 Interactive HTML with print-to-PDF functionality  
📱 Responsive design works on all devices  

## Installation

Install jitsreport using pip:

```bash
pip install jitsreport 

Quick Start:
import jitsreport as jr
OR
from jitsreport import generate_report_from_excel

# Generate a complete report with one line
jr.generate_report_from_excel("your_data.xlsx", output_html="analysis_report.html")

License:
MIT License - Free for commercial and personal use

Author
Surajit Das:
📧 Email: mr.surajitdas@gmail.com