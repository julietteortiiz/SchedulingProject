#IMPORTS
import sys
from collections import OrderedDict





class College:
    def __init__(self, name):
        self.name = name
        self.buildings = []
class Building:
    def __init__(self, ID, name, rooms=None):
        self.ID = ID
        self.name = name
        self.rooms = rooms if rooms is not None else []
        self.dept = ""
        self.popularity = []            

    def insert_by_popularity(self, classObj):
        self.popularity.append(classObj)

class Room:
    def __init__(self, ID, capacity):
        self.ID = ID
        self.capacity = capacity
        self.schedule = []

class Class:
    def __init__(self, ID, *args):
        self.ID = int(ID)
        self.building = ""
        self.dept_popularity = -1
        self.room = ""
        self.days = ""
        self.time = ""
        self.students = []

        if len(args) == 3:
            teacherID, time, room = args
            self.college = None
            self.dept = ""
            self.popularity = 0
            self.teacherID = int(teacherID)
            self.day_frequency = 0
            self.credit_hours = 0
            self.time = int(time)
            self.room = int(room)
        elif len(args) == 6:
            college, dept, popularity, teacherID, day_frequency, credit_hours = args
            self.college = college
            self.dept = dept
            self.popularity = popularity
            self.teacherID = int(teacherID)
            self.day_frequency = int(day_frequency)
            self.credit_hours = int(credit_hours)
        else:
            raise ValueError("Class expects either 4 total args or 7 total args.")




brynmawr = College("Bryn Mawr")
haverford = College("Haverford")






# college object has building objects assigned to 

i = -1 #for construction preference list
pref_list = []
popularity = {}
j = 0 #for constructing teacher conflict
class_teacher = [] #['class','teacher]...
cID_IID = {} #{class:teacher}
pop = {} #for compute overlap
all_buildings = {}
num_of_class_times = 0
num_of_rooms = 0
num_of_classes = 0
num_of_teachers = 0
num_of_students = 0
room_sizes = []
room_slots = {}
time_slots = {}

#READ INPUTS
if len(sys.argv) < 3:
    print("Usage: new_algorithm.py <pref_list> <constraints>")
    sys.exit(1)

with open(sys.argv[1], 'r') as pref_unclean:
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




with open(sys.argv[2], "r") as constraints_file:
    buildings_section = False
    buildings_read = 0

    rooms_section = False
    rooms_read = 0

    classes_read = 0
    class_section = False

    for line in constraints_file:
        processed_line = line.split()
        if not processed_line or processed_line[0].startswith("#"):
            continue

        if processed_line[0] == "Class" and processed_line[1] == "Times":
            num_of_class_times = int(processed_line[2])
            continue

        if processed_line[0] == "Buildings":
            num_of_buildings = int(processed_line[1])
            buildings_section = True
            rooms_section = False
            class_section = False
            continue

        if processed_line[0] == "Rooms":
            num_of_rooms = int(processed_line[1])
            room_sizes.append(0)
            rooms_section = True
            buildings_section = False
            class_section = False
            continue

        if processed_line[0] == "Classes":
            num_of_classes = int(processed_line[1])
            continue

        if processed_line[0] == "Teachers":
            num_of_teachers = int(processed_line[1])
            class_section = True
            buildings_section = False
            rooms_section = False
            continue

        if buildings_section and buildings_read < num_of_buildings:
            buildingID = int(processed_line[0])
            college_code = processed_line[1]
            building_name = processed_line[2]
            building = Building(buildingID, building_name, [])
            all_buildings[buildingID] = building
            if college_code == "B":
                brynmawr.buildings.append(building)
            else:
                haverford.buildings.append(building)
            buildings_read += 1
            if buildings_read == num_of_buildings:
                buildings_section = False
            continue

        if rooms_section and rooms_read < num_of_rooms:
            roomID = processed_line[0]
            buildingID = int(processed_line[1])
            capacity = int(processed_line[2])
            room = Room(roomID, capacity)
            if buildingID in all_buildings:
                all_buildings[buildingID].rooms.append(room)
            room_sizes.append(capacity)
            rooms_read += 1
            if rooms_read == num_of_rooms:
                rooms_section = False
            continue

        if class_section and classes_read < num_of_classes:
            classID = int(processed_line[0])
            dept = processed_line[2]
            pairedClassID = int(processed_line[3])
            credit_hours = processed_line[4]
            day_frequency = processed_line[5]
            teacherID = min(classID, pairedClassID)
            class_teacher.append([classID, teacherID])
            cID_IID[classID] = teacherID
            classes_read += 1
            continue






#FUNCTIONS

#create time slots
for time in range (1, num_of_class_times+1):
    time_slots[time] = []

#create room slots
for room in range (1, num_of_rooms+1):
    room_slots[room] = []


#create teacher conflict
teacher_conflict = [0] * (num_of_classes + 1)
for a in class_teacher:
    tchr1 = int(a[1])
    cID_IID[int(a[0])] = tchr1
    for b in class_teacher:
        tchr2 = int(b[1])
        if tchr1 == tchr2 and a[0] != b[0]:
            teacher_conflict[int(a[0])] = int(b[0])
            teacher_conflict[int(b[0])] = int(a[0])



#Assign classes to time slots
# Notes: I think this is going to create issues if there ends up not being any available slots
def divide_into_slots(overlap_conflict, teacher_conflict):

    for clss in overlap_conflict:
        if all(clss[0] not in slot for slot in time_slots.values()):
            for key in time_slots:
                if clss[1] not in time_slots[key] and teacher_conflict[clss[0]] not in time_slots[key] and len(time_slots[key]) < num_of_rooms:
                    time_slots[key].append(clss[0])
                    break
    
        if all(clss[1] not in slot for slot in time_slots.values()):
            for key in time_slots:
                if clss[0] not in time_slots[key] and teacher_conflict[clss[1]] not in time_slots[key] and len(time_slots[key]) < num_of_rooms:
                    time_slots[key].append(clss[1])
                    break
    # if a class wasn't scheduled, schedule it in a an empty slot
    all_classes = set(range(1, num_of_classes + 1))
    scheduled = set()
    for slot in time_slots.values():
        scheduled.update(slot)
    missing = all_classes - scheduled

    for clss in missing:
        placed = False
        for key in time_slots:
            if len(time_slots[key]) < num_of_rooms:
                time_slots[key].append(clss)
                placed = True
                break



#Take classes (now in times slots) and assign them rooms based on popularity
def divide_into_rooms(popularity):
    room_lst = {}

    sorted_rooms = sorted(range(1, len(room_sizes)), key=lambda r: room_sizes[r], reverse=True)

    for t in time_slots:
        classes = time_slots[t]

        sorted_classes = sorted(classes, key=lambda c: popularity.get(c, 0), reverse=True)

        room_lst[t] = {}

        for i in range(len(sorted_classes)):
            r = sorted_rooms[i]
            cls = sorted_classes[i]
            room_lst[t][r] = cls

    return room_lst

#Take the scheduled classes and the preference lists and create all the class objects
#created a dictionary to easily fetch the teacher id for each class
def create_class_objects(room_slots, pref_list, cID_IID):
    objects = []
    for time, pair in room_slots.items():
        for room, clss in pair.items():
            name = "class" + str(clss)
            teacherID = cID_IID[clss]
            temp = Class(clss,teacherID,time, room)
            temp.capacity = room_sizes[room]
            temp.students = []
            name = temp
            objects.append(name)
    sorted_objects = sorted(objects, key=lambda x: x.ID)
    couldnt_enroll_count = 0
    for list in pref_list:
        studentID = int(list[0])
        times_enrolled = [0] * num_of_class_times
        for i in range(1,5):
            clssID = int(list[i])
            class_Class = sorted_objects[clssID-1]
            #for each class on pref list check that student is available
            #at that time, else don't enroll them and count
             
            if times_enrolled[class_Class.time-1] == 0 and len(class_Class.students) < class_Class.capacity:
                times_enrolled[class_Class.time-1] = 1
                class_Class.students.append(studentID)
            else:
                couldnt_enroll_count = couldnt_enroll_count + 1
    
    #This is line for checking optimality
    #print("Couldnt enroll " + str(couldnt_enroll_count))
    #opt = ((num_of_students * 4) - couldnt_enroll_count) / (num_of_students * 4)
    #print("Opt " + str(opt))
    return sorted_objects

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
                str(clss.room),
                str(clss.teacherID),
                str(clss.time),
                student_text,
            ]
        )
        stream.write(row)
        stream.write("\n")
            


#MAIN, FUNCTION CALLS
overlap_conflict, popularity = compute_overlap(pref_list)
divide_into_slots(overlap_conflict, teacher_conflict)
room_slots = divide_into_rooms(popularity)
objects_list = create_class_objects(room_slots, pref_list, cID_IID)
output_schedule(objects_list)
