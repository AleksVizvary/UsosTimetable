# UsosTimetable

Skrypt w Pythonie do zrobienia własnego planu z planu USOS AGH.

Podajesz link do planu, wybierasz swoje grupy i dostajesz plik `.xlsx` tylko z tymi zajęciami, które Cię interesują.

## Instalacja

Potrzebny jest Python 3 i Git.

Najpierw pobierz repo:

```bash
git clone https://github.com/AleksVizvary/UsosTimetable.git
cd UsosTimetable
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Windows PowerShell

```powershell
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
py main.py
```

## Użycie

Po uruchomieniu program poprosi o link do planu USOS:

```text
Wklej link do planu USOS:
```

Otwórz plan grupy w USOS-ie i skopiuj cały adres z przeglądarki.

Potem program pokaże dostępne numery grup dla każdego typu zajęć. Wybierz swoje numery. Przy wykładzie, WF-ie i lektoracie wystarczy odpowiedzieć `y` albo `n`.

Gotowy plik zapisze się w folderze `timetables`, np.:

```text
timetables/schedule_1.xlsx
```

Przy kolejnym uruchomieniu powstanie `schedule_2.xlsx`, itd.

## Jeśli coś nie działa

Skrypt jest napisany pod obecny format planu na USOS AGH. Jeśli USOS zmieni układ strony, parser może wymagać poprawki.
