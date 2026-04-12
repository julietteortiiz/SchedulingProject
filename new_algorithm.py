#IMPORTS
import sys
from collections import OrderedDict





class College:
    def __init__(self, name):
        self.name = name
        self.buildings = {# building objects : list of departments}
class Building:
    def __init__(self, ID, name, rooms):
        self.ID = ID
        self.name = name
        self.rooms = [# room objects]
        self.dept = ""
        self.popularity = []            

    def insert_by_popularity(self, classObj):
        self.popularity.append(classObj)

class Room:
    def __init__(self, ID, capacity):
        self.ID = ID
        self.capacity = capacity
        self.schedule  [[#class objects]] # rows represent times and columns represent weekdays always 5 

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
        self.room = "" # given by dept popularity ranking
        self.days = "" # given by a room's time availability
        self.time = "" # given by a room's time availability
        self.students = [] # students who want to take this class




brynmawr = College("Bryn Mawr")
haverford = College("Haverford")
brynmawr.buildings = {carpenter: ["Econ", "Art"], }
carpenter.rooms = [213, 214, 215]






# college object has building objects assigned to 

i = -1 #for construction preference list
pref_list = []
popularity = {}
j = 0 #for constructing teacher conflict
class_teacher = [] #['class','teacher]...
cID_IID = {} #{class:teacher}
pop = {} #for compute overlap
num_of_class_times = 0
num_of_rooms = 0
num_of_classes = 0
num_of_teachers = 0
num_of_students = 0
room_sizes = []
room_slots = {}
time_slots = {}

#READ INPUTS
if len(sys.argv) < 1:
    print("Usage: algorithm.py <pref_list> <constraints> ")
    exit

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
    line_number = 0 

    buildings_section = False
    buildings_read = 0

    rooms_section = False
    rooms_read = 0

    classes_section = False
    classes_read = 0
        
    dept_to_buildings = {
    # Bryn Mawr
    "CS": ["Park"],
    "Physics": ["Park"],
    "Geology": ["Park"],
    "Math": ["Dalton"],

    # Haverford
    "Biology": ["Stokes"],
    "Chemistry": ["Stokes"],
    "Economics": ["Sharp"],
    "Psychology": ["Sharp"]
}

    
    for line in constraints_file:
        processed_line = line.split()
        if processed_line[0] == "Class" and processed_line[1] == "Times":
            num_of_class_times = int(processed_line[2])

        elif processed_line[0] == "Buildings":
            num_of_buildings = int(processed_line[1])
            buildings_section = True

        elif buildings_section = True:
            buildingID = int(processed_line[0])
            builidng_name = processed_line[2]
            buildings_room_num = int(processed_line[3])
            building = Building(buildingID, building_name, buildings_room_num)    
            match building.name:
                case "Park":
                    building.depts = ["CS", "Physics", "Geology"]
                case "Taylor": 
                    building.depts = ["Psychology"]
                case "Dalton":
                    building.depts = []
            all_buildings[buildingID] = building
            if processed_line[1] == "B":    
                brynmawr.buildings.append(building)
            else:   
                haverford.buildings.append(building)
            buildings_read += 1
            if buildings_read == num_of_buildings:
                buildings_section == False

        elif processed_line[0] == "Rooms":
            num_of_rooms = int(processed_line[1])
            room_sizes.append(0)
            rooms_section = True

        elif rooms_section == True: 

            roomID = processed_line[0]
            buildingID = processed_line[1]
            capacity = processed_line[2]
            room = Room(roomID, capacity)
            all_buildings[buildingID].rooms.append(room)

            room_sizes.append(int(processed_line[2]))
            rooms_read += 1    

            if rooms_read == num_of_rooms:
                rooms_section = False

        elif processed_line[0] == "Classes":
            num_of_classes = int(processed_line[1])
        elif processed_line[0] == "Teachers":
            num_of_teachers = int(processed_line[1])
            class_section = True
        elif class_section = True
            classID = processed_line[0]
            dept = processed_line[2]
            teacherPairID = processed_line[3]
            credit_hours = processed_line[4]
            day_frequency = processed_line[5]
            if processed_line[1] == "B":    
                college = brynmawr
            else:   
                college = haverford    
            classObj = Class(classID,college,dept, popularity[classID], teacherPairID, day_frequency, credit_hours)
                
            classObj.building = dept_to_building[dept]
            classes_read += 1
            building.insert_by_popularity(classObj)
            if classes_read == num_of_classes:  
                classes_section = False
            
 
        line_number += 1






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
def output_schedule(objects_list):
    sys.stdout.write("Course	Room	Teacher	Time	Students\n")
    for clss in objects_list:
        string = ""
        for student in clss.students:
            string = string + str(student) + " "
        output = str(clss.ID) + "\t" + str(clss.room) + "\t" + str(clss.teacherID) + "\t" + str(clss.time) + "\t" + string
        sys.stdout.write(output)
        sys.stdout.write("\n") 
            


#MAIN, FUNCTION CALLS
overlap_conflict, popularity = compute_overlap(pref_list)
divide_into_slots(overlap_conflict, teacher_conflict)
room_slots = divide_into_rooms(popularity)
objects_list = create_class_objects(room_slots, pref_list, cID_IID)
output_schedule(objects_list)

