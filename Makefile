juliette: juliette.py
	python3 juliette.py demo_studentprefs.txt 

final: greedy_algorithm.py
	python3 greedy_algorithm.py p.txt c.txt > test_schedule.txt

valid: is_valid.pl
	perl is_valid.pl demo_constraints.txt demo_studentprefs.txt test_schedule.txt

10000schedule:
	python3 algorithm.py p_10000.txt c_10000.txt > our_schedule100000.txt

100:
	perl is_valid.pl c_100.txt p_100.txt our_schedule100.txt

1000:
	perl is_valid.pl c_1000.txt p_1000.txt our_schedule1000.txt

10000:
	perl is_valid.pl c_10000.txt p_10000.txt our_schedule1000.txt
