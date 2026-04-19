# IMPORTS
import sys
from collections import OrderedDict
import math


# Objects

class College:
    def __init__(self, name):
        self.name = name
        self.buildings = {}# building objects : list of departments}
    def __str__(self):
        return self.name + " " + self.buildings
    
class Building:
    def __init__(self, ID, name, rooms):
        self.ID = ID
        self.name = name
        self.rooms = []# room objects]
        self.depts = []
        self.classes = []  
          
    def __str__(self):
        return f"{self.ID} {self.name} {self.rooms}" 
    def __repr__(self):
        return f"{self.ID} {self.name} {self.rooms}"
    def insert_by_popularity(self, classObj):
        self.popularity.append(classObj)

class Room:
    def __init__(self, ID, capacity):
        self.ID = ID
        self.capacity = capacity
        self.schedule =  [[]] # rows represent times and columns represent weekdays always 5 
        self.classes = []
    def __str__(self):
        return f"{self.ID}"
    def __repr__(self):
        return f"{self.ID} {self.capacity}"

class Class:
    def __init__(self, ID, college, dept, popularity, teacherID, day_frequency, credit_hours):

        # input data
        self.ID = ID # assigned at creation
        self.college = college # given by constraint file
        self.dept = dept
        self.popularity = popularity # calculated from student pref
        self.teacherID = teacherID # given by constraint file
        self.day_frequency = day_frequency # given by constraint file
        self.credit_hours =  credit_hours # given by constraint file

        #################

        # assigned data

        self.building = "" # decided by dept
        self.dept_popularity = -1 # set by ranking all classes within dept by popularity
        self.room = "" # given by dept popularity ranking, needs to just be id
        self.days = "" # given by a room's time availability
        self.time = "" # given by a room's time availability
        self.students = [] # students who want to take this class

    def __str__(self):
        return str(self.ID) + " " + self.dept + " " + str(self.building) + "room" + str(self.room) + " Days" + str(self.days) + " Times " + str(self.time)

class Teacher:
    def __init__(self, ID):
        self.ID = ID
        self.classes = []

class Student:
    def __init__(self, ID):
        self.ID = ID
        self.schedule = ""
        
# GLOBALS
brynmawr = College("Bryn Mawr")
haverford = College("Haverford")
class_objects = {}
building_objects = {}
room_objects = {}
teacher_objects = {}
student_objects = {}
room_sizes = []
pref_list = []
num_of_class_times = 0

if len(sys.argv) < 3:
    print("Usage: algorithm.py <pref_list> <constraints> ")
    sys.exit()

# P1: READ INPUTS

#Information in our constraints file (created from real data):
# number of class times
# number of buildings
# for each building: id, college, name, number of rooms
# number of rooms
# for each room: id, building id, capacity
# number of classes
# number of teachers
# for each class: id, teacherID, college, department, credit hours, day frequency
# NOTES FOR REAL DATA:
# 1. some classes dont have teachers assigned, teacherID = -1
# 2. some classes dont have number of days, so we don't assign time

def read_constraints():
    with open(sys.argv[2], "r") as constraints_file:
        line_number = 0 

        buildings_section = False
        buildings_read = 0

        rooms_section = False
        rooms_read = 0

        class_section = False
        classes_read = 0
        all_buildings = []
        college_building_names = {"B": [], "H": []}
 
        dept_to_buildings = {
    # Bryn Mawr
        "BMCBio": ["Park"],
        "BMCChem": ["Park"],
        "BMCGeo": ["Park"],
        "BMCMath": ["Park"],
        "BMCPhys": ["Park"],
        "BMCAstro": ["Park"],
        "BMCStats": ["Park"],
        "BMCQuant": ["Park"],
        "BMCCS": ["Park"],
        "BMCPsyc": ["Bettys", "Bettws"],
        "BMCPsych": ["Bettys", "Bettws"],
        "BMCEduc": ["Bettys", "Bettws"],
        "BMCPeace": ["Bettys", "Bettws"],
        "BMCInter": ["Bettys", "Bettws"],
        "BMCSocial": ["Dalton"],
        "BMCSocl": ["Dalton"],
        "BMCSoc": ["Dalton"],
        "BMCAnth": ["Dalton"],
        "BMCPols": ["Dalton"],
        "BMCPoli": ["Dalton"],
        "BMCEcon": ["Dalton"],
        "BMCCsts": ["Dalton"],
        "BMCGnst": ["Dalton"],
        "BMCHist": ["OldLibrary", "OldLib"],
        "BMCPhil": ["OldLibrary", "OldLib"],
        "BMCCity": ["OldLibrary", "OldLib"],
        "BMCCities": ["OldLibrary", "OldLib"],
        "BMCRelg": ["OldLibrary"],
        "BMCInde": ["OldLibrary"],
        "BMCArch": ["Carpenter"],
        "BMCHart": ["Carpenter"],
        "BMCCnse": ["Carpenter"],
        "BMCComl": ["Carpenter"],
        "BMCCsem": ["Carpenter"],
        "BMCEngl": ["EnglishHouse", "EngHouse"],
        "BMCEng": ["EnglishHouse", "EngHouse"],
        "BMCWrite": ["EnglishHouse", "EngHouse"],
        "BMCLing": ["EnglishHouse", "EngHouse"],
        "BMCRus": ["RussianHouse", "EngHouse"],
        "BMCRuss": ["RussianHouse", "EngHouse"],
        "BMCGerm": ["EnglishHouse", "EngHouse"],
        "BMCFren": ["EnglishHouse", "EngHouse"],
        "BMCSpan": ["EnglishHouse", "EngHouse"],
        "BMCItal": ["EnglishHouse", "EngHouse"],
        "BMCHebr": ["EnglishHouse", "EngHouse"],
        "BMCLatn": ["EnglishHouse", "EngHouse"],
        "BMCGrek": ["EnglishHouse", "EngHouse"],
        "BMCEast": ["EnglishHouse", "EngHouse"],
        "BMCJapan": ["EnglishHouse", "EngHouse"],
        "BMCArab": ["EnglishHouse", "EngHouse"],
        "BMCArtW": ["Goodhart"],
        "BMCArtT": ["Goodhart"],
        "BMCArtF": ["Goodhart"],
        "BMCArtD": ["Goodhart"],
        "BMCArts": ["Goodhart"],
        "BMCMusc": ["Goodhart"],
        "BMCEnv": ["Park"],
        # Haverford
        "HCBio": ["Sharpless"],
        "HCPsyc": ["Sharpless"],
        "HCPsych": ["Sharpless"],
        "HCEnv": ["Sharpless"],
        "HCChem": ["Sharpless"],
        "HCPhys": ["Hilles"],
        "HCMath": ["Hilles"],
        "HCCS": ["Hilles"],
        "HCGeo": ["Hilles"],
        "HCStats": ["Hilles"],
        "HCQuant": ["Hilles"],
        "HCAstro": ["Observatory"],
        "HCEcon": ["Chase"],
        "HCInter": ["Chase"],
        "HCPeace": ["IraDeAReid"],
        "HCHist": ["Hall"],
        "HCPols": ["Hall"],
        "HCPoli": ["Hall"],
        "HCSpan": ["Hall"],
        "HCSpanish": ["Hall"],
        "HCComl": ["Hall"],
        "HCCompLit": ["Hall"],
        "HCRelg": ["Gest"],
        "HCPhil": ["Gest"],
        "HCEngl": ["WoodsideCottage", "Woodside"],
        "HCEng": ["WoodsideCottage", "Woodside"],
        "HCWrite": ["WoodsideCottage", "Woodside"],
        "HCLing": ["WoodsideCottage", "Woodside"],
        "HCGerm": ["WoodsideCottage", "Woodside"],
        "HCFren": ["WoodsideCottage", "Woodside"],
        "HCItal": ["WoodsideCottage", "Woodside"],
        "HCEast": ["WoodsideCottage", "Woodside"],
        "HCHebr": ["WoodsideCottage", "Woodside"],
        "HCLatn": ["WoodsideCottage", "Woodside"],
        "HCGrek": ["WoodsideCottage", "Woodside"],
        "HCRuss": ["WoodsideCottage", "Woodside"],
        "HCJapan": ["WoodsideCottage", "Woodside"],
        "HCArab": ["WoodsideCottage", "Woodside"],
        "HCMusic": ["Roberts"],
        "HCAnth": ["Roberts"],
        "HCSocl": ["Roberts"],
        "HCSoc": ["Roberts"],
        "HCArtW": ["GIAC"],
        "HCArtT": ["GIAC"],
        "HCArtF": ["GIAC"],
        "HCArtD": ["GIAC"],
        "HCHart": ["Marshall"],
        "HCCnse": ["Stokes"],
        "HCArts": ["GIAC"],
        "HCMusc": ["Roberts"],
        "HCCsts": ["Union"],
        "HCGnst": ["Union"],
        "HCCity": ["Union"],
        "HCCsem": ["Union"],
        "HCArch": ["Union"],
        "HCGender": ["Union"],
        "HCHealth": ["Union"],
        "HCEduc": ["SocialWork"],
        "HCSocial": ["Union"],
        "HCInde": ["Union"],
        }        
        
        def resolve_building_name(dept, college_code):
            for building_name in dept_to_buildings.get(dept, []):
                if building_name in building_objects:
                    return building_name

            same_college_buildings = college_building_names.get(college_code, [])
            if same_college_buildings:
                return same_college_buildings[0]

            raise KeyError(f"No building mapping found for department {dept}")




        for line in constraints_file:
            processed_line = line.split()
            if processed_line[0] == "Class" and processed_line[1] == "Times":
                global num_of_class_times 
                num_of_class_times = int(processed_line[2])

            elif processed_line[0] == "Buildings":
                num_of_buildings = int(processed_line[1])
                all_buildings = [""] * (num_of_buildings + 1)
                buildings_section = True

            #for each building
            elif buildings_section == True:
                buildingID = int(processed_line[0]) #give it an ID
                building_name = processed_line[2] #get it's name
                buildings_room_num = int(processed_line[3]) #get the number of rooms in the building
                building = Building(buildingID, building_name, buildings_room_num)  #create building object
                building_objects[building.name] = building
                #seperate into buildings       
                all_buildings[buildingID] = building
                if processed_line[1] == "B":    
                    brynmawr.buildings[building] = building.depts
                else:   
                    haverford.buildings[building] = building.depts
                college_building_names[processed_line[1]].append(building.name)
                buildings_read += 1
                if buildings_read == num_of_buildings:
                    buildings_section = False

            elif processed_line[0] == "Rooms":
                num_of_rooms = int(processed_line[1])
                room_sizes.append(0)
                rooms_section = True

            elif rooms_section == True: 
                roomID = int(processed_line[0])
                buildingID = int(processed_line[1])
                capacity = int(processed_line[2])
                room = Room(roomID, capacity)
                all_buildings[buildingID].rooms.append(room) 
                room_objects[roomID] = room

                room_sizes.append(int(processed_line[2]))
                rooms_read += 1    

                if rooms_read == num_of_rooms:
                    rooms_section = False

            elif processed_line[0] == "Classes":
                num_of_classes = int(processed_line[1])
            elif processed_line[0] == "Teachers":
                num_of_teachers = int(processed_line[1])
                all_classes = [""] * (num_of_classes + 1)
                class_section = True
            elif class_section ==True:
                classID = int(processed_line[0])
                teacherID = int(processed_line[1])
                dept = processed_line[3]
                credit_hours = int(processed_line[4])
                day_frequency = int(processed_line[5])
                
                if processed_line[2] == "B":    
                    college = brynmawr
                else:   
                    college = haverford  
                    
                classObj = Class(classID,college,dept, 0, teacherID, day_frequency, credit_hours) 
                classObj.building = [resolve_building_name(dept, processed_line[2])]
                classes_read += 1
                all_classes[classID] = classObj
                
                b = building_objects.get(classObj.building[0])
                b.classes.append(classObj)
                if teacherID != -1:              
                    if teacherID not in teacher_objects:          
                        t = Teacher(teacherID)
                        teacher_objects[t.ID] = t
                        t.classes.append(classObj)
                
                    else: 
                        t = teacher_objects.get(teacherID)
                        t.classes.append(classObj)
                   
                                
                
                if classes_read == num_of_classes:  
                    class_section = False
                class_objects[classObj.ID] = classObj
                
    
        line_number += 1
        return num_of_class_times

def read_pref():
    with open(sys.argv[1], 'r') as pref_unclean:
        i = -1
        for line in pref_unclean:
            processed_line = line.split()
            if i == -1:
                i += 1  
                num_of_students = int(processed_line[1])
                continue
            pref_list.append(processed_line)
            i += 1

read_constraints()
read_pref()


# Computer Overlap finds and orders classes with the most conflict
# also keeps track of popularity
# if a pair (c1,c2) share a teacherID, their conflict score is tripled everytime it appears
# this is aimed to prioritize scheduling classes with teacher conflict 
def compute_overlap(pref_list):
    over = {}

    for student_list in pref_list:
        classes_per = min(5, (len(student_list)-1))
        sID = int(student_list[0])
        student = Student(sID)
        student_objects[sID] = student
        for i in range(1, classes_per + 1):
            current = class_objects.get(int(student_list[i]))
            current.popularity = current.popularity + 1
                
            for j in range(i+1, classes_per + 1):
                nxt = class_objects.get(int(student_list[j]))
                pair = (min(current.ID, nxt.ID), max(current.ID, nxt.ID))
              
                if pair in over:
                    over[pair] = over[pair] + 1
                    if current.teacherID == nxt.teacherID:
                        over[pair] = over[pair] * 3
                else:
                    over[pair] = 1
                    if current.teacherID != -1 and current.teacherID == nxt.teacherID:
                        over[pair] = over[pair] * 3
                    
    overlap = OrderedDict(sorted(over.items(), key=lambda item: item[1], reverse=True))
    return overlap
 
# Assign all classes to a room in their building based of their
# popularity score compared to other classes in that building
def assign_rooms(Buildings):
        
    for name, building in Buildings.items():  
        if building.classes == [] or building.rooms == []:
            continue        
        sorted_classes = sorted(building.classes, key=lambda x:x.popularity, reverse = True)
        sorted_rooms = sorted(building.rooms, key=lambda x: x.capacity, reverse = True)
        num_classes = len(sorted_classes)
        num_rooms  = len(sorted_rooms)

        #1. len(classes) >= len(rooms) -> each room gets assigned 0 or 1 class, prioritize assigning larger rooms
        if num_classes == num_rooms or num_classes < num_rooms:
            for i in range(num_classes):
                current = sorted_classes[i]
                current.room = sorted_rooms[i]
                sorted_rooms[i].classes.append(current)

        #2. len(classes) > len(rooms) -> each room gets assigned multiple classes, prioritize larger rooms
        if num_classes > num_rooms:
            classes_per_room_max = math.ceil(num_classes/num_rooms)
            classes_per_room_min = math.floor(num_classes/num_rooms)
            num_rooms_min_classes = (num_rooms * classes_per_room_max) - num_classes
            num_rooms_max_classes = num_rooms - num_rooms_min_classes
            #first loop: we know that num of rooms that will recieve the greater number of classes
            # for each i room, assign j number of classes
            for i in range(num_rooms_max_classes):
                for j in range(classes_per_room_max):
                    current_class = sorted_classes[0]
                    current_class.room = sorted_rooms[i]
                    sorted_rooms[i].classes.append(current_class)
                    del sorted_classes[0]

            for _ in range(num_rooms_max_classes):
                del sorted_rooms[0]

            for a in range(num_rooms_min_classes):
                for b in range(classes_per_room_min):
                    current_class = sorted_classes[0]
                    current_class.room = sorted_rooms[a]
                    sorted_rooms[a].classes.append(current_class)
                    del sorted_classes[0]

# ASSIGN TIME FUNCTIONS _______________________________________

# Initialize data structures which will allow us to keep track of conflict when 
# assigning times
rows, cols = (num_of_class_times+ 2), 5
time_matrix = [[set() for _ in range(cols)] for _ in range(rows)] #track teacher conflict
room_matrix = [[set() for _ in range(5)] for _ in range(num_of_class_times)] #track room conflict

# key = day frequency
# value = different combinations of days we consider for scheduling
DAYS = {
    5: [[0, 1, 2, 3, 4]],
    4: [[0, 1, 3, 4]],
    3: ([0, 2, 4], [1, 3, 4]),
    2: ([0, 2], [1, 3], [2, 4], [1, 4], [0, 3]),
    1: ([0], [1], [2], [3], [4])
} 

# 1. Given a class, search for all available times on the first day of a possible combination
# Idea: If not available time on first day of a day combination, then that combo 
# can be dumped
def find_time(time_slots, teacher_id, room_id, blocked_times, j):
    valid_times = []
    for i in range(num_of_class_times - time_slots + 1):
        valid = True
        end_time = i

        if blocked_times is not None and i in blocked_times:
            valid = False
        if teacher_id != -1 and teacher_id in time_matrix[i][j]:
            valid = False
        if room_id in room_matrix[i][j]:
            valid = False
        if not valid:
            continue

        for a in range(1, time_slots):
            q = a + i
            if blocked_times is not None and q in blocked_times:
                valid = False
            if teacher_id != -1 and teacher_id in time_matrix[q][j]:
                valid = False
            if room_id in room_matrix[q][j]:
                valid = False

            if not valid:
                break

            end_time = q

        if valid and ((end_time - i) + 1) == time_slots:
            valid_times.append((i, end_time))

    return valid_times if valid_times else None 

#2. Given a time, check that there's no teacher and room conflict for all days in combination
# Idea: given a time from find_time(), we can check that it's valid for a class for all days      
def check_time(start_time, end_time, time_slots, j_range, teacher_id, room_id, blocked_times):
    for j in j_range:
        for i in range(start_time, end_time + 1):
            if blocked_times is not None and i in blocked_times:
                return False
            if teacher_id != -1 and teacher_id in time_matrix[i][j]:
                return False
            if room_id in room_matrix[i][j]:
                return False
    return True

#3. For an overlap pair, if we have the time of one class get the range of time slots 
# we don't want the second class to be scheduled in
def blocked_time_range(conflict_time):
    if conflict_time in (None, ""):
        return None
    return set(range(conflict_time[0], conflict_time[1] + 1))
               
#4. Given a class, we identify
#    a. teacher conflict
#    b. room conflict
#    c. overlapping pair conflict time
#    d. all possible day combinations given the day frequency
# Then we call find_time and check_time until we can return a valid time/days for our class                  
def get_time(class_object, time_slots, day_frequency, class_conflict):
    teacher_id = class_object.teacherID
    room_id = class_object.room.ID
    s_con = blocked_time_range(class_conflict)
    a = DAYS.get(min(5, day_frequency))
    for combo in a:
        j = combo[0]
        times = find_time(time_slots, teacher_id, room_id, s_con, j)
        if times is None:
            continue
        for time in times:
            if check_time(time[0], time[1], time_slots, combo[1:], teacher_id, room_id, s_con):
                return time, combo
    return None

# Use update matrix to track where classes are being scheduled
# update both our time matrix and room matrix to track conflict   
def update_matrix(class_object, time, days):
    for day in days:
        for i in range(time[0], time[1]+1):
            time_matrix[i][day].add(class_object.teacherID)  
            room_matrix[i][day].add(class_object.room.ID)
 
# Assign class to a different room if no time can be found
# Called from assign_class_time()        
def place_class_in_room(class_object, room):
    if class_object.room not in ("", None):
        class_object.room.classes = [c for c in class_object.room.classes if c.ID != class_object.ID]

    class_object.room = room
    if all(existing.ID != class_object.ID for existing in room.classes):
        room.classes.append(class_object)

# Function where we troubleshoot cases where
# a. no day frequency
# b. if no time can be found: reassign class to different room in same building and recheck
# c. if time still can't be found: find a room in the same college and try assigning to room with least number of 
# classes assigned to it
def assign_class_time(class_object, conflict_time):
    if class_object.day_frequency == 0:
        # print(f"WARNING: class {class_object.ID} has day_frequency 0, skipping")
         return
    
    time_slots = max(1, math.ceil((class_object.credit_hours / class_object.day_frequency) * 2))
    assignment = get_time(class_object, time_slots, class_object.day_frequency, conflict_time)
    if assignment is None and conflict_time is not None:
        assignment = get_time(class_object, time_slots, class_object.day_frequency, None)

    original_room = class_object.room

    if assignment is None:
        b = building_objects.get(class_object.building[0])
        for room in b.rooms:
            if room.ID == original_room.ID:
                continue
            place_class_in_room(class_object, room)
            assignment = get_time(class_object, time_slots, class_object.day_frequency, None)
            if assignment is not None:
                break
    
    if assignment is None:
        college = class_object.college
        all_rooms = []
        for bldg in building_objects.values():
            for room in bldg.rooms:
                if room.ID == original_room.ID:
                    continue
                same_college = bldg in college.buildings
                all_rooms.append((room, same_college))
        
        all_rooms.sort(key=lambda x: (0 if x[1] else 1, len(x[0].classes)))
        
        for room, _ in all_rooms:
            place_class_in_room(class_object, room)
            assignment = get_time(class_object, time_slots, class_object.day_frequency, None)
            if assignment is not None:
                break

    if assignment is None:
        print(f"ERROR: No valid time found for class {class_object.ID}, skipping")
        return

    class_time, class_days = assignment
    class_object.time = class_time
    class_object.days = class_days
    update_matrix(class_object, class_time, class_days)

# Core function where we go through every conflict pair from computer_overlap()   
def assign_times(overlap_pairs):
    for pair in overlap_pairs:
        class1 = class_objects[pair[0]]
        class2 = class_objects[pair[1]]
        if class1.time == "" and class2.time == "":
            assign_class_time(class1, None)
            assign_class_time(class2, class1.time)
            
        if class1.time == "" and class2.time != "":
            assign_class_time(class1, class2.time)
             
        if class1.time != "" and class2.time == "":
            assign_class_time(class2, class1.time)

    for class_object in class_objects.values():
        if class_object.time == "":
            assign_class_time(class_object, None)  

# END TIME FUNCTIONS ______________________________________________________________   
def output_schedule(objects_list, stream=None):
    if stream is None:
        stream = sys.stdout

    stream.write("Course\tRoom\tTeacher\tTime\tDays\tStudents\n")

    dic = {0: 'M', 1: 'T', 2: 'W', 3: 'TH', 4: 'F'}
    for i, clss in objects_list.items():
        # Skip courses that never received a complete assignment.
        if clss.room in ("", None) or clss.time in ("", None) or clss.days in ("", None):
            continue

        student_text = " ".join(str(student) for student in clss.students)
        days = ""
        for d in clss.days:
            days = days + dic.get(d)
        row = "\t".join(
            [
                str(clss.ID),
                str(clss.room.ID),
                str(clss.teacherID if clss.teacherID != -1 else "NA"),
                str(clss.time),
                str(days),
                student_text,
            ]
        )
        stream.write(row)
        stream.write("\n")
        
def assign_students(pref_list):
    couldnt_enroll_count = 0
    successful_classes = 0
    for list in pref_list:
        s = student_objects.get(int(list[0])) 
        s.schedule = [[0 for _ in range(5)] for _ in range(num_of_class_times)]

        # For each class in the preference list
        for i in range(1,min(5, len(list))):
            c = class_objects.get(int(list[i]))
            if not c or c.time == "":
                continue
            start = c.time[0]
            end = c.time[1]
            slots = range(start, end + 1)
            days = c.days
            enroll = True
            
            # check for conflict
            for a in days:
                for b in slots:
                    if s.schedule[b][a] != 0:
                        enroll = False
                        break
            
            if enroll == True:
                if len(c.students) >= c.room.capacity:
                    couldnt_enroll_count += 1
                    continue

                for m in days:
                    for n in slots:
                        s.schedule[n][m] = 1            
                c.students.append(s.ID)
                successful_classes += 1
            else:
                couldnt_enroll_count += 1

    print("Couldn't enroll:" + str(couldnt_enroll_count))
    print("Successful enrollements:" + str(successful_classes))

def check_teacher_conflict(): 
    for i, t in teacher_objects.items():
        s = [[0 for _ in range(5)] for _ in range(num_of_class_times)] 
        for c in t.classes:
            if not c or c.time == "":
                continue
            start = c.time[0]
            end = c.time[1]
            slots = range(start, end + 1)
            days = c.days
            enroll = True
            
            #check for conflict
            for a in days:
                for b in slots:
                    if s[b][a] != 0:
                        enroll == False
                        print("Teacher conflict" + str(t.ID))  
                        s[b][a] = -333                                                           
            
            if enroll == True:
                for m in days:
                    for n in slots:
                        s[n][m] = 1   

                               
                      
# MAIN
overlap_conflict = compute_overlap(pref_list)
assign_rooms(building_objects)
assign_times(overlap_conflict)
assign_students(pref_list)
output_schedule(class_objects)
check_teacher_conflict()
