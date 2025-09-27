from bs4 import BeautifulSoup
import requests
import pandas as pd
import pathlib
pd.set_option("display.max_columns", 500)


def get_lesson_dict(lesson):
    subject = lesson[0]

    time = lesson[1].replace(' ', '').split(',')[1].split('-')
    time_start = time[0]
    time_end = time[1]

    group_info = lesson[2].split(', ')
    group_nr = ''.join(i for i in group_info[1] if i.isdigit())
    group_type = group_info[0]


    lesson_dict = {'subject': subject,
                   'time_start': time_start,
                   'time_end': time_end,
                   'group_type': group_type,
                    'group_nr': group_nr}

    return lesson_dict

def get_timetable_dict(url):

    page_html = requests.get(url).text
    soup = BeautifulSoup(page_html, "html.parser")

    main_soup = soup.find("usos-timetable")
    days = main_soup.find_all('timetable-day')
    timetable_dict = {}

    for d in days:
        day_name = d.parent.find("h4").text
        timetable_tags = d.find_all("timetable-entry")
        lessons_per_day = []
        for t in timetable_tags:
            subject = t.get("name")
            date_time = t.find("span", {"slot": "dialog-event"}).text
            group_type_and_number = t.find("span", {"slot": "dialog-info"}).text

            lesson_info = [subject, date_time, group_type_and_number]
            lesson_dict = get_lesson_dict(lesson_info)

            lessons_per_day.append(lesson_dict)

        timetable_dict[day_name] = lessons_per_day

    return timetable_dict

def find_group_qty_per_lesson_type(timetable_dict):

    group_qty_per_lesson_type = {lesson['group_type']: 0 for weekday in timetable_dict for lesson in timetable_dict[weekday]}

    for weekday in timetable_dict:
        day = timetable_dict[weekday]
        for lesson in day:
            type = lesson['group_type']
            group_nr = lesson['group_nr']
            if int(group_nr) > int(group_qty_per_lesson_type[type]):
                group_qty_per_lesson_type[type] = group_nr

    return group_qty_per_lesson_type

def select_group_numbers(group_qty_per_lesson_type, test):
    if test:
        return {group: "1" for group in group_qty_per_lesson_type}

    selected_groups = {}
    for group_type in group_qty_per_lesson_type:
        while True:
            selected_group_nr = input(
                f"Choose group number for a {group_type.upper()} group, max {group_qty_per_lesson_type[group_type]} groupes: ")
            if selected_group_nr.isdigit() and 1 <= int(selected_group_nr) <= int(group_qty_per_lesson_type[group_type]):
                break
            print("🫥🫥🫥")

        selected_groups[group_type] = selected_group_nr
    return selected_groups

def create_timetable_for_selected_groups(timetable_dict, selected_group_numbers):
    final_timetable = {weekday: [] for weekday in timetable_dict}

    for weekday in timetable_dict:
        for lesson in timetable_dict[weekday]:
            lesson_type = lesson["group_type"]
            group_number = lesson["group_nr"]
            if group_number == selected_group_numbers[lesson_type]:
                final_timetable[weekday].append(lesson)

    return final_timetable

def create_pandas_frame(timetable):
    times_1 = {lesson['time_start'] for key in timetable.keys() for lesson in timetable[key]}
    times_2 = {lesson['time_end'] for key in timetable.keys() for lesson in timetable[key]}
    indexes = sorted(pd.to_datetime(list(times_1 | times_2), format="%H:%M").time)
    df = pd.DataFrame(columns=timetable.keys(), index=indexes)

    return df

def fill_pandas_form(final_timetable_dict):
    df = create_pandas_frame(final_timetable_dict)
    timetable = final_timetable_dict

    for day in timetable:
        for lesson in timetable[day]:
            time_start = pd.to_datetime(lesson["time_start"], format="%H:%M").time()
            time_end = pd.to_datetime(lesson["time_end"], format="%H:%M").time()
            mask = (df.index >= time_start) & (df.index <= time_end)
            df.loc[mask, day] = lesson["subject"]

    return df

def save_file(file, to_where_folder_name):

    destination_folder = f"{pathlib.Path(__file__).parent.resolve()}/{to_where_folder_name}"
    saves = [name.name for name in pathlib.Path(destination_folder).iterdir()]

    nr = 1
    while True:
        name = f"schedule_{nr}.xlsx"
        if name not in saves:
            break
        nr += 1

    file.to_excel(f"{destination_folder}/{name}")

def combine(url, test=False):
    timetable_dict = get_timetable_dict(url)
    # CREATES DICT TIMETABLE FOR ALL GROUPS ^^
    group_qty_per_lesson_type = find_group_qty_per_lesson_type(timetable_dict)
    selected_group_numbers = select_group_numbers(group_qty_per_lesson_type, test)
    # ALLOWS TO SPECIFY FOR NEEDED GROUPS NUMBERS  ^^
    final_timetable_dict = create_timetable_for_selected_groups(timetable_dict, selected_group_numbers)
    # CREARES DICT TIMETABLE FOR SELECTED GROUPS
    filled_df = fill_pandas_form(final_timetable_dict)
    # CREATES A PANDA FORM AND FILLS IT WITH DICT TIMETABLE
    save_file(filled_df, "timetables")


url = "https://web.usos.agh.edu.pl/kontroler.php?_action=katalog2%2Fprzedmioty%2FpokazPlanGrupyPrzedmiotow&grupa_kod=ITE_1S_sem1&cdyd_kod=25%2F26-Z&fbclid=IwY"
timetable = combine(url)

