import sys
import operator
import scipy.stats as stats
from copy import deepcopy
from munkres import Munkres
filename1 = sys.argv[1]
filename2 = sys.argv[2]
nodecount = int(sys.argv[3])
rolecount = int(sys.argv[4])
f = open(filename1, 'r+')
role_sets1 = {}
role_sets2 = {}
for record in f:
    record= record.strip().split('\t')
    node = int(record[0])
    role = int(record[1])
    role_sets1.setdefault(role,set()).add(node)

#For Rolx Result    
with open(filename2) as f1:
  lines = f1.read().split(',')
for i in xrange(len(lines)):
    role_sets2.setdefault(int(lines[i]),set()).add(i)
 

'''#For non Rolx Result   
f = open(filename2, 'r+')
for record in f:
    record= record.strip().split('\t')
    node = int(record[0])
    role = int(record[1])
    role_sets2.setdefault(role,set()).add(node)'''

A = [
  [nodecount for i in xrange(rolecount)] 
    for j in xrange(rolecount)
]

for i in xrange(rolecount):
  for j in xrange(rolecount):
     if i in role_sets1 and j in role_sets2:
      absThing = len(role_sets1[i] & role_sets2[j])
     else:
      absThing = 0 
     
     A[i][j] -= absThing
     
m = Munkres()
indexes = m.compute(A)
print indexes
map_info = [-1 for i in xrange(rolecount)]
for x in indexes:
  map_info[x[0]] = x[1]
print map_info

final_sum = 0
for i in xrange(rolecount):
  if i in role_sets1 and map_info[i] in role_sets2:
    absThing = len(role_sets1[i] & role_sets2[map_info[i]])
  else:
    absThing = 0 
  final_sum += absThing/float(nodecount)

print final_sum