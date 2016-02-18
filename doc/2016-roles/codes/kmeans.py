'''Syntax to run the file:
  python kmeans.py <Input_file_name>
Example:
 python kmeans.py karate_directed.txt
'''
import sys
import numpy as np
from collections import defaultdict,Counter
import time
from scipy.cluster.vq import kmeans2
from os.path import basename
neighbor_nodes = {}
predecessor_nodes = {}

'''Profile Distance Calculation using the neighbor role vector'''
def F_calculation_new(neighbor_role_vector,role,node_count,centroid):
	distance = 0
	#role_median = median(neighbor_role_vector,axis = 0)
	for i in xrange(node_count):
		idx = -1
		node_role_id = int(role[i])
		distance += sum(list(np.power(np.array(centroid[node_role_id]) - np.array(neighbor_role_vector[i]),2)))
	return distance



'''Centroid Calculation for all the roles using the profiles of the nodes'''	
def centroid_calculation(role_vector,neighbor_role_vector):
	#print 'IN CENTROID FUNCTION'
	role_median = {}
	for key in role_vector:
		role_candidates = role_vector[key]
		median_vector = []
		for node in role_candidates:
			median_vector.append(neighbor_role_vector[node])
		role_median[key]=list(np.mean(median_vector, axis = 0))
	return role_median
  

      
'''Profile Creation using the neighbor details and their respective roles'''
def role_population(role,node_count,no_roles):
        global neighbor_nodes
	neighbor_role_vector = [[0 for j in xrange(no_roles)] for i in xrange(node_count)]
	for key in  neighbor_nodes:
		neighbors = neighbor_nodes[key]
		for j in xrange(len(neighbors)):
			neighbor_role = role[neighbors[j]]
			neighbor_role_vector[key][neighbor_role] += 1
	#role_median = centroid_calculation(role_vector,neighbor_role_vector)
	
	return neighbor_role_vector

      
'''The main function that clusters the nodes with same edges that have similar roles'''
def iterative(fname,no_roles):
	global neighbor_nodes,predecessor_nodes
	f = open(fname, 'r+')
	fromNode = []
	#edgeList = []
	flag1 = 0
	flag2 = 0
	cnt = 0
	#File reading and neighbor details preparation
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
		  fromNode.append(src_node)
		  neighbor_nodes.setdefault(src_node,[]).append(dst_node)
		  predecessor_nodes.setdefault(dst_node,[]).append(src_node)

	print 'Reading File is done...'
	counter1=Counter(fromNode)
	a = counter1.most_common(node_count)
	degrees = [-1 for i in xrange(node_count)]
	for x in a:
	  degrees[int(x[0])]=x[1]
	(res,role) = kmeans2(np.array(degrees),no_roles)

	role_vector = defaultdict(list)
	for i in xrange(node_count):
		role_id = role[i]
		role[i]=role_id
		role_vector[role_id].append(i)
	neighbor_role_vector = role_population(role,node_count,no_roles)
	role_median = centroid_calculation(role_vector,neighbor_role_vector)
	distance = F_calculation_new(neighbor_role_vector,role,node_count,role_median)
	print 'Initial Distance',distance
	print 'TIME:',time.time()
	flag = True
	iteration = 1
	stop_flag = False
	while flag:
		print '================================'
		print 'Iteration:',iteration
		(centroid,role_new) = kmeans2(np.array(neighbor_role_vector),no_roles,minit='points')
		
		#Distance Calculation
		distance_new = F_calculation_new(neighbor_role_vector,role_new,node_count,centroid)
		print 'NEW DISTANCE:',distance_new
		diff_sum = distance - distance_new
		print 'Difference between Profile Distance:',diff_sum
		if diff_sum > 0 and stop_flag == False:
		  distance = distance_new
		  #profile Update
		  neighbor_role_vector = role_population(role_new,node_count,no_roles)
		  for i in xrange(node_count):
			  role[i]=role_new[i]

			
		  iteration += 1
		else:
		  flag = False
		  print 'Final Profile Distance:',distance
		  return role_new,node_count,distance,iteration-1,flag2	

'''Main part that takes input arguments, calls the functions and writes the final output to files'''
if __name__ == '__main__':
  i_filename = sys.argv[1]
  no_roles = int(sys.argv[2])
  file_name = basename(i_filename).split('.')[0]
  print file_name
  stats_filename = 'logs/'+file_name +'_kmeans_statistics.txt'
  output_filename = 'output/'+file_name +'_kmeans_output.txt'
  st_time = time.time()
  roles_final,node_count,distance,iteration,flag = iterative(i_filename,no_roles)
  end_time = time.time()
  with open(stats_filename,'wb') as outfile:
	  text = 'FILE NAME: '+str(file_name)+'\n'
	  outfile.write(text)
	  text = 'NODE COUNT: '+str(node_count)+'\n'
	  outfile.write(text)
	  text = 'ROLE COUNT: '+str(no_roles)+'\n'
	  outfile.write(text)
	  text = 'ITERATIONS: '+str(iteration)+'\n'
	  outfile.write(text)
	  text =  'FINAL DISTANCE: '+ str(distance)+'\n'
	  outfile.write(text)
	  text = 'START TIME: '+ str(st_time)+'\n'
	  outfile.write(text)
	  text = 'END TIME: '+ str(end_time)+'\n'
	  outfile.write(text)
	  total_time = end_time - st_time
	  text = 'TOTAL TIME: '+ str(total_time)+'\n'
	  outfile.write(text)
  with open(output_filename,'wb') as outfile:
    for key in xrange(node_count):
      if flag == 1:
	text = str(key+1) +'\t' +str(roles_final[key]) +'\n'
      else:
	text = str(key) +'\t' +str(roles_final[key]) +'\n'
      outfile.write(text)



