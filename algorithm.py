#IMPORTS
import sys
from collections import OrderedDict

# NOTES:
# 1. Need to adjust code for different sized INPUTS
# 2. is there a way to get rid of globals?
# 3. I think code will look better and be more easily updated for real data if we avoid global 
# variables and global data structures
# 4. I think some data structures can be rid of if we create the class objects sooner an just directly update 
# certain values like teacher ID. 

#DATA STRUCTURES AND GLOBAL VARIABLES
class Class:
    def __init__(self, ID, teacherID, time, room):
        self.ID = ID
        self.teacherID = teacherID
        self.time = time
        self.room =  room
        self.students = []

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

with open(sys.argv[2], "r") as constraints_file:
    line_number = 0
    reading_rooms = False
    rooms_read = 0
    for line in constraints_file:
        processed_line = line.split()
        if line_number == 0:
            num_of_class_times = int(processed_line[2])
        elif line_number == 1:
            num_of_rooms = int(processed_line[1])
            room_sizes.append(0)
            reading_rooms = True

        elif reading_rooms == True: 
            room_sizes.append(int(processed_line[1]))
            rooms_read += 1    

            if rooms_read == num_of_rooms:
                reading_rooms = False
        elif processed_line[0] == "Classes":
            num_of_classes = int(processed_line[1])
        elif processed_line[0] == "Teachers":
            num_of_teachers = int(processed_line[1])
            for line in constraints_file:
                class_teacher.append(line.split())
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

