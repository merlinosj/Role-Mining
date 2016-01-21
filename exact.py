#python exact.py 10.txt 10
import sys
import numpy as np
from collections import defaultdict,OrderedDict,Counter
import operator
import time
from os.path import basename
profile = {}

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
def exact_role_assignment(fname):
  global profile
  f = open(fname, 'r+')
  fromNode = []
  #edgeList = []
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
  counter1=Counter(fromNode)
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

  neighbor_role_vector = role_population(neighbor_nodes,role,node_count,no_roles)
  #print neighbor_nodes
  #print neighbor_role_vector
  #print profile
  #sorted_profile = sorted(profile, key=itemgetter(*range(no_roles)))
  #print sorted_profile

  iteration = 1

  '''if score == 0:
    return role'''
  flag = True
  while flag:
	  print 'Iteration:', iteration
	  role_list = [i for i in xrange(no_roles)]
	  profile = neighbor_role_vector
	  sorted_profile = sorted(profile.items(), key=operator.itemgetter(1))
	  print 'profile sorting is done....'
	  z = zip(*sorted_profile)
	  r = 0
	  profile1 = 0
	  role[z[0][profile1]] = r
	  for profile2 in xrange(1,len(z[0])):
	    if z[1][profile1] == z[1][profile2]:
	      #print 'MATCHING',z[0][profile1],z[0][profile2]
	      role[z[0][profile2]] = r
	    else:
	      r += 1
	      role[z[0][profile2]] = r
	      profile1 = profile2
	  print 'profile comparision is done....'
	  no_roles_new = len(set(role.values()))
	  print 'New Role Count:',no_roles_new
	  neighbor_role_vector = role_population(neighbor_nodes,role,node_count,no_roles_new)
	  print 'Role Vector Population done...'

	  if no_roles_new > no_roles:
		no_roles = no_roles_new
	  else:
		flag = False
	  iteration += 1
	  #if iteration == 2:
	  	#break
  return role,no_roles_new,node_count,iteration-1,flag2

i_filename = sys.argv[1]
file_name = basename(i_filename).split('.')[0]
print file_name
stats_filename = 'logs/'+file_name +'_exact_statistics.log'
output_filename = 'output/'+file_name +'_exact_output.txt'
st_time = time.time()
roles_final,no_roles,node_count,iteration,flag = exact_role_assignment(i_filename)
end_time = time.time()

print 'No of Roles:',no_roles
with open(stats_filename,'wb') as outfile:
	text = 'FILE NAME: '+str(file_name)+'\n'
	outfile.write(text)
	text = 'NODE COUNT: '+str(node_count)+'\n'
	outfile.write(text)
	text = 'ROLE COUNT: '+str(no_roles)+'\n'
	outfile.write(text)
	text = 'ITERATIONS: '+str(iteration)+'\n'
	outfile.write(text)
	text = 'START TIME: '+ str(st_time)+'\n'
	outfile.write(text)
	text = 'END TIME: '+ str(end_time)+'\n'
	outfile.write(text)
	total_time = end_time - st_time
	text = 'TOTAL TIME: '+ str(total_time)+'\n'
	outfile.write(text)
with open(output_filename,'wb') as outfile:
  for key, value in roles_final.iteritems():
    if flag == 1:
      text = str(key+1) +'\t' +str(value) +'\n'
    else:
      text = str(key) +'\t' +str(value) +'\n'
    outfile.write(text)
	


