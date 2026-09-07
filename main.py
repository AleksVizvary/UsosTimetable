from bs4 import BeautifulSoup
import requests
import pandas as pd
import pathlib
import re
from datetime import datetime

pd.set_option("display.max_columns", 500)


class TimetableError(Exception):
    pass


def get_lesson_dict(lesson):
    subject = lesson[0].strip()

    time_match = re.search(
        r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})",
        lesson[1],
    )
    if time_match is None:
        raise TimetableError("Nie udało się odczytać godzin zajęć z USOS-a.")

    time_start, time_end = time_match.groups()

    group_info = [part.strip() for part in lesson[2].split(",")]
    group_type = group_info[0]
    group_nr = ""

    group_match = re.search(r"grupa\s*(?:nr\s*)?(\d+)", lesson[2], re.IGNORECASE)
    if group_match is not None:
        group_nr = group_match.group(1)

    return {
        "subject": subject,
        "time_start": time_start,
        "time_end": time_end,
        "group_type": group_type,
        "group_nr": group_nr,
    }


def get_timetable_dict(url):
    if not url:
        raise TimetableError("Nie podano linku do planu.")

    try:
        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise TimetableError(f"Nie udało się pobrać planu z USOS-a: {error}")

    soup = BeautifulSoup(response.text, "html.parser")
    main_soup = soup.find("usos-timetable")

    if main_soup is None:
        raise TimetableError(
            "Nie znalazłem planu na tej stronie. Sprawdź link albo spróbuj ponownie później."
        )

    days = soup.find_all("timetable-day")
    if not days:
        raise TimetableError("USOS zwrócił pusty plan.")

    timetable_dict = {}

    for day in days:
        heading = day.find_previous("h4")
        if heading is None:
            raise TimetableError("Nie udało się odczytać dnia tygodnia z USOS-a.")

        day_name = heading.get_text(strip=True)
        timetable_tags = day.find_all("timetable-entry")
        lessons_per_day = []

        for tag in timetable_tags:
            subject = tag.get("name")
            date_time_tag = tag.find("span", {"slot": "dialog-event"})
            group_info_tag = tag.find("span", {"slot": "dialog-info"})

            if subject is None or date_time_tag is None or group_info_tag is None:
                raise TimetableError(
                    "Nie udało się odczytać części planu. USOS mógł zmienić format strony."
                )

            lesson_info = [
                subject,
                date_time_tag.get_text(" ", strip=True),
                group_info_tag.get_text(" ", strip=True),
            ]
            lessons_per_day.append(get_lesson_dict(lesson_info))

        timetable_dict[day_name] = lessons_per_day

    if not any(timetable_dict.values()):
        raise TimetableError("Nie znaleziono żadnych zajęć w tym planie.")

    return timetable_dict


def find_group_numbers_per_lesson_type(timetable_dict):
    group_numbers = {}

    for weekday in timetable_dict:
        for lesson in timetable_dict[weekday]:
            group_type = lesson["group_type"]
            group_nr = lesson["group_nr"]

            if group_type not in group_numbers:
                group_numbers[group_type] = set()

            if group_nr:
                group_numbers[group_type].add(group_nr)

    return {
        group_type: sorted(numbers, key=int)
        for group_type, numbers in group_numbers.items()
    }


def ask_yes_no(question):
    while True:
        answer = input(f"{question} y/n\n").strip().lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("Wpisz y albo n.")


def select_group_numbers(group_numbers_per_lesson_type, test=False):
    selected_group_numbers = {}
    include_all_types = {"wykład", "zajęcia z wf", "lektorat"}

    for group_type, available_numbers in group_numbers_per_lesson_type.items():
        normalized_type = group_type.casefold()

        if test:
            selected_group_numbers[group_type] = "*"
            continue

        if normalized_type in include_all_types or not available_numbers:
            if ask_yes_no(f"Dodawać {group_type}?"):
                # "*" means: include every entry of this type, regardless of its group number.
                selected_group_numbers[group_type] = "*"
            else:
                selected_group_numbers[group_type] = None
            continue

        numbers_text = ", ".join(available_numbers)
        while True:
            selected_group_nr = input(
                f"Wybierz grupę na {group_type.upper()} (dostępne: {numbers_text}): "
            ).strip()

            if selected_group_nr in available_numbers:
                selected_group_numbers[group_type] = selected_group_nr
                break

            print(f"Wybierz jeden z numerów: {numbers_text}")

    return selected_group_numbers


def create_timetable_for_selected_groups(timetable_dict, selected_group_numbers):
    final_timetable = {weekday: [] for weekday in timetable_dict}

    for weekday in timetable_dict:
        for lesson in timetable_dict[weekday]:
            lesson_type = lesson["group_type"]
            group_number = lesson["group_nr"]
            selected_group = selected_group_numbers.get(lesson_type)

            if selected_group is None:
                continue

            if selected_group == "*" or group_number == selected_group:
                final_timetable[weekday].append(lesson)

    return final_timetable


def create_pandas_frame(timetable):
    times = {
        lesson["time_start"]
        for weekday in timetable
        for lesson in timetable[weekday]
    }

    if not times:
        raise TimetableError("Dla wybranych grup plan jest pusty.")

    sorted_times = sorted(times, key=lambda value: datetime.strptime(value, "%H:%M"))
    indexes = [datetime.strptime(value, "%H:%M").time() for value in sorted_times]

    return pd.DataFrame(columns=timetable.keys(), index=indexes)


def fill_pandas_form(final_timetable_dict):
    df = create_pandas_frame(final_timetable_dict)

    for day in final_timetable_dict:
        for lesson in final_timetable_dict[day]:
            time_start = datetime.strptime(lesson["time_start"], "%H:%M").time()
            description = f'{lesson["group_type"]}: \n{lesson["subject"]}'
            current_value = df.at[time_start, day]

            if pd.isna(current_value):
                df.at[time_start, day] = description
            else:
                df.at[time_start, day] = f"{current_value}\n\n{description}"

    return df


def save_file(file, to_where_folder_name):
    destination_folder = pathlib.Path(__file__).parent.resolve() / to_where_folder_name
    destination_folder.mkdir(parents=True, exist_ok=True)

    nr = 1
    while True:
        output_path = destination_folder / f"schedule_{nr}.xlsx"
        if not output_path.exists():
            break
        nr += 1

    file.to_excel(output_path)
    return output_path


def combine(url, test=False):
    timetable_dict = get_timetable_dict(url)
    group_numbers = find_group_numbers_per_lesson_type(timetable_dict)
    selected_group_numbers = select_group_numbers(group_numbers, test)
    final_timetable_dict = create_timetable_for_selected_groups(
        timetable_dict, selected_group_numbers
    )
    filled_df = fill_pandas_form(final_timetable_dict)
    return save_file(filled_df, "timetables")


if __name__ == "__main__":
    try:
        url = input("Wklej link do planu:\n").strip()
        saved_file = combine(url)
        print(f"\nGotowe. Plan zapisany tutaj:\n{saved_file}")
    except TimetableError as error:
        print(f"\nBłąd: {error}")
        raise SystemExit(1)
