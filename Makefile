juliette: juliette.py
	python3 juliette.py demo_studentprefs.txt 

algorithm: algorithm.py
	python3 algorithm.py demo_studentprefs.txt demo_constraints.txt 

valid: is_valid.pl
	perl is_valid.pl demo_constraints.txt demo_studentprefs.txt demo_schedule.txt