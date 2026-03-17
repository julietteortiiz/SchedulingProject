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
print(pref_list)


class Class:
    def __init__(self, ID, teacherID, pref_count, room, room_size, overlap):
        self.ID = ID
        self.teacherID = teacherID
        self.pref_count = pref_count
        self.room =  room
        self.room_size = room_size



def compute_overlap(pref_list):
    over = {}
    for student_list in pref_list:
        for i in range(1, 4):
            current = student_list[i]
            for j in range(i+1, 4):
                next = student_list[j]
                temp = ""
                if int(next) < int(current):
                    temp = current
                    current = next
                    next = temp
                print(current, next)
                if (current, next) in over:
                    over[(current, next)] = over[(current, next)] + 1
                else: 
                    over[(current, next)] = 1

    overlap = OrderedDict(sorted(over.items(), key=lambda item: item[1]))   
    return overlap


print(compute_overlap(pref_list))

