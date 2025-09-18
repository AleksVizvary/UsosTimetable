import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import pandas as pd
import datetime
import os
import pathlib

### CLEANING THE DATE & TIME ###

def prettify_godz(time_str):

    time = "".join([g for g in time_str if g.isdigit()])
    periodicity = ""

    if len(time) == 3:
        periodicity = time_str[0:-4]
        time = time[0] + ':' + time[1:]
    elif len(time) == 4:
        periodicity = time_str[0:-5]
        time = time[0:2] + ':' + time[2:]
    if len(time_str) == 4 or len(time_str) == 5:
        periodicity = "everyday"

    return periodicity, time

### HELPING WITH PARSING ###

def extract_lesson_data(lesson_soup):

    lesson_name = lesson_soup.get("name")

    lesson_info_soup = lesson_soup.find("div", {"slot": "info"}).text.split()
    lesson_type, group_nr = lesson_info_soup[0].strip(','), lesson_info_soup[2]
    building, room = lesson_info_soup[-1].strip(',').strip('(').strip(')'), lesson_info_soup[-3].strip(',').strip('(').strip(')')


    time_str = lesson_soup.find("span", {"slot": "time"}).text
    periodicity, time = prettify_godz(time_str)

    lesson_dict = {"subject": lesson_name,
                       "time": time,
                       "periodicity": periodicity,
                       "lesson type": lesson_type,
                       "group nr": group_nr,
                       "building": building,
                       "room": room
                       }

    return lesson_dict

def create_lessons_list(lessons_soup):
    lessons = []
    for paragraph in lessons_soup:
        lesson_dict = extract_lesson_data(paragraph)

        lessons.append(lesson_dict)

    return lessons

### RETURNING ONLY NEEDED GROUPS ###

def find_group_qty_per_lesson_type(timetable_dict):
    group_types = {lesson['lesson type']: 0 for weekday in timetable_dict for lesson in timetable_dict[weekday]}

    for weekday in timetable_dict:
        day = timetable_dict[weekday]
        for lesson in day:
            type = lesson['lesson type']
            group_nr = lesson['group nr']
            if int(group_nr) > int(group_types[type]):
                group_types[type] = group_nr

    return group_types

def select_group_numbers(group_qty_per_lesson_type, test):

    if test:
        return {group: "1" for group in group_qty_per_lesson_type}

    selected_groups = {}
    for group_type in group_qty_per_lesson_type:
        while True:
            selected_group_nr = input(
                f"Choose group number for a group group_type of {group_type}, max {group_qty_per_lesson_type[group_type]} groupes: ")
            if selected_group_nr.isdigit() and 1 <= int(selected_group_nr) <= int(group_qty_per_lesson_type[group_type]):
                break
            print("🫥🫥🫥")

        selected_groups[group_type] = selected_group_nr
    return selected_groups


### CREATING PANDAS SET ###

def create_pandas_form(timetable):
    starting_hours_str = []

    for day in timetable:
        for lesson in timetable[day]:
            if lesson["time"] not in starting_hours_str:
                starting_hours_str.append(lesson["time"])

    days = {day_name: [" " for i in range(len(starting_hours_str))] for day_name in timetable}
    starting_hours = sorted([datetime.time(int(hour.split(':')[0]), int(hour.split(':')[1])) for hour in starting_hours_str])

    return pd.DataFrame(days, index = starting_hours, dtype=object)

def add_lesson_to_pandas_form(day_name, lesson, pandas_form):
    starting_hour = lesson["time"].split(':')
    subject = lesson["subject"]
    lesson_type = lesson["lesson type"]
    row = datetime.time(int(starting_hour[0]), int(starting_hour[1]))
    column = day_name
    pandas_form.loc[row, column] = f"{subject} ({lesson_type.upper()})"

    return pandas_form

def create_completed_pandas_form(raw_timetable, test=False):

    timetable = create_pandas_form(raw_timetable)

    for day in raw_timetable:
        for lesson in raw_timetable[day]:
            timetable = add_lesson_to_pandas_form(day, lesson, timetable)

    return timetable

def save_file(final_file):

    path = pathlib.Path(__file__).parent.resolve()
    path = f"/{path}/timetables"

    lista_plikow = os.listdir(path)
    nr = 1
    nazwa = f"plan_{nr}.xlsx"



    while True:
        nazwa = f"plan_{nr}.xlsx"
        if nazwa not in lista_plikow:
            break
        nr += 1

    final_file.to_excel(f"/Users/aleksandervizvary/Documents/Programs/UsosProject/timetables/{nazwa}")

### CREATING REPORT (SHOWS CLASSES QTY AND ELSE DATA) ###

def create_report(timetable_dict):
    subjects_qty = {lesson["subject"]: 0 for weekday in timetable_dict for lesson in timetable_dict[weekday]}
    lesson_types_qty = {lesson["lesson type"]: 0 for weekday in timetable_dict for lesson in timetable_dict[weekday]}

    for weekday in timetable_dict:
        for lesson in timetable_dict[weekday]:
            subjects_qty[lesson["subject"]] += 1
            lesson_types_qty[lesson["lesson type"]] += 1

    report = [subjects_qty, lesson_types_qty]

    return report

def save_report(report):

    path = pathlib.Path(__file__).parent.resolve()
    path = f"/{path}/reports"
    files_list = os.listdir(path)

    nr = 1
    while True:
        file_name = f"report_nr_{nr}.txt"
        if file_name not in files_list:
            break
        nr += 1

    path = f"{path}/{file_name}"

    with open(path, "w") as text_file:

        text_file.write("Iilosci poszczególnych zajęc:")
        text_file.write("\n")
        for i in report[0]:
            text_file.write(f"{i}: {report[0][i]}")
            text_file.write("\n")

        text_file.write(" ")
        text_file.write("\n")

        text_file.write("Iilosci poszczególnych rodzajów zajęc:")
        text_file.write("\n")
        for i in report[1]:
            text_file.write(f"{i}: {report[1][i]}")
            text_file.write("\n")


### MAIN FUNCTIONS ###

def create_timetable_soup(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

    except:
        print("Not today now, lad")
        exit()

    try:
        timetable_soup = soup.find("usos-timetable")
    except:
        exit()

    try:
        timetable_day_list = timetable_soup.contents
    except:
        print("Not today now, lad")
        exit()

    return timetable_day_list

def create_timetable_dict(timetable_day_list):
    raw_timetable = {}

    for paragraf in timetable_day_list:
        if isinstance(paragraf, Tag):
            day_name = paragraf.find("h4").text
            raw_timetable[day_name] = []

    for paragraf in timetable_day_list:
        if isinstance(paragraf, Tag):
            day_name = paragraf.find("h4").text
            timetable_day_soup = paragraf.find("timetable-day")
            raw_lesson = timetable_day_soup.find_all("timetable-entry")

            lessons = create_lessons_list(raw_lesson)
            for l in lessons:
                if l is not None:
                    raw_timetable[day_name].append(l)


    return raw_timetable

def create_timetable_for_selected_groups(timetable_dict, selected_group_numbers):
    final_timetable = {weekday: [] for weekday in timetable_dict}

    for weekday in timetable_dict:
        for lesson in timetable_dict[weekday]:
            lesson_type = lesson["lesson type"]
            group_number = lesson["group nr"]
            if group_number == selected_group_numbers[lesson_type]:
                final_timetable[weekday].append(lesson)

    return final_timetable

def create_final_timetable(url, test=False):
    timetable_soup = create_timetable_soup(url)
    timetable_dict = create_timetable_dict(timetable_soup)
    group_qty_per_lesson_type = find_group_qty_per_lesson_type(timetable_dict)
    selected_group_numbers = select_group_numbers(group_qty_per_lesson_type, test)

    final_timetable_dict = create_timetable_for_selected_groups(timetable_dict, selected_group_numbers)
    return final_timetable_dict

### COMBINED FUNCTIONS ###

def print_raw_timetable(timetable_dict):

    print("=======")
    for weekday in timetable_dict:
        print("-------+++-------")
        day = timetable_dict[weekday]
        print(weekday)
        print("-------+++-------")

        for day_timetable in day:
            for lesson in day_timetable:
                print(f"{lesson}: {day_timetable[lesson]}")
            print("============================")

def run(url, test=False):

    timetable_dict = create_final_timetable(url, test)

    if test:
        final_file = create_completed_pandas_form(timetable_dict, test)
        print_raw_timetable(timetable_dict)

    report = create_report(timetable_dict)
    save_report(report)

    final_file = create_completed_pandas_form(timetable_dict, test)
    save_file(final_file)

### ================== ###

url = "https://web.usos.agh.edu.pl/kontroler.php?_action=katalog2%2Fprzedmioty%2FpokazPlanGrupyPrzedmiotow&grupa_kod=ITE_1S_sem1&cdyd_kod=25%2F26-Z&fbclid=IwY"
test = True
run(url, test)
