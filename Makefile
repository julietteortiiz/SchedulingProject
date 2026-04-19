final: greedy_algorithm.py
	python3 greedy_algorithm.py project/brynmawr/real_student_prefs.txt project/brynmawr/real_constraints.txt > a_schedule.txt

valid: is_valid_v2.pl
	perl is_valid_v2.pl project/brynmawr/real_constraints.txt project/brynmawr/real_student_prefs.txt a_schedule.txt

optimality:
	set -e; \
	for c in experiments/optimality/*_c.txt; do \
		base="$${c%_c.txt}"; \
		p="$${base}_p.txt"; \
		s="/tmp/$$(basename "$$base")_schedule.txt"; \
		echo "== $$(basename "$$base") =="; \
		python3 greedy_algorithm.py "$$p" "$$c" | tee /tmp/run.txt | awk 'BEGIN{keep=0} /^Course\tRoom\tTeacher\tTime\tDays\tStudents$$/{keep=1} keep' > "$$s"; \
		perl is_valid_v2.pl "$$c" "$$p" "$$s"; \
	done

class_scale:
	set -e; \
	for c in experiments/class_scale/*_c.txt; do \
		base="$${c%_c.txt}"; \
		p="$${base}_p.txt"; \
		s="/tmp/$$(basename "$$base")_schedule.txt"; \
		echo "== $$(basename "$$base") =="; \
		python3 greedy_algorithm.py "$$p" "$$c" | tee /tmp/run.txt | awk 'BEGIN{keep=0} /^Course\tRoom\tTeacher\tTime\tDays\tStudents$$/{keep=1} keep' > "$$s"; \
		perl is_valid_v2.pl "$$c" "$$p" "$$s"; \
	done
