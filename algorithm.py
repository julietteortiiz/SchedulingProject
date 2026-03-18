import sys
from collections import OrderedDict




pref_file = ""
if len(sys.argv) > 1:
    pref_file = sys.argv[1]
    
else:
    print("Usage: algorithms.py <pref_list> <constraints> <data>")


i = -1
pref_list = []
with open(pref_file, 'r') as pref_unclean:
    for line in pref_unclean:
        if i == -1:
            i += 1  
            continue
        pref_list.append(line.split())
        i += 1


class Class:
    def __init__(self, ID, teacherID, pref_count, room, room_size, overlap):
        self.ID = ID
        self.teacherID = teacherID
        self.pref_count = pref_count
        self.room =  room
        self.room_size = room_size



popularity = [0] * 15 
def compute_overlap(pref_list):
    over = {}
    for student_list in pref_list:
        for i in range(1, 5):
            current = int(student_list[i])
            popularity[current] += 1
            for j in range(i+1, 5):
                nxt = int(student_list[j])
                pair = (min(current, nxt), max(current, nxt))


                if pair in over:
                    over[pair] = over[pair] + 1
                else: 
                    over[pair] = 1
    print(popularity)
    overlap = OrderedDict(sorted(over.items(), key=lambda item: item[1], reverse=True)) 
    return overlap


overlap_conflict = compute_overlap(pref_list)

# we need overlapping
# now we need rank class popularity


j = 0
teacher_conflict = [0] * 15
with open(sys.argv[2], "r") as contraints_file:
    for line in contraints_file:
        if j < 8:
            j +=1
            continue
        clss = int(line.split()[0])
        teacher_conflict[clss] = int(line.split()[1])


# avoid overlap class and teacher class
time_slots = {}
times = 4
for time in range (1, times+1):
    time_slots[time] = []

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
#def divide_into rooms


divide_into_slots(overlap_conflict, teacher_conflict)
print(overlap_conflict)
print(teacher_conflict)
print(time_slots)


