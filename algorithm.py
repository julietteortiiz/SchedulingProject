import sys
from collections import OrderedDict




pref_file = ""
if len(sys.argv) > 1:
    pref_file = sys.argv[1]
    
else:
    print("Usage: algorithm.py <pref_list> <constraints> <data>")

#construct preference list

i = -1
pref_list = []
with open(pref_file, 'r') as pref_unclean:
    for line in pref_unclean:
        if i == -1:
            i += 1  
            continue
        pref_list.append(line.split())
        i += 1

#class object definition
class Class:
    def __init__(self, ID, teacherID, time, room):
        self.ID = ID
        self.teacherID = teacherID
        self.time = time
        self.room =  room
        self.students = []

#create the overlap dictionary and the list of classes based off popularity
popularity = {}
pop = {}
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

#we need overlapping
# now we need rank class popularity

#read in constraints and get teachers

j = 0
teacher_conflict = [0] * 15
class_teacher = []
cID_IID = {} #for easy class/teacher lookup

with open(sys.argv[2], "r") as contraints_file:
    for line in contraints_file:
        if j < 8:
            j +=1
            continue
        class_teacher.append(line.split())

for a in class_teacher:
    tchr1 = int(a[1])
    cID_IID[int(a[0])] = tchr1
    for b in class_teacher:
        tchr2 = int(b[1])
        if tchr1 == tchr2 and a[0] != b[0]:
            teacher_conflict[int(a[0])] = int(b[0])
            teacher_conflict[int(b[0])] = int(a[0])
    
# avoid overlap class and teacher class

#create time slots
time_slots = {}
times = 4
for time in range (1, times+1):
    time_slots[time] = []
#I think this is going to create issues if there ends up not being any available slots
def divide_into_slots(overlap_conflict, teacher_conflict):

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

room_slots = {}
rooms = 4
room_sizes = [0, 84, 89, 18, 59]
for room in range (1, rooms+1):
    room_slots[room] = []

#For each time slot assign the most popular class to the largest room and so on
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


overlap_conflict, popularity = compute_overlap(pref_list)
divide_into_slots(overlap_conflict, teacher_conflict)
room_slots = divide_into_rooms(popularity)

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
    for list in pref_list:
        studentID = int(list[0])
        for i in range(1,4):
            clssID = int(list[i])
            class_Class = sorted_objects[clssID-1]
            class_Class.students.append(studentID)
    
            
      
          
    



            
            
create_class_objects(room_slots, pref_list, cID_IID)
#print("\nOverlap Conflict") 
#print(overlap_conflict)
#print("\n Popularity")
#print(popularity)
print("\n Teacher Conflict")
print(teacher_conflict)
#print("\n Time Slots")
#print(time_slots)
#Room Slots are going to be {1: {1:100, 2:200, 3:300, 4:400}}
#This says in time slot 1: class 100 is in room 1...
print("\n Room Slots")
print(room_slots)

#This takes in the scheduled classes (room_slots) from algorithm
#and enrolls students into the classes, reports optimality, and writes
#to a schedule text
#print("\n pref list")
#print(pref_list)




