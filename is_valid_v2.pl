#!/usr/bin/perl -w
use strict;

if (!$ARGV[0] || !$ARGV[1] || !$ARGV[2]) {
	print "$0 takes a schedule and checks that it's valid based on the current schedule format.\n";
	print "Usage:\n";
	print "$0: <constraints file> <prefs file> <schedule file>\n";
	exit 1;
}

my $cfile = $ARGV[0];
my $pfile = $ARGV[1];
my $sfile = $ARGV[2];

my $numslots;
my $numrooms;
my $numclasses;
my $numteachers;
my %roomSize = ();
my %origCourseTeacher = ();
readConstraints($cfile);

my $numstudents;
my %origStudentPrefs = ();
readPrefs($pfile);

open(my $sched_fh, "<", $sfile) || die "Can't open file: $sfile\n";

my %courseSeen = ();
my %courseStudents = ();
my %roomDaySlot = ();
my %teacherDaySlot = ();
my %studentDaySlot = ();

my $lineno = 0;
my $stuprefs = 0;

my $bestcase = 0;

for my $stu (keys %origStudentPrefs) {
    $bestcase += scalar(@{$origStudentPrefs{$stu}});
}

while (my $line = <$sched_fh>) {
	chomp $line;

	if ($lineno == 0) {
		if ($line ne "Course\tRoom\tTeacher\tTime\tDays\tStudents") {
			print "Header line has incorrect format.\n";
			print "Line:$line\n";
			exit 1;
		}
		$lineno++;
		next;
	}

	my @fields = split(/\t/, $line, -1);
	if (@fields != 6) {
		print "Content line has incorrect format.\n";
		print "Line:$line\n";
		exit 1;
	}

	my ($course, $room, $teacher, $time, $days, $stus) = @fields;

	if ($course !~ /^\d+$/) {
		print "Course has incorrect format.\n";
		print "Line:$line\n";
		exit 1;
	}

	if (defined $courseSeen{$course}) {
		print "Course $course defined more than once.\n";
		print "Line:$line\n";
		exit 1;
	}
	$courseSeen{$course} = 1;

	if (!defined $origCourseTeacher{$course}) {
		print "Course $course is not defined in constraints.\n";
		print "Line:$line\n";
		exit 1;
	}

	if ($room eq "" || $teacher eq "" || $time eq "" || $days eq "") {
		print "Course $course is missing required schedule fields.\n";
		print "Line:$line\n";
		exit 1;
	}

	if ($room !~ /^\d+$/) {
		print "Room has incorrect format for course $course.\n";
		print "Line:$line\n";
		exit 1;
	}

	if (!defined $roomSize{$room}) {
		print "Room $room for course $course is not defined in constraints.\n";
		print "Line:$line\n";
		exit 1;
	}

	my $expected_teacher = $origCourseTeacher{$course};
	if ($expected_teacher == -1) {
		if ($teacher ne "NA") {
			print "Course $course should have teacher NA.\n";
			print "Line:$line\n";
			exit 1;
		}
	} else {
		if ($teacher !~ /^\d+$/) {
			print "Teacher has incorrect format for course $course.\n";
			print "Line:$line\n";
			exit 1;
		}
		if ($teacher != $expected_teacher) {
			print "Course $course does not have the correct teacher.\n";
			print "Line:$line\n";
			exit 1;
		}
	}

	my ($start, $end) = parse_time_range($time, $course, $line);
	my @day_indices = parse_days($days, $course, $line);

	my @students = ();
	if ($stus ne "") {
		if ($stus !~ /^(\d+)( \d+)*$/) {
			print "Students have incorrect format.\n";
			print "Line:$line\n";
			exit 1;
		}
		@students = split(/ /, $stus);
	}

	my $classsize = scalar(@students);
	if ($classsize > $roomSize{$room}) {
		print "Room $room is too small to hold course $course with $classsize students.\n";
		print "Line:$line\n";
		exit 1;
	}

	for my $day (@day_indices) {
		for my $slot ($start .. $end) {
			if (defined $roomDaySlot{$day}{$slot}{$room}) {
				my $other = $roomDaySlot{$day}{$slot}{$room};
				print "Multiple courses scheduled for room $room on day $day at slot $slot: $other and $course.\n";
				print "Line:$line\n";
				exit 1;
			}
			$roomDaySlot{$day}{$slot}{$room} = $course;

			if ($teacher ne "NA") {
				if (defined $teacherDaySlot{$day}{$slot}{$teacher}) {
					my $other = $teacherDaySlot{$day}{$slot}{$teacher};
					print "Teacher $teacher scheduled for overlapping courses $other and $course.\n";
					print "Line:$line\n";
					exit 1;
				}
				$teacherDaySlot{$day}{$slot}{$teacher} = $course;
			}
		}
	}

	$courseStudents{$course} = \@students;
	for my $stu (@students) {
		if (!defined $origStudentPrefs{$stu}) {
			print "Student $stu assigned to course $course but is not in the preference file.\n";
			print "Line:$line\n";
			exit 1;
		}

		if (!inArray($course, $origStudentPrefs{$stu})) {
			print "Student $stu assigned to unrequested course $course.\n";
			print "Line:$line\n";
			exit 1;
		}

		for my $day (@day_indices) {
			for my $slot ($start .. $end) {
				if (defined $studentDaySlot{$stu}{$day}{$slot}) {
					my $other = $studentDaySlot{$stu}{$day}{$slot};
					print "Student $stu assigned to overlapping courses $other and $course.\n";
					print "Line:$line\n";
					exit 1;
				}
				$studentDaySlot{$stu}{$day}{$slot} = $course;
			}
		}
		$stuprefs++;
	}

	$lineno++;
}

print "Schedule is valid.\n";
print "Student Preferences Value: ", $stuprefs, "\n";
print "Best Case Student Preference Value: ", $bestcase, "\n";
my $fit = int(($stuprefs/$bestcase) * 1000) /1000;
print "Fit percentage: ", $fit, "%\n";

exit 0;

sub readConstraints {
	my $file = $_[0];
	open(my $constraints_fh, "<", $file) || die "Can't open file: $file\n";

	my $isroom = 0;
	my $isclass = 0;
	while (my $line = <$constraints_fh>) {
		chomp $line;
		if ($line =~ /^Class Times\t(\d+)$/) {
			$numslots = $1;
		}
		if ($line =~ /^Buildings\t(\d+)$/) {
			$isroom = 0;
			$isclass = 0;
			next;
		}
		if ($line =~ /^Rooms\t(\d+)$/) {
			$numrooms = $1;
			$isroom = 1;
			$isclass = 0;
			next;
		}
		if ($line =~ /^Classes\t(\d+)$/) {
			$numclasses = $1;
			$isroom = 0;
			$isclass = 0;
			next;
		}
		if ($line =~ /^Teachers\t(\d+)$/) {
			$numteachers = $1;
			$isclass = 1;
			$isroom = 0;
			next;
		}
		if ($isroom) {
			my @fields = split(/\t/, $line);
			my $roomnum = $fields[0];
			my $size = $#fields >= 2 ? $fields[2] : $fields[1];
			$roomSize{$roomnum} = $size;
		}
		if ($isclass) {
			my @fields = split(/\t/, $line);
			my $classnum = $fields[0];
			my $classteach = $fields[1];
			$origCourseTeacher{$classnum} = $classteach;
		}
	}

	return;
}

sub readPrefs {
	my $file = $_[0];
	open(my $prefs_fh, "<", $file) || die "Can't open file: $file\n";

	while (my $line = <$prefs_fh>) {
		chomp $line;

		if ($line =~ /^Students\t(\d+)$/) {
			$numstudents = $1;
			next;
		}

		if ($line =~ /^(\d+)\t(.*)$/) {
			my $stu = $1;
			my @prefs = split(/\s+/, $2);
			$origStudentPrefs{$stu} = \@prefs;
		}
	}

	return;
}

sub parse_time_range {
	my ($time, $course, $line) = @_;
	if ($time !~ /^\((\d+),\s*(\d+)\)$/) {
		print "Time has incorrect format for course $course.\n";
		print "Line:$line\n";
		exit 1;
	}

	my $start = $1;
	my $end = $2;
	if ($start > $end) {
		print "Time range is reversed for course $course.\n";
		print "Line:$line\n";
		exit 1;
	}
	if ($end >= $numslots) {
		print "Course $course uses time slot $end but only $numslots slots exist.\n";
		print "Line:$line\n";
		exit 1;
	}
	return ($start, $end);
}

sub parse_days {
	my ($days, $course, $line) = @_;
	my %day_map = (
		"M"  => 0,
		"T"  => 1,
		"W"  => 2,
		"TH" => 3,
		"F"  => 4,
	);

	my @parsed = ();
	my $remaining = $days;
	while ($remaining ne "") {
		if ($remaining =~ s/^TH//) {
			push @parsed, $day_map{"TH"};
		} elsif ($remaining =~ s/^M//) {
			push @parsed, $day_map{"M"};
		} elsif ($remaining =~ s/^T//) {
			push @parsed, $day_map{"T"};
		} elsif ($remaining =~ s/^W//) {
			push @parsed, $day_map{"W"};
		} elsif ($remaining =~ s/^F//) {
			push @parsed, $day_map{"F"};
		} else {
			print "Days have incorrect format for course $course.\n";
			print "Line:$line\n";
			exit 1;
		}
	}

	my %seen = ();
	for my $day (@parsed) {
		if ($seen{$day}) {
			print "Course $course repeats a day in $days.\n";
			print "Line:$line\n";
			exit 1;
		}
		$seen{$day} = 1;
	}

	return @parsed;
}

sub inArray {
	my $item = $_[0];
	my $arr = $_[1];

	foreach my $it (@{$arr}) {
		if ($it eq $item) {
			return 1;
		}
	}

	return 0;
}
