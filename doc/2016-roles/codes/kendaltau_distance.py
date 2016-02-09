import sys
import operator
import scipy.stats as stats
from copy import deepcopy
import numpy as np

i_filename = sys.argv[1]
res_filename = sys.argv[2]
f = open(i_filename, 'r+')
namelist = dict()
idlist = dict()
neighbors = {}
i = 0
cnt = 0
for record in f:
    cnt += 1
    record= record.strip().split('\t')
    if cnt == 1:
        node_count = int(record[0])
    else:
      src_node = int(record[0])
      dst_node = int(record[1])
      neighbors.setdefault(src_node,set()).add(dst_node)


role_list = {}
role = {}
degree_list = dict()
f = open(res_filename, 'r+')
for record in f:
    record= record.strip().split('\t')
    node = int(record[0])
    #degree = int(record[1])
    node_role = int(record[1])
    role[node]=node_role
    role_list.setdefault(node_role,set()).add(node)
avg_degree = {}

for keys in role_list:
  nodes = list(role_list[keys])
  nodes.sort()
  deg_sum = 0
  for node in nodes:
    if node in neighbors:
       deg_sum += len(neighbors[node])
       degree_list[node] = len(neighbors[node])
    else:
       deg_sum += 0
       degree_list[node] = 0       
  #print deg_sum
  avg_degree[keys] = deg_sum/float(len(nodes))
#print avg_degree
sorted_role = sorted(avg_degree.items(), key=operator.itemgetter(1))
#print sorted_role

z = zip(*sorted_role)
sorted_role_list = np.argsort(list(z[0]))
#print sorted_role_list
#sl =[8]
#for x in sorted_role_list:
#   sl.append(x)
#sorted_role_list.append(5)
#sorted_role_list.append(8)
#sorted_role_list.append(3)
#sorted_role_list = deepcopy(sl)
print sorted_role_list
role1 = deepcopy(role)
for keys in role:
  role1[keys]=sorted_role_list[role[keys]]
#print role
#print degree_list
x = list(role1.values())
y = list(degree_list.values())
#print role
#print role1
#print np.mean([degree_list[z] for z in role1 if role1[z] == 0])
#print np.mean([degree_list[z] for z in role1 if role1[z] == 1])
#print np.mean([degree_list[z] for z in role1 if role1[z] == 2])
#print np.mean([degree_list[z] for z in role1 if role1[z] == 3])
tau, p_value = stats.kendalltau(x, y)
print 'TAU:',tau
print 'P_VALUE:',p_value
