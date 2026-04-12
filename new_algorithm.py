#IMPORTS
import sys
from collections import OrderedDict
import math


class College:
    def __init__(self, name):
        self.name = name
        self.buildings = {}# building objects : list of departments}
    def __str__(self):
        return self.name + " " + self.buildings
    
class Building:
    def __init__(self, ID, name, rooms):
        self.ID = ID
        self.name = name
        self.rooms = []# room objects]
        self.depts = []
        self.classes = []  
          
    def __str__(self):
        return f"{self.ID} {self.name} {self.rooms}" 
    def __repr__(self):
        return f"{self.ID} {self.name} {self.rooms}"
    def insert_by_popularity(self, classObj):
        self.popularity.append(classObj)

class Room:
    def __init__(self, ID, capacity):
        self.ID = ID
        self.capacity = capacity
        self.schedule =  [[]] # rows represent times and columns represent weekdays always 5 
    def __str__(self):
        return f"{self.ID} {self.capacity}"
    def __repr__(self):
        return f"{self.ID} {self.capacity}"

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
        self.room = "" # given by dept popularity ranking, needs to just be id
        self.days = "" # given by a room's time availability
        self.time = "" # given by a room's time availability
        self.students = [] # students who want to take this class

    def __str__(self):
        return str(self.ID) + " " + self.dept + " " + str(self.building) + str(self.room)

#GLOBALS
brynmawr = College("Bryn Mawr")
haverford = College("Haverford")
class_objects = []
building_objects = {}
room_objects = []



#READ INPUTS
if len(sys.argv) < 1:
    print("Usage: algorithm.py <pref_list> <constraints> ")
    exit

pref_list = []
with open(sys.argv[1], 'r') as pref_unclean:
    i = -1
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
    pop = {} #for compute overlap

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
room_sizes = []


with open(sys.argv[2], "r") as constraints_file:
    line_number = 0 

    buildings_section = False
    buildings_read = 0

    rooms_section = False
    rooms_read = 0

    classes_section = False
    classes_read = 0
    all_buildings = []
 
    dept_to_buildings = {
    # Bryn Mawr
    "CS": ["Park"],
    "Biology": ["Park"],
    "Physics": ["Park"],
    "English" : ["Guild"],
    "Art" : ["Goodhart"],
    "Sociology": ["Dalton"],
    "Philosophy" : ["Bettws"],
    # Haverford
    "History": ["Chase"],
    "Econ": ["Sharpless"],
    "Math": ["Hilles"],
    "Psychology": ["Sharpless"],
    "Chem":["Stokes"],
    "Political":["Chase"],
    "Music":["Roberts"],
    "Psychology":["Stokes"]
}

    for line in constraints_file:
        processed_line = line.split()
        if processed_line[0] == "Class" and processed_line[1] == "Times":
            num_of_class_times = int(processed_line[2])

        elif processed_line[0] == "Buildings":
            num_of_buildings = int(processed_line[1]) 
            all_buildings = [""] * (num_of_buildings + 1)
            buildings_section = True

        #for each building
        elif buildings_section == True:
            buildingID = int(processed_line[0]) #give it an ID
            building_name = processed_line[2] #get it's name
            buildings_room_num = int(processed_line[3]) #get the number of rooms in the building
            building = Building(buildingID, building_name, buildings_room_num)  #create building object
            building_objects[building.name] = building
             
            #seperate into buildings       
            all_buildings[buildingID] = building
            if processed_line[1] == "B":    
                brynmawr.buildings[building] = building.depts
            else:   
                haverford.buildings[building] = building.depts
            buildings_read += 1
            if buildings_read == num_of_buildings:
                buildings_section = False

        elif processed_line[0] == "Rooms":
            num_of_rooms = int(processed_line[1])
            room_sizes.append(0)
            rooms_section = True

        elif rooms_section == True: 
            roomID = int(processed_line[0])
            buildingID = int(processed_line[1])
            capacity = int(processed_line[2])
            room = Room(roomID, capacity)
            all_buildings[buildingID].rooms.append(room) 
            room_objects.append(room)

            room_sizes.append(int(processed_line[2]))
            rooms_read += 1    

            if rooms_read == num_of_rooms:
                rooms_section = False

        elif processed_line[0] == "Classes":
            num_of_classes = int(processed_line[1])
        elif processed_line[0] == "Teachers":
            num_of_teachers = int(processed_line[1])
            class_section = True
        elif class_section ==True:
            classID = int(processed_line[0])
            dept = processed_line[2]
            teacherPairID = int(processed_line[3])
            credit_hours = int(processed_line[4])
            day_frequency = int(processed_line[5])
            
            if processed_line[1] == "B":    
                college = brynmawr
            else:   
                college = haverford  
                  
            classObj = Class(classID,college,dept, popularity[classID], teacherPairID, day_frequency, credit_hours) 
            classObj.building = dept_to_buildings[dept]
            classes_read += 1
            b = building_objects.get(classObj.building[0])
            b.classes.append(classObj)
          
            
            if classes_read == num_of_classes:  
                classes_section = False
            class_objects.append(classObj)
            
 
    line_number += 1



def assign_rooms(Buildings):
        
    for name, building in Buildings.items():  
        if building.classes == [] or building.rooms == []:
            continue        
        sorted_classes = sorted(building.classes, key=lambda x:x.popularity, reverse = True)
        sorted_rooms = sorted(building.rooms, key=lambda x: x.capacity, reverse = True)
        num_classes = len(sorted_classes)
        num_rooms  = len(sorted_rooms)

        #1. len(classes) >= len(rooms) -> each room gets assigned 0 or 1 class, prioritize assigning larger rooms
        if num_classes == num_rooms or num_classes < num_rooms:
            for i in range(num_classes):
                current = sorted_classes[i]
                current.room = sorted_rooms[i]

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
                    current_class.room = sorted_rooms[i]
                    
                    del sorted_classes[0]

            for _ in range(num_rooms_max_classes):
                del sorted_rooms[0]

            for a in range(num_rooms_min_classes):
                for b in range(classes_per_room_min):
                    current_class = sorted_classes[0]
                    current_class.room = sorted_rooms[i]
                    del sorted_classes[0]


def assign_times(overlap_pairs):
    for pair in overlap_pairs:
        class1 = pair[0]
        class2 = pair[1]
       

#MAIN
overlap_pairs = compute_overlap(pref_list)
assign_rooms(building_objects)

for c in class_objects:
    print(c)












