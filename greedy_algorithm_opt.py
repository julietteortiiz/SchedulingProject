# IMPORTS
import sys
from collections import OrderedDict
import math



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
        return f" Room {self.ID}"
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
        return str(self.ID) + " " + self.dept + " " + str(self.building) + str(self.room) + " Days" + str(self.days) + " Times " + str(self.time)

#GLOBALS
brynmawr = College("Bryn Mawr")
haverford = College("Haverford")
class_objects = {}
building_objects = {}
room_objects = []



#READ INPUTS
if len(sys.argv) < 1:
    print("Usage: algorithm.py <pref_list> <constraints> ")
    exit

pref_list = []
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

#create the overlap dictionary and the list of classes based off popularity
def compute_overlap(pref_list):
    over = {}
    pop = {} #for compute overlap

    for student_list in pref_list:
        for i in range(1, 5):
            current = int(student_list[i])
            if current in pop:
                pop[current] += 1
            else:
                pop[current] = 1
            for j in range(i+1, 5):
                nxt = int(student_list[j])
                pair = (min(current, nxt), max(current, nxt))


                if pair in over:
                    over[pair] = over[pair] + 1
                else:
                    over[pair] = 1
    overlap = OrderedDict(sorted(over.items(), key=lambda item: item[1], reverse=True))
    popularity = dict(sorted(pop.items(), key=lambda item: item[1], reverse=True))
    return overlap, popularity


overlap_conflict, popularity = compute_overlap(pref_list)
room_sizes = []
num_of_class_times = 0

with open(sys.argv[2], "r") as constraints_file:
    line_number = 0 

    buildings_section = False
    buildings_read = 0

    rooms_section = False
    rooms_read = 0

    class_section = False
    classes_read = 0
    all_buildings = []
 
    dept_to_buildings = {
    # Bryn Mawr majors
    "BMCBio": ["Park"],
    "BMCChem": ["Park"],
    "BMCGeo": ["Park"],
    "BMCMath": ["Park"],
    "BMCPhys": ["Park"],
    "BMCPsych": ["Bettws"],
    "BMCEduc": ["Bettws"],
    "BMCCS": ["Park"],
    "BMCHist": ["OldLib"],
    "BMCPhil": ["OldLib"],
    "BMCCities": ["OldLib"],
    "BMCSoc": ["Dalton"],
    "BMCAnth": ["Dalton"],
    "BMCPoli": ["Dalton"],
    "BMCEcon": ["Dalton"],
    "BMCClass": ["Carpenter"],
    "BMCArch": ["Carpenter"],
    "BMCArtHist": ["Carpenter"],
    "BMCEng": ["EngHouse"],
    "BMCRus": ["EngHouse"],
    "BMCMusic": ["Goodhart"],
    "BMCTheater": ["Goodhart"],
    "BMCArts": ["Goodhart"],
    # Haverford majors
    "HCBio": ["Sharpless"],
    "HCPsych": ["Sharpless"],
    "HCChem": ["KINSC"],
    "HCPhys": ["KINSC"],
    "HCAstro": ["KINSC"],
    "HCMath": ["Hilles"],
    "HCCS": ["Hilles"],
    "HCEcon": ["Chase"],
    "HCLing": ["Chase"],
    "HCHist": ["Hall"],
    "HCPoli": ["Hall"],
    "HCSpanish": ["Hall"],
    "HCCompLit": ["Hall"],
    "HCEng": ["Woodside"],
    "HCMusic": ["Roberts"],
    "HCAnth": ["Roberts"],
    "HCSoc": ["Roberts"],
    "HCRel": ["Roberts"],
    "HCAfr": ["Union"],
    "HCGender": ["Union"],
    "HCHealth": ["Union"],
}

    for line in constraints_file:
        processed_line = line.split()
        if processed_line[0] == "Class" and processed_line[1] == "Times":
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
            room_objects.append(room)

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
            teacherPairID = int(processed_line[1])
            dept = processed_line[3]
            credit_hours = int(processed_line[4])
            day_frequency = int(processed_line[5])
            
            if processed_line[2] == "B":    
                college = brynmawr
            else:   
                college = haverford  
                  
            classObj = Class(classID,college,dept, popularity.get(classID, 0), teacherPairID, day_frequency, credit_hours) 
            classObj.building = dept_to_buildings[dept]
            classes_read += 1
            all_classes[classID] = classObj
            b = building_objects.get(classObj.building[0])
            b.classes.append(classObj)
          
            
            if classes_read == num_of_classes:  
                class_section = False
            class_objects[classObj.ID] = classObj
            
 
    line_number += 1



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

rows, cols = num_of_class_times, 5
time_matrix = [[set() for _ in range(cols)] for _ in range(rows)]

def find_time(time_slots, teacher_conflict, room_conflict, blocked_times, j):
    valid_times = []
    for i in range(num_of_class_times - time_slots + 1):
        # Check first slot
        if teacher_conflict in time_matrix[i][j] or \
            any(rc in time_matrix[i][j] for rc in room_conflict) or \
                (blocked_times is not None and i in blocked_times):
            continue
        
        end_time = i 
        valid = True
        for a in range(1, time_slots):
            if teacher_conflict in time_matrix[i + a][j] or \
                any(rc in time_matrix[i + a][j] for rc in room_conflict) or \
                    (blocked_times is not None and (i + a) in blocked_times):
                valid = False
                break
            else:
                end_time = i + a

        if valid and ((end_time - i) + 1) == time_slots:
            valid_times.append((i, end_time))
                
    return valid_times if valid_times else None

def check_time(start_time, end_time, time_slots, j_range, t_conflict, r_conflict, blocked_times):
    for day in j_range:
        for k in range(time_slots):
           if t_conflict in time_matrix[start_time + k][day] or \
               any(rc in time_matrix[start_time + k][day] for rc in r_conflict) or \
                   (blocked_times is not None and (start_time + k) in blocked_times):
                       return False
    return True

def blocked_time_range(conflict_time):
    if conflict_time in (None, ""):
        return None
    return set(range(conflict_time[0], conflict_time[1] + 1))
                    
def five_per_week(class_object, time_slots_per_day, teacher_conflict, room_conflict, class_conflict):
    a = [0, 1, 2, 3, 4] #M, T, W, TH, F
    #Returns a list of valid times found on Monday
    times = find_time(time_slots_per_day, teacher_conflict, room_conflict, class_conflict, 0)  
    if times == None:
        return None 
    #Checks each time across all other days until valid time accross all days is found   
    for time in times:
        if check_time(time[0], time[1], time_slots_per_day, a[1:], teacher_conflict, room_conflict, class_conflict) == True:
            return time, a 
    #Returns no time if there is no valid time
    return None         
                     
def three_per_week(class_object, time_slots_per_day, teacher_conflict, room_conflict, class_conflict):
    a = [[0, 2, 4], [1, 3, 4]] 
    for combo in a:
        j = combo[0]
        times = find_time(time_slots_per_day, teacher_conflict, room_conflict, class_conflict, j)  
        if times == None:
            return None 
        for time in times:
            if check_time(time[0], time[1], time_slots_per_day, combo[1:], teacher_conflict, room_conflict, class_conflict) == True:
                return time, combo       
    return None   

def two_per_week(class_object, time_slots_per_day, teacher_conflict, room_conflict, class_conflict):
    a = [[0, 2], [1, 3], [2, 4], [1, 4], [0, 3]]
    for combo in a:
        j = combo[0]
        times = find_time(time_slots_per_day, teacher_conflict, room_conflict, class_conflict, j)  
        if times == None:
            return None 
        for time in times:
            if check_time(time[0], time[1], time_slots_per_day, combo[1:], teacher_conflict, room_conflict, class_conflict) == True:
                return time, combo        
    return None  

def four_per_week(class_object, time_slots_per_day, teacher_conflict, room_conflict, class_conflict):
    a = [0, 1, 3, 4]
    times = find_time(time_slots_per_day, teacher_conflict, room_conflict, class_conflict, 0)  
    if times == None:
        return None 
    for time in times:
        if check_time(time[0], time[1], time_slots_per_day, a[1:], teacher_conflict, room_conflict, class_conflict) == True:
            return time, a       
    return None

def one_per_week(class_object, time_slots_per_day, teacher_conflict, room_conflict, class_conflict):
    a = [[0], [1], [2], [3], [4]]
    for combo in a:
        j = combo[0]
        times = find_time(time_slots_per_day, teacher_conflict, room_conflict, class_conflict, j)  
        if times == None:
            return None 
        for time in times:
            if check_time(time[0], time[1], time_slots_per_day, combo[1:], teacher_conflict, room_conflict, class_conflict) == True:
                return time, combo        
    return None

def get_time(class_object, time_slots, day_frequency, c_conflict):
    t_conflict = class_object.teacherID
    r_conflict = [c.ID for c in class_object.room.classes if c.ID != class_object.ID]
    blocked_times = blocked_time_range(c_conflict)
    
    if day_frequency == 5:
        return five_per_week(class_object, time_slots, t_conflict, r_conflict, blocked_times)
    if day_frequency == 4:
        return four_per_week(class_object, time_slots, t_conflict, r_conflict, blocked_times)
    if day_frequency == 3:
        return three_per_week(class_object, time_slots, t_conflict, r_conflict, blocked_times)
    if day_frequency == 2:
        return two_per_week(class_object, time_slots, t_conflict, r_conflict, blocked_times)
    if day_frequency == 1:
        return one_per_week(class_object, time_slots, t_conflict, r_conflict, blocked_times)

def update_matrix(class_object, time, days):
    for day in days:
        for i in range(time[0], time[1]+1):
            time_matrix[i][day].add(class_object.ID)


def place_class_in_room(class_object, room):
    if class_object.room not in ("", None):
        class_object.room.classes = [c for c in class_object.room.classes if c.ID != class_object.ID]

    class_object.room = room
    if all(existing.ID != class_object.ID for existing in room.classes):
        room.classes.append(class_object)


def default_days_for_frequency(day_frequency):
    if day_frequency == 5:
        return [0, 1, 2, 3, 4]
    if day_frequency == 4:
        return [0, 1, 3, 4]
    if day_frequency == 3:
        return [0, 2, 4]
    if day_frequency == 2:
        return [0, 2]
    return [0]


def fallback_assignment(time_slots, day_frequency):
    end_time = min(num_of_class_times - 1, time_slots - 1)
    return (0, end_time), default_days_for_frequency(day_frequency)

def assign_class_time(class_object, conflict_time):
    time_slots = max(1, math.ceil((class_object.credit_hours / class_object.day_frequency) * 2))
    assignment = get_time(class_object, time_slots, class_object.day_frequency, conflict_time)
    if assignment is None:
        assignment = get_time(class_object, time_slots, class_object.day_frequency, None)

    original_room = class_object.room

    if assignment is None:
        for room in room_objects:
            if room.ID == original_room.ID:
                continue
            place_class_in_room(class_object, room)
            assignment = get_time(class_object, time_slots, class_object.day_frequency, None)
            if assignment is not None:
                break

    if assignment is None:
        fallback_room = class_object.room if class_object.room not in ("", None) else original_room
        if fallback_room in ("", None):
            fallback_room = room_objects[0]
        place_class_in_room(class_object, fallback_room)
        assignment = fallback_assignment(time_slots, class_object.day_frequency)

    class_time, class_days = assignment
    class_object.time = class_time
    class_object.days = class_days
    update_matrix(class_object, class_time, class_days)
    
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

#Write output to stdout, in makefile this will create our_schedule.txt        
def output_schedule(objects_list, stream=None):
    if stream is None:
        stream = sys.stdout

    stream.write("Course\tRoom\tTeacher\tTime\tStudents\n")

    ordered_classes = sorted(objects_list, key=lambda clss: int(clss.ID))

    for clss in ordered_classes:
        student_text = " ".join(str(student) for student in clss.students)
        row = "\t".join(
            [
                str(clss.ID),
                str(clss.room.ID),
                str(clss.teacherID),
                str(clss.time[0]),
                student_text,
            ]
        )
        stream.write(row)
        stream.write("\n")
        
def assign_students(pref_list):
    sorted_objects = sorted(class_objects.values(), key=lambda x: int(x.ID))
    couldnt_enroll_count = 0
    for list in pref_list:
        studentID = int(list[0])
        times_enrolled = [0] * num_of_class_times
        for i in range(1,5):
            clssID = int(list[i])
            class_Class = sorted_objects[clssID-1]
            #for each class on pref list check that student is available
            #at that time, else don't enroll them and count
            start = class_Class.time[0]
            end = class_Class.time[1]
            slots = range(start, end + 1)
            if all(times_enrolled[slot] == 0 for slot in slots) and len(class_Class.students) < class_Class.room.capacity:
                for slot in slots:
                    times_enrolled[slot] = 1
                class_Class.students.append(studentID)
            else:
                couldnt_enroll_count = couldnt_enroll_count + 1
    
    #This is line for checking optimality
    print("Couldnt enroll " + str(couldnt_enroll_count))
    opt = ((num_of_students * 4) - couldnt_enroll_count) / (num_of_students * 4)
    print("Fit percentage: " + str(opt))
    return sorted_objects
        
#MAIN
assign_rooms(building_objects)
assign_times(overlap_conflict)
assign_students(pref_list)
del all_classes[0]
output_schedule(all_classes)
