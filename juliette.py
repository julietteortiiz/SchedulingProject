# IMPORTS
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
        self.classes = []
    def __str__(self):
        return f" Room {self.ID}"
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
        return str(self.ID) + " " + self.dept + " " + str(self.building) + str(self.room) + " Days" + str(self.days) + " Times " + str(self.time)

#GLOBALS
brynmawr = College("Bryn Mawr")
haverford = College("Haverford")
class_objects = {}
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
                    over[(current,second)] = 1

    overlap = OrderedDict(sorted(over.items(), key=lambda item: item[1]))   
    print(overlap)


compute_overlap(pref_list) 

