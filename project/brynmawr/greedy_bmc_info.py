#!/usr/bin/python

import csv
import sys

def build_course_ids(list_of_dicts):
    course_id_map = {}
    counter = 1

    for d in list_of_dicts:
        course = d["Course ID"]

        course = course.rstrip()
    

        if course and course not in course_id_map:
            course_id_map[course] = counter
            counter += 1

    return course_id_map

def build_professor_ids(list_of_dicts):
    prof_id_map = {}
    counter = 1

    for d in list_of_dicts:
        prof = d.get("Instructor ID")

        if prof and prof != "#Value!":
            if prof not in prof_id_map:
                prof_id_map[prof] = counter
                counter += 1
        if prof == "#Value!":
            prof_id_map[prof] = -1
    return prof_id_map

def build_student_ids(list_of_dicts):
    student_id_map = {}
    counter = 1

    for d in list_of_dicts:
        student = d.get("Student ID")

        student = student.rstrip()

        if student and student not in student_id_map:
            student_id_map[student] = counter
            counter += 1

    return student_id_map




def get_data_list_of_dicts(filename, filename2):
    listb = []
    listh = []
    with open(filename) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            listb.append(row)
    with open(filename2) as h:   
        h_csv = csv.DictReader(h)
        for row in h_csv:
            listh.append(row)
    return listb, listh

def get_room_sizes(list_of_dicts):
  room_sizes_dict = {}
  rooms = {}
  for dict in list_of_dicts:
    room = dict["Facil ID 1"]
    status = dict["Status"]
    course = dict["Course ID"]
    campus = dict["Catalog"][0]
    day_frequency = dict["Days 1"]

    if room:
        room = room.strip().upper().replace(" ", "")
    
    if status == "E" and not room == "":
      if room in room_sizes_dict:
        if course in room_sizes_dict[room]:
          room_sizes_dict[room][course] = room_sizes_dict[room][course] + 1
        else:
          room_sizes_dict[room][course] = 1
      else:
        room_sizes_dict[room] = {}
        room_sizes_dict[room][course] = 1

  room_capacities = {}
  for room in room_sizes_dict:
    capacity = 0

    for course in room_sizes_dict[room]:
      if room_sizes_dict[room][course] > capacity:
        capacity = room_sizes_dict[room][course]
    room_capacities[room] = capacity

  return room_capacities

def get_student_prefs_enrolled(list_of_dicts):
  student_prefs = {}
  for dict in list_of_dicts:
    student = dict["Student ID"]
    course = dict["Course ID"].rstrip()
    status = dict["Status"]
    room = dict["Facil ID 1"]
    if status == "E":
      if student in student_prefs:
        student_prefs[student].append(course_map[course])
      else:
        student_prefs[student] = [course_map[course]]
  return student_prefs

def convert_time(time_str):
    time, midday = time_str.split()
    hour, minutes = time.split(":")
    minutes = float(minutes)/60
    if hour == "12":
        hour = 0
    if midday == "AM":
        return (float(hour) + float(minutes))
    else:
        return (12 + float(hour) + float(minutes))


def get_courses(list_of_dicts):
  courses = {}
  for dict in list_of_dicts:
#    real_course = dict["Course ID"]
#    real_prof = dict["Instructor ID"]
    campus = dict["Catalog"][0]
    room = dict["Facil ID 1"]
    subject_unclean = dict["Subject"]
    day_freq = len(dict["Days 1"])
    if dict["Srt1 AM/PM"] != "" and dict["End 1 AMPM"] != "":
        start = convert_time(dict["Srt1 AM/PM"])
        end = convert_time(dict["End 1 AMPM"])
        time = end - start
    else:
        time = 1
    credit_hours = day_freq * time
    
    course_id = course_map[dict["Course ID"]]
    prof_id = prof_map.get(dict["Instructor ID"])
    

    if campus == "B":
        subject_map = {
            "HEBR": "BMCHebr",
            "CITY": "BMCCity",
            "ARCH": "BMCArch",
            "ITAL": "BMCItal",
            "ANTH": "BMCAnth",
            "ECON": "BMCEcon",
            "ARTT": "BMCArtT",
            "EDUC": "BMCEduc",
            "PSYC": "BMCPsyc",
            "SOCL": "BMCSocl",
            "ENGL": "BMCEngl",
            "EAST": "BMCEast",
            "FREN": "BMCFren",
            "MATH": "BMCMath",
            "POLS": "BMCPols",
            "HIST": "BMCHist",
            "SPAN": "BMCSpan",
            "BIOL": "BMCBio",
            "ARTW": "BMCArtW",
            "CMSC": "BMCCS",
            "CHEM": "BMCChem",
            "PHYS": "BMCPhys",
            "ARTF": "BMCArtF",
            "HART": "BMCHart",
            "CNSE": "BMCCnse",
            "PHIL": "BMCPhil",
            "ARTD": "BMCArtD",
            "RUSS": "BMCRuss",
            "GEOL": "BMCGeo",
            "GERM": "BMCGerm",
            "COML": "BMCComl",
            "LATN": "BMCLatn",
            "CSEM": "BMCCsem",
            "CSTS": "BMCCsts",
            "GREK": "BMCGrek",
            "GNST": "BMCGnst"
        }

    if campus == "H":
        subject_map = {
            "HEBR": "HCHebr",
            "CITY": "HCCity",
            "ARCH": "HCArch",
            "ITAL": "HCItal",
            "ANTH": "HCAnth",
            "ECON": "HCEcon",
            "ARTT": "HCArtT",
            "EDUC": "HCEduc",
            "PSYC": "HCPsyc",
            "SOCL": "HCSocl",
            "ENGL": "HCEngl",
            "EAST": "HCEast",
            "FREN": "HCFren",
            "MATH": "HCMath",
            "POLS": "HCPols",
            "HIST": "HCHist",
            "SPAN": "HCSpan",
            "BIOL": "HCBio",
            "ARTW": "HCArtW",
            "CMSC": "HCCS",
            "CHEM": "HCChem",
            "PHYS": "HCPhys",
            "ARTF": "HCArtF",
            "HART": "HCHart",
            "CNSE": "HCCnse",
            "PHIL": "HCPhil",
            "ARTD": "HCArtD",
            "RUSS": "HCRuss",
            "GEOL": "HCGeo",
            "GERM": "HCGerm",
            "COML": "HCComl",
            "LATN": "HCLatn",
            "CSEM": "HCCsem",
            "CSTS": "HCCsts",
            "GREK": "HCGrek",
            "GNST": "HCGnst"
        }
    
    subject = subject_map.get(subject_unclean, subject_unclean)

    if course_id not in courses and prof_id != '#Value!':
        courses[course_id] = {
            "course_id": course_id,
            "teacher_id": prof_id,
            "college": campus,
            "dept": subject,
            "credit_hours": int(credit_hours),
            "day_freq": day_freq

        }
  return courses

def get_building(list_of_dicts):
    buildings = {}
    rooms = {}
    i = 1
    room_id = 1
    for dict in list_of_dicts:
        room = dict["Facil ID 1"]
        campus = dict["Catalog"][0]
        prefix_to_building = {
            "TAY": "Taylor",
            "CARP": "Carpenter",
            "DAL": "Dalton",
            "PK": "Park",
            "TH": "OldLibrary",
            "EH": "EnglishHouse",
            "GOCOM": "Goodhart",
            "GO": "Goodhart",
            "GIL": "Guild",
            "ROSTUD": "RhoadsStudio",
            "PEMSTD": "PemDance",
            "RC": "RussianHouse",
            "CAN": "Canaday",
            "ARNST": "Arnecliffe",
            "RO": "Rockerfeller",        
    
            "HLS": "Hilles",
            "STOAUD": "Stokes",
            "STO": "Stokes",
            "WDS": "WoodsideCottage",
            "GST": "Gest",
            "ESTW": "KinscEastWing",
            "SHA": "Sharpless",
            "SHAAUD": "Sharpless",
            "HLL": "Hall",
            "LNKL": "Link",
            "OBS": "Observatory",
            "CHS": "Chase",
            "CHSAUD": "Chase",
            "UN": "Union",
            "MAGILLHVID": "MagillLibrary",
            "MAGILLMR": "MagillLibrary",
            "ROB": "Roberts",
            "GIACSWAN": "GIAC",
            "IRADEAREID": "IraDeAReid",
            "MARSHAUD": "Marshall",
            "BYC": "Bettys",
            "SW": "SocialWork"
        }

        building = next(
            (bldg for prefix, bldg in prefix_to_building.items() if room.startswith(prefix)),
            None
        )

        if not building:
            continue 
        
        if not room:
            continue
        if building not in buildings:
            buildings[building] = {
                "name": building,
                "id": i,
                "college": campus,
                "rooms": set()

            }
            i +=1    
        if room not in rooms:
            rooms[room] = {
                "id": room_id,
                "building_id": buildings[building]["id"],
                "capacity": room_capacities.get(room, 0)
            }
            room_id +=1

        buildings[building]["rooms"].add(rooms[room]["id"])
    for b in buildings:
        buildings[b]["rooms"] = list(buildings[b]["rooms"])
    return buildings, rooms

# Issue: didn't handle the case where a course number is corresponded to multiple courses.
def get_subject_level(list_of_dicts):
    subject_level = {}
    for dict in list_of_dicts:
        course_id = course_map[dict["Course ID"]]
        department = dict["Subject"]
        campus = dict["Catalog"][0]
        catalog = dict.get("Catalog")
        if catalog and catalog[1:].isdigit():
            level = catalog[1:]
        else:
            level = dict.get("Level")   
    
 
        if not course_id in subject_level:
            subject_level[course_id] = (department,level)
    return subject_level

def get_prof_courses(list_of_dicts):
  profs = {}
  for dict in list_of_dicts:
    prof = dict["Instructor ID"]
    course = dict["Course ID"]
    campus = dict["Catalog"][0]
    prof_id = prof_map.get(dict["Instructor ID"])
    course_id = course_map[dict["Course ID"]]

    if not prof_id == "" and prof != "#Value!":
      if prof_id in profs:
        if not course in profs[prof_id]:
          profs[prof_id].append(course_id)
      else:
        profs[prof_id] = [course_id]
  return profs

def get_class_times(list_of_dicts):
  times = []
  for dict in list_of_dicts:
    start = dict["Srt1 AM/PM"]
    end = dict["End 1 AMPM"]
    days = dict["Days 1"]
    class_time = (start, end, days)
    campus = dict["Catalog"][0]
    if not class_time in times and not start == "" \
        and not end == "" and not days == "":
      times.append(class_time)
  return times


def write_building_to_file(list_of_dicts, f):
    buildings,room = get_building(list_of_dicts)
   # f = open(filename, 'w')
    f.write("Building\t" + str(len(buildings)) + "\n")

    for building in buildings:
        f.write(str(buildings[building]["id"]) + "\t")
        f.write(buildings[building]["college"] + "\t")
        f.write(buildings[building]["name"] + "\t")
        f.write(str(len(buildings[building]["rooms"])) + "\t" + "\n")
def write_prefs_to_file(list_of_dicts, filename):
  student_prefs = get_student_prefs_enrolled(list_of_dicts)
  f = open(filename, 'w')
  f.write("Students\t" + str(len(student_prefs)) + "\n")
  for student in student_prefs:
    towrite = str(student_map[student]) + "\t"
    for course in student_prefs[student]:
      towrite = towrite + str(course) + " "
    towrite = towrite + "\n"
    f.write(towrite)

def write_class_times_to_file(list_of_dicts, f):
  class_times = get_class_times(list_of_dicts)
  f.write("Class Times\t" + "20" + "\n")
  #i = 1
  #for (start, end, days) in class_times:
   # f.write(str(i) + "\t" + start + " " + end + " " + days + "\n")
   # i = i + 1

def write_rooms_to_file(list_of_dicts, f):
  room_capacities = get_room_sizes(list_of_dicts)
  buildings,rooms = get_building(list_of_dicts)
  f.write("Rooms\t" + str(len(room_capacities)) + "\n")
  for room in room_capacities:
    f.write(str(rooms[room]["id"]) + "\t")
    f.write(str(rooms[room]["building_id"]) + "\t")
    f.write(str(rooms[room]["capacity"]) + "\t" + "\n")
def write_num_classes_to_file(list_of_dicts, f):
  num_classes = len(get_courses(list_of_dicts))
  f.write("Classes\t" + str(num_classes) + "\n")

def write_teachers_to_file(list_of_dicts, f):
  prof_courses = get_prof_courses(list_of_dicts)
  num_profs = len(prof_courses)
  courses = get_courses(list_of_dicts)
  subject_level = get_subject_level(list_of_dicts)
  building = get_building(list_of_dicts)
  f.write("Teachers\t" + str(num_profs) + "\n")
  
  for course in courses:
    f.write(str(courses[course]["course_id"]) + "\t")
    f.write(str(courses[course]["teacher_id"]) + "\t")
    f.write(courses[course]["college"] + "\t")
    f.write(courses[course]["dept"] + "\t")
    f.write(str(courses[course]["credit_hours"])+ "\t")
    f.write(str(courses[course]["day_freq"]) + "\t")
    f.write("\n")

def write_constraints_to_file(list_of_dicts, filename):
  f = open(filename, 'w')
  write_class_times_to_file(list_of_dicts, f)
  write_building_to_file(list_of_dicts, f)
  write_rooms_to_file(list_of_dicts, f)
  write_num_classes_to_file(list_of_dicts, f)
  write_teachers_to_file(list_of_dicts, f)
  f.close()



if len(sys.argv) != 5:
  print ("Usage: " + sys.argv[0] + " <bryn_mawr.csv> <haverford.csv> <student_prefs.txt> <constraints.txt>")
  exit(1)
list_of_dicts, list_of_dicts_h = get_data_list_of_dicts(sys.argv[1], sys.argv[2])
all_dicts = list_of_dicts + list_of_dicts_h

course_map = build_course_ids(all_dicts)
prof_map = build_professor_ids(all_dicts)
student_map = build_student_ids(all_dicts)
room_capacities = get_room_sizes(all_dicts)
write_prefs_to_file(all_dicts, sys.argv[3])
write_constraints_to_file(all_dicts, sys.argv[4])



