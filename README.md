# Mass Spec Peak Analyzer

A user-friendly Streamlit app to analyze mass spectrometry peak data from CSV files. Merge peaks across multiple cell lines and days, normalize by the number of scans, identify top peaks, and generate both CSV and PDF outputs with interactive visualization.

---

## Features

- Drag-and-drop multiple CSV files for analysis.
- Normalize peak intensities by the "Number of Scans" column.
- Merge peaks based on user-defined m/z tolerance.
- Highlight top peaks based on user-defined percentage threshold.
- Generate:
  - Merged CSV file with normalized peak intensities.
  - PDF figure showing all peaks across cell lines and days with top peaks annotated.
  - TXT file with top peaks for quick reference.
- Interactive visualization via Streamlit.
- Fully customizable:
  - Output file names
  - m/z tolerance
  - Significance threshold (%)

---

## Folder Structure
mass_spec_analyzer/
- app.py # Streamlit app code
- requirements.txt # Python dependencies
- README.md # Instructions and usage

---

## Setup Instructions

### 1. Install Python
Download and install [Python 3.8 or higher](https://www.python.org/downloads/).

### 2. Install git
Download and install [GIT](https://git-scm.com/downloads). 

### 3. Clone the Repository
Open up your terminal and copy and paste the below in to it.

```bash
git --version
git clone https://github.com/maxgeorgejackson/HDI
cd HDI
```

### 4 Create a virtual environment
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5 Install dependancies
```bash
pip install --upgrade pip
pip install -r requirments.txt
```

### 6 Run the app 
```bash
streamlit run app.py
```

## How to run after setup

### 1 Terminal
Open up the terminal and put the following command in:
```bash
cd HDI
```
Then activate the environment:
Windows
```bash
venv\Scripts\activate
```
Mac/Linux
```bash
venv/bin/activate
```

### 2 Run app

Then we run the app, easy as that!
```bash
streamlit run app.py
```

### Functionality
This tool takes files in the exact format of the other examples you showed me. You can drag and drop or search for files in the top box.

Output csv and pdf names are whatever you want just make sure to add the .csv and .pdf respectivly.

m/z tolerance is the value you want it to merge either side so change this as you wish.

Top % threshold is for the graph and the txt file and is basically used just to inspect the data to quickly check the values seem correct.

Good luck!
