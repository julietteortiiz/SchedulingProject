# Group Project: The Registrar's Problem
**CS 340, Spring 2026 | Prof. Dianna Xu**
**Deadline:** April 15th, midnight

---

## Problem Description

You will be considering the classic problem of how to schedule classes so that students are less likely
to have conflicts among the courses they want to take. To study this issue, you'll start by considering
how to schedule classes after students select their preferences. The registration process will ask
students to select 4 classes that they would like to register for (all classes assumed to be equally
important). The registrar's office (you) will then take these preferences and create a schedule that
allows as many students as possible to take most of the classes they want.

Specifically, the registrar's office needs to create a schedule that handles the following issues:

### 1. Classes
A list of classes is given. Every class must be scheduled in one room, for one time slot, with one
particular teacher, and with a list of enrolled students.

### 2. Room Sizes
A list of classroom sizes is given in terms of the number of students the classroom can hold. A class
scheduled in a room may not have more students enrolled than will fit in the room. Only one class can
be scheduled in the room at a given time.

### 3. Class Times
A number of possible class times is given. These are assumed to be simple non-overlapping slots.

### 4. Teachers
A list of teachers and names of the classes they teach is given. Each teacher teaches two classes (so
the number of teachers is exactly half the number of classes, which must be even). No teacher may teach
more than one class at a given time.

### 5. Student Preferences
A list of students and corresponding class requests for four classes is given. No student may be
scheduled for more than one class that meets at the same time.

---

## Optimality Criterion

A schedule is considered **optimal** if it meets all of the above constraints and achieves the best
possible value for student preferences. The value of student preferences is calculated by awarding
**1 point** for each class a student is enrolled in. The total point sum over all students is the
student preferences value achieved.

> **Maximum possible value:** 4 × (number of students)