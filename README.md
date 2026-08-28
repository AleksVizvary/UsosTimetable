# UsosTimetable

I made this because checking the full USOS timetable and figuring out my actual groups every time was annoying.

The script downloads the AGH USOS timetable, reads all available groups and lets me generate a much simpler `.xlsx` timetable with only the groups I choose.

## what it does

- downloads the timetable from USOS
- parses the HTML with BeautifulSoup
- reads subjects, hours, group types and group numbers
- lets me choose the groups I need
- builds a timetable with pandas
- exports it to `.xlsx`

## setup

```bash
git clone https://github.com/AleksVizvary/UsosTimetable.git
cd UsosTimetable
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For now the USOS timetable URL is set in the code. Run:

```bash
python main.py
```

## status

works for the current AGH USOS timetable format. if the HTML structure changes, the parser will probably need an update.
