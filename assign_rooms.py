#IMPORTS
import sys
import math
from collections import OrderedDict


#DATA STRUCTURES AND GLOBAL VARIABLES
class Class:
    def __init__(self, ID, dept, popularity):
        self.ID = ID
        self.room = []
        self.popularity = popularity
        self.dept = dept

class Building:
    def __init__(self, departments, rooms, classes):
        self.ID = id
        self.departments = departments #departmentID of which departments should be in here
        self.rooms = rooms #dictionary (key: roomID, value: room size)
        self.classes = classes #we'll insert classes in here as they are read in through compute_overlap()



def assign_rooms(Buildings):
    for building in Buildings:
        print("Building")
        sorted_classes = sorted(building.classes, key=lambda x:x.popularity, reverse = True)
        sorted_rooms = sorted(building.rooms.items(), key=lambda item: item[1], reverse = True)
        num_classes = len(sorted_classes)
        num_rooms  = len(sorted_rooms)
        
        #1. len(classes) >= len(rooms) -> each room gets assigned 0 or 1 class, prioritize assigning larger rooms
        if num_classes == num_rooms or num_classes < num_rooms:
            for i in range(num_classes):
                current = sorted_classes[i]
                current.room.append(sorted_rooms[i])
        
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
                    current_class.room.append(sorted_rooms[i])
                    del sorted_classes[0]
            
            for i in range(num_rooms_max_classes):
                del sorted_rooms[0]

            for i in range(num_rooms_min_classes):
                for j in range(classes_per_room_min):
                    current_class = sorted_classes[0]
                    current_class.room.append(sorted_rooms[i])
                    del sorted_classes[0]

                

#MAIN

c1 = Class(1, "Math", 3)
c2 = Class(2, "Math", 4)
c3 = Class(3, "Math", 1)
c4 = Class(4, "Math", 2)
c5 = Class(5, "Math", 5)
c6 = Class(6, "History", 3)
c7 = Class(7, "History", 1)
c8 = Class(8, "History", 2)

b1 = Building("Math",{1:5, 2:10, 3:7}, [c1,c2,c3,c4,c5])
b2 = Building("History",{4:1, 5:9, 6:11},[c6,c7,c8])


buildings = [b1,b2]

assign_rooms(buildings)

listt = [c6,c7,c8]
for c in listt:
    print("class: " + str(c.ID))
    print(c.room)
        



