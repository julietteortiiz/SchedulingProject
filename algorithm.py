import sys
from collections import OrderedDict




if len(sys.argv) > 1:
    pref_list = sys.argv[1]
 #   constraints = sys.argv[2]
 #   data = sys.argv[3]
else:
    print("Usage: algorithms.py <pref_list> <constraints> <data>")






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
        for i in range(2):
            current = student_list[i]
            for j in range(i+1, 3):
                next = student_list[j]
                over[(current, next)] = over[(current, next)] + 1

    overlap = OrderedDict(sorted(over.items(), key=lambda item: item[1]))   
    return overlap


compute_overlap(pref_list) 
