# MDPDecider.py
# when run, accepts game states from stdin and outputs moves to stdout

import sys
from time import gmtime, strftime

file = open(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '.txt', 'w')

for line in sys.stdin:
	file.write(line)
sys.stdout.write('message ' + '\n')
sys.stdout.flush()