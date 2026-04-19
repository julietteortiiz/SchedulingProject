final: greedy_algorithm.py
	python3 greedy_algorithm.py project/brynmawr/real_student_prefs.txt project/brynmawr/real_constraints.txt > a_schedule.txt

valid: is_valid.pl
	perl is_valid_v2.pl project/brynmawr/real_student_prefs.txt project/brynmawr/real_constraints.txt a_schedule.txt

