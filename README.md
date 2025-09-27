# UsosTimetable

A Python tool for fetching and organizing university timetables from [USOS AGH](https://usosweb.agh.edu.pl/).  
It scrapes the timetable page, extracts lessons and groups, and saves the final schedule into an Excel file.

---

## Features
- Scrapes timetable data from USOS (via `requests` + `BeautifulSoup`)
- Converts timetable into a structured Python dictionary
- Lets you **select specific group numbers** for each lesson type
- Creates a **pandas DataFrame** with times and days as a grid
- Saves the final schedule as an Excel file in the `timetables/` folder

---

## Requirements
- Python 3.12+
- Packages:  
  - `pandas`  
  - `requests`  
  - `beautifulsoup4`  
  - `pathlib`

---

## Usage

### Clone the repo and set up a virtual environment:

```bash
git clone git@github.com:AleksVizvary/UsosTimetable.git
cd UsosTimetable
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```

### Run the main script (replace the URL with your own timetable link):

```bash python -m UsosProject.main```

### The script will:

Ask you which group number to choose for each lesson type **(or auto-select if test=True)**.

Build a weekly timetable in pandas.

Save it as schedule_X.xlsx inside the timetables/ folder.