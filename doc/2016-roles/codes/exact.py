#python exact.py 10.txt 10
import sys
import collections
import numpy as np
import math
from numpy import median
import random
from copy import deepcopy
from scipy.cluster.vq import kmeans2
from collections import defaultdict,OrderedDict
import operator
profile = {}
'''Profile Distance Calculation using the neighbor role vector'''
def F_calculation_new(neighbor_role_vector,role,role_vector,node_count):
	fr_value = [0 for i in xrange(node_count)]
	role_median = []
	for role_candidates in role_vector:
		median_vector = []
		#val = neighbor_role_vector[role_candidates[0]]
		for node in role_candidates:
			median_vector.append(neighbor_role_vector[node])
			#if val <> neighbor_role_vector[node]:
			  #print 'ROLE MATCH',role_candidates[0],node
		print median_vector
		role_median.append(list(median(median_vector, axis = 0)))
		#role_median.append(neighbor_role_vector[role_candidates[0]])
	print role_median
	print 'Centriod Calculation is done...'
	for i in xrange(node_count):
		idx = -1
		node_role_id = int(role[i])
		res=sum(list(np.power(np.array(role_median[node_role_id]) - np.array(neighbor_role_vector[i]),2)))
		#print 'Distance of node ',i,' is:',math.sqrt(res)
		print res
		sum_total = math.sqrt(res)
		fr_value[i] = sum_total
	return fr_value

'''Role Vector population(P) using the neighbor details and their respective role'''
def role_population(neighbor_nodes,role,node_count,no_roles):
  neighbor_role_vector = defaultdict(int)
  for key in  neighbor_nodes:
	  neighbors = neighbor_nodes[key]
	  #print 'NEIGHBORS OF ',key,'IS:',neighbors
	  role_dict = defaultdict(int)
	  for neighbor_node in neighbors:
		  neighbor_role = role[neighbor_node]
		  role_dict[neighbor_role] += 1
		  #neighbor_role_vector[key][neighbor_role] = neighbor_role_vector[key][neighbor_role] + 1
	  neighbor_role_vector[key] = zip(role_dict.keys(),role_dict.values())
  return neighbor_role_vector

'''The main function that clusters the nodes with same edges that have similar roles'''
def exact_role_assignment(fname,no_nodes):
  global profile
  f = open(fname, 'r+')
  fromNode = []
  #edgeList = []
  #neighbor_nodes=[[] for i in xrange(no_nodes)]
  neighbor_nodes = {}
  neighbor = []
  flag1 = 0
  flag2 = 0
  cnt = 0
  for record in f:
	  cnt += 1
	  record= record.strip().split('\t')
	  if cnt == 1:
		  node_count = int(record[0])
	  else:
		  if flag1 == 0:
			  flag1 = 1
			  first_node = int(record[0])
			  if first_node == 1:
				flag2 = 1
			  if flag2 == 1:
				old_node = first_node -1
			  else:
				old_node = first_node
		  if flag2 == 1:
			src_node = int(record[0])-1
			dst_node = int(record[1])-1
		  else:
			src_node = int(record[0])
			dst_node = int(record[1])
		  #edgeList.append((int(record[0]),int(record[1])))
		  fromNode.append(src_node)
		  if old_node == src_node:
			  neighbor.append(dst_node)

		  else:
			  neighbor_nodes[old_node]=neighbor
			  old_node = src_node
			  neighbor = []
			  neighbor.append(dst_node)
  neighbor_nodes[old_node]=neighbor
  print 'Reading File is done...'
  counter1=collections.Counter(fromNode)
  a = counter1.most_common(node_count)
  degrees = {}
  for x in a:
	  degrees[int(x[0])]=x[1]
  degree_set = set(degrees.values())
  degree_numpy = np.array(degrees.values())
  print 'Degree Calculation done...'
  role = {}
  i = 0
  for degree in degree_set:
	  ind = np.where(degree_numpy == degree)[0]
	  for element in ind:
		  role[element] = i
	  i += 1
  print 'Role Assignment based on degree is done... '
  for m in xrange(node_count):
    if m not in role:
      role[m] = i
  no_roles = len(set(role.values()))
  print 'Role Count:',no_roles
  role_vector = [[] for x in xrange(no_roles)]
  #Random Role Assignment
  for key in role:
	  role_id = role[key]
	  role_vector[role_id].append(key)

  neighbor_role_vector = role_population(neighbor_nodes,role,node_count,no_roles)
  #print neighbor_nodes
  #print neighbor_role_vector
  #print profile
  #sorted_profile = sorted(profile, key=itemgetter(*range(no_roles)))
  #print sorted_profile
  '''fr_value = F_calculation_new(neighbor_role_vector,role,role_vector,node_count)
  score = sum(fr_value)
  print 'Score:',score'''
  iteration = 1

  '''if score == 0:
    return role'''
  flag = True
  while flag:
	  print 'Iteration:', iteration
	  role_new = deepcopy(role)
	  role_list = [i for i in xrange(no_roles)]
	  profile = neighbor_role_vector
	  sorted_profile = sorted(profile.items(), key=operator.itemgetter(1))
	  print 'profile sorting is done....'
	  z = zip(*sorted_profile)
	  r = 0
	  profile1 = 0
	  role_new[z[0][profile1]] = r
	  for profile2 in xrange(1,len(z[0])):
	    if z[1][profile1] == z[1][profile2]:
	      #print 'MATCHING',z[0][profile1],z[0][profile2]
	      role_new[z[0][profile2]] = r
	    else:
	      r += 1
	      role_new[z[0][profile2]] = r
	      profile1 = profile2
	  print 'profile comparision is done....'
	  no_roles_new = len(set(role_new.values()))
	  print 'New Role Count:',no_roles_new
	  role_vector_new = [[] for x in xrange(no_roles_new)]
	  for key in role_new:
		  role_id = role_new[key]
		  role_vector_new[role_id].append(key)
	  neighbor_role_vector = role_population(neighbor_nodes,role_new,node_count,no_roles_new)
	  print 'Role Vector Population done...'
	  #print neighbor_role_vector
	  '''fr_value= F_calculation_new(neighbor_role_vector,role_new,role_vector_new,node_count)
	  print 'Score Calculation done...'
	  score = sum(fr_value)
	  print 'Score:',score'''
	  if no_roles_new > no_roles:
		no_roles = no_roles_new
	  else:
		flag = False
	  iteration += 1
	  #if iteration == 2:
	  	#break
  return role_new

i_filename = sys.argv[1]
no_nodes = int(sys.argv[2])

roles_final = exact_role_assignment(i_filename,no_nodes)
print 'No of Roles:',len(set(roles_final.values()))
	


