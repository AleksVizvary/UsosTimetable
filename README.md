# UsosTimetable

Program pozwala generować własnego planu zajęć na podstawie planu dostępnego w systemie USOS AGH, w celu zwizualizowania jak może wyglądać plan zajęć na nadchodzący semestr (bo zawsze jest dzień przed zajęciami, pozdro).

Program korzysta z planu dla całego semestru i roku kierunku, pobiera wszystkie dostępne zajęcia oraz grupy, a następnie generuje indywidualny plan zajęć na podstawie wybranych przez użytkownika grup.

Przykładowo: jeżeli w USOS widoczny jest pełny plan dla danego semestru, zawierający wykłady, ćwiczenia, laboratoria, projekty, lektoraty i WF dla wielu grup, program pozwala wybrać konkretne grupy i zapisuje gotowy, uproszczony plan do pliku Excel.

## Instalacja

```bash
git clone git@github.com:AleksVizvary/UsosTimetable.git
cd UsosTimetable
python3 -m venv venv
source venv/bin/activate
pip install -r reuirements.txt
```

## Uruchomienie

Obecnie link do planu należy przekazać w kodzie.

Żeby szybko wygenerować przykładowy plan bez ręcznego wybierania grup, można użyć trybu testu:

```python
combine(url, True)
```

Aby samodzielnie wybrać grupy, należy uruchomić program z `test=False`:

```python
combine(url, False)
```

## Aktualne ograniczenia

- Link do planu USOS nie jest jeszcze wygodnie podawany z terminala.
- Jeżeli USOS zmieni strukturę HTML, parser może wymagać poprawek.

## Requirements

```txt
beautifulsoup4==4.14.0
bs4==0.0.2
certifi==2025.8.3
charset-normalizer==3.4.3
idna==3.10
numpy==2.3.3
pandas==2.3.2
pathlib==1.0.1
python-dateutil==2.9.0.post0
pytz==2025.2
requests==2.32.5
six==1.17.0
soupsieve==2.8
typing_extensions==4.15.0
tzdata==2025.2
urllib3==2.5.0

```

## Funkcje

- Pobieranie strony z planem zajęć z USOS AGH.
- Parsowanie danych z HTML przy użyciu `requests` oraz `BeautifulSoup`.
- Odczytywanie informacji o zajęciach:
  - nazwa przedmiotu,
  - dzień tygodnia,
  - godzina rozpoczęcia,
  - godzina zakończenia,
  - typ zajęć,
  - numer grupy.
- Tworzenie słownika z pełnym planem zajęć dla wszystkich grup.
- Wyszukiwanie maksymalnej liczby grup dla każdego typu zajęć.
- Interaktywny wybór numerów grup dla poszczególnych typów zajęć.
- Możliwość dodania albo pominięcia wykładów.
- Możliwość dodania albo pominięcia WF-u.
- Możliwość dodania albo pominięcia lektoratu.
- Automatyczne utworzenie planu tylko dla wybranych grup.
- Konwersja planu do `pandas.DataFrame`.
- Utworzenie tabeli, w której:
  - kolumny odpowiadają dniom tygodnia,
  - wiersze odpowiadają godzinom zajęć.
- Eksport gotowego planu do pliku `.xlsx`.
- Automatyczne zapisywanie kolejnych plików jako `schedule_1.xlsx`, `schedule_2.xlsx`, `schedule_3.xlsx` itd.
- Zapisywanie gotowych planów w folderze `timetables/`.

## Etapy działania programu

Program wykonuje kolejne etapy:

1. Pobiera stronę z planem zajęć z USOS.
2. Odczytuje wszystkie zajęcia widoczne w planie.
3. Dzieli zajęcia według dni tygodnia.
4. Dla każdego zajęcia zapisuje nazwę przedmiotu, godzinę, typ zajęć i numer grupy.
5. Sprawdza, ile grup istnieje dla każdego typu zajęć.
6. Pyta użytkownika, które grupy chce uwzględnić.
7. Pomija zajęcia z niewybranych grup.
8. Tworzy tabelę planu zajęć.
9. Zapisuje wynik do pliku Excel.