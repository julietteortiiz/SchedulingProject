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
teacher_conflict = [0] * 15 #[0,10,4,...] says 10 conflicts with 1, 4 conflicts with 2
class_teacher = [] #['class','teacher]...
cID_IID = {} #{class:teacher}
pop = {} #for compute overlap
time_slots = {}
times = 4
room_slots = {}
rooms = 4
room_sizes = [0, 84, 89, 18, 59]



#READ INPUTS
pref_file = ""
if len(sys.argv) > 1:
    pref_file = sys.argv[1]
    
else:
    print("Usage: algorithm.py <pref_list> <constraints> <data>")


with open(pref_file, 'r') as pref_unclean:
    for line in pref_unclean:
        if i == -1:
            i += 1  
            continue
        pref_list.append(line.split())
        i += 1

with open(sys.argv[2], "r") as contraints_file:
    for line in contraints_file:
        if j < 8:
            j +=1
            continue
        class_teacher.append(line.split())


#FUNCTIONS

#create time slots
for time in range (1, times+1):
    time_slots[time] = []

#create room slots
for room in range (1, rooms+1):
    room_slots[room] = []

#create teacher conflict
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


overlap_conflict, popularity = compute_overlap(pref_list)

# we need overlapping
# now we need rank class popularity


j = 0
teacher_conflict = [0] * 15
class_teacher = []

with open(sys.argv[2], "r") as contraints_file:
    for line in contraints_file:
        if j < 8:
            j +=1
            continue
        class_teacher.append(line.split())

for a in class_teacher:
    tchr1 = int(a[1])
    for b in class_teacher:
        tchr2 = int(b[1])
        if tchr1 == tchr2 and a[0] != b[0]:
            teacher_conflict[int(a[0])] = int(b[0])
            teacher_conflict[int(b[0])] = int(a[0])
# avoid overlap class and teacher class

time_slots = {}
times = 4
for time in range (1, times+1):
    time_slots[time] = []

def divide_into_slots(overlap_conflict, teacher_conflict):
    times = 4
    time_slots = {time: [] for time in range(1, times + 1)} 
    for clss in overlap_conflict:
        if all(clss[0] not in slot for slot in time_slots.values()):
            for key in time_slots:
                if clss[1] not in time_slots[key] and teacher_conflict[clss[0]] not in time_slots[key] and len(time_slots[key]) < 4:
                    time_slots[key].append(clss[0])
                    break
    
        if all(clss[1] not in slot for slot in time_slots.values()):
            for key in time_slots:
                if clss[0] not in time_slots[key] and teacher_conflict[clss[1]] not in time_slots[key] and len(time_slots[key]) < 4:
                    time_slots[key].append(clss[1])
                    break
    return time_slots


room_slots = {}
rooms = 4
room_sizes = [0, 84, 89, 18, 59]
for room in range (1, rooms+1):
    room_slots[room] = []

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
            name = temp
            objects.append(name)
    sorted_objects = sorted(objects, key=lambda x: x.ID)
    couldnt_enroll_count = 0
    for list in pref_list:
        studentID = int(list[0])
        times_enrolled = [0,0,0,0]
        for i in range(1,4):
            clssID = int(list[i])
            class_Class = sorted_objects[clssID-1]
            #for each class on pref list check that student is available
            #at that time, else don't enroll them and count 
            if times_enrolled[class_Class.time - 1] == 0:
                times_enrolled[class_Class.time - 1] = 1
                class_Class.students.append(studentID)
            else:
                couldnt_enroll_count = couldnt_enroll_count + 1
    
    #This is line for checking optimality
    #print("Couldnt enroll " + str(couldnt_enroll_count))
    #opt = ((50 * 4) - couldnt_enroll_count) / (50 * 4)
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
print(time_slots)
room_slots = divide_into_rooms(popularity)
print(room_slots)
    

divide_into_slots(overlap_conflict, teacher_conflict)
print(overlap_conflict)
print(teacher_conflict)
print(time_slots)
print(popularity)