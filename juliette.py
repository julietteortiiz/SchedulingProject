import sys
from collections import OrderedDict


with open(sys.argv[1], 'r') as f:
        lines = f.readlines()

pref_list = []
for line in lines[1:]:
    parts = line.strip().split()
    if len(parts) >= 2:
        numbers = [int(x) for x in parts[1:]]
        pref_list.append(numbers)


class Class:
    def __init__(self, ID, teacherID, pref_count, room, room_size, overlap):
        self.ID = ID
        self.teacherID = teacherID
        self.pref_count = pref_count
        self.room =  room
        self.room_size = room_size


#over is a dictionary
# key = (current,next)
def compute_overlap(pref_list):
    over = {}
    for student_list in pref_list:
        for i in range(2):
            current = student_list[i]
            for j in range(i+1, 3):
                second = student_list[j]
                if second < current:
                    temp = current
                    current = second
                    second = temp
                if (current,second) in over:
                    a = over[(current,second)]
                    over[(current,second)] = a + 1
                else:
                    over[(current,second)] = 1

    overlap = OrderedDict(sorted(over.items(), key=lambda item: item[1], reverse = True))   
    return overlap

Times = [1, 2, 3, 4]
Rooms = [1, 2, 3, 4]
Teachers = {1:(12,13), 2:(6,2), 3:(10,5), 4:(8,9), 5:(1,11), 6:(3,4), 7:(14,7)}

def schedule(overlap):
    SC = [0] * 14
    for pair in overlap:
        classA = pair[0]
        classB = pair[1]
        ScheduledA = SC[classA - 1]
        ScheduledB = SC[classB - 1] 
        if ScheduledA != 0 and ScheduledB != 0:
            continue
        if ScheduledA != 0 and ScheduledB == 0: 
            
#when scheduling need to first check that there's an avilable time slot
#that doesn't induce 
def findSlot(classID, overlapTime, conflictTime, scheduledClasses):
    check = []
    for i in range(1,14):
        if i != overlapTime or i != conflictTime:
            check.append(i)
    for time in check:
        if NULL in scheduledClasses[time]:
            print("Found Slot!")
            return time
    






             



#MAIN
overlap = compute_overlap(pref_list) 
schedule(overlap)

