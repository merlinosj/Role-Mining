'''Syntax to run the file:
  python hillclimbing.py <Input_file_name> <Output_file_name> <no_of_nodes> <no_of_roles>
Example:
 python hillclimbing.py karate_directed.txt karate_out.txt 34 4
'''
import sys
import numpy as np
from copy import deepcopy
from collections import defaultdict,OrderedDict,Counter
import time
neighbor_nodes = {}
predecessor_nodes = {}

'''Intermediate Centroid calculation which updates the centroid of the old role and new role of the node. The rest are intact'''
def intermediate_median_calculation(old_role,new_role,role_median,role_vector,neighbor_role_vector):
	neighbor_roles = {old_role,new_role}
	for neighbor_role in neighbor_roles:
		role_candidates = role_vector[neighbor_role]
		median_vector = []
		for node in role_candidates:
			median_vector.append(neighbor_role_vector[node])
		role_median[neighbor_role]=list(np.mean(median_vector, axis = 0))
	return role_median
      
'''Profile Update Function that updates the centroids of the node and its predecessors'''
def centroid_update(candidate,role_median,role_vector,neighbor_role_vector,role):
	global predecessor_nodes
	#print 'IN CENTROID FUNCTION'
	if candidate in predecessor_nodes:
		neighbors = predecessor_nodes[candidate]
		neighbor_roles = set(role[candidate])
		for j in neighbors:
			neighbor_roles.add(role[j])
		for neighbor_role in neighbor_roles:
			role_candidates = role_vector[neighbor_role]
			median_vector = []
			for node in role_candidates:
				median_vector.append(neighbor_role_vector[node])
			role_median[neighbor_role]=list(np.mean(median_vector, axis = 0))
	#print role_median
	return role_median

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
def role_population(role,node_count,no_roles,role_vector):
        global neighbor_nodes
	neighbor_role_vector = [[0 for j in xrange(no_roles)] for i in xrange(node_count)]
	for key in  neighbor_nodes:
		neighbors = neighbor_nodes[key]
		for j in xrange(len(neighbors)):
			neighbor_role = role[neighbors[j]]
			neighbor_role_vector[key][neighbor_role] += 1
	role_median = centroid_calculation(role_vector,neighbor_role_vector)
	return neighbor_role_vector,role_median

'''Profile updating function for a node for which the role is changed. The profile of predecessor of the node is updated'''
def role_update(candidate,candidate_old_role,candidate_new_role,neighbor_role_vector):
        global predecessor_nodes
	if candidate in predecessor_nodes:
		neighbors = predecessor_nodes[candidate]
				
		for j in neighbors:
			#print 'PREDECESSOR:',j
			#print neighbor_role_vector[j]
			neighbor_role_vector[j][candidate_new_role] +=  1
			neighbor_role_vector[j][candidate_old_role] -=  1
			#print neighbor_role_vector[j]
		#role_median = centroid_update(candidate,role_median,role_vector,neighbor_role_vector,neighbor_nodes,role)
	return neighbor_role_vector
      
      
'''Distance Calculation using profile and role centroids'''
def F_calculation_new(neighbor_role_vector,role,role_vector,role_median,node_count):
	fr_value = [0 for i in xrange(node_count)]
	for i in xrange(node_count):
		idx = -1
		node_role_id = int(role[i])
		res=sum(list(np.power(np.array(role_median[node_role_id]) - np.array(neighbor_role_vector[i]),2)))
		sum_total = res
		fr_value[i] = sum_total
	return fr_value

'''The main function that reads the graph and calls functions to develop profiles and use them for clustering'''

def hill_climbing(fname,no_nodes,no_roles):
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
		  #edgeList.append((int(record[0]),int(record[1])))
		  fromNode.append(src_node)
		  neighbor_nodes.setdefault(src_node,[]).append(dst_node)
		  #neighbor_nodes.setdefault(dst_node,[]).append(src_node)
		  predecessor_nodes.setdefault(dst_node,[]).append(src_node)

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
		  role[element] = i%no_roles
	  i += 1
	print 'Role Assignment based on degree is done... '
	for m in xrange(node_count):
		if m not in role:
		  role[m] = 0
	no_roles = len(set(role.values()))
	print 'Role Count:',no_roles
	
	role_vector = defaultdict(list)
	
	#Role Vector Update
	for key in role:
	  role_id = role[key]
	  role_vector[role_id].append(key)
	#print 'role_vector',role_vector
	neighbor_role_vector,role_median = role_population(role,node_count,no_roles,role_vector)
	#print 'neighbor_role_vector',neighbor_role_vector
	#print 'role_median',role_median	
	fr_value = F_calculation_new(neighbor_role_vector,role,role_vector,role_median,node_count)
	fr_value_sum = sum(fr_value)
	print 'Initial Distance',fr_value_sum	
	node_list = [i for i in xrange(node_count)]
	flag = True
	i = 1
	distance = 0
	while flag:
		print 'Iteration: ',i
		no_change_counter = 0
		for candidate in node_list:
			'''if int(candidate)%10 == 0:
				print 'Candidate is:',candidate
				#print 'DISTANCE:',distance
				#print time.time()'''
			#print 'Candidate is:',candidate
			max_gain = 0
			max_gain_role_ind = -1
			max_gain_role = role.copy()
			max_gain_role_vector = role_vector.copy()
			max_gain_role_median = role_median.copy()

			old_role = role[candidate]
			c_old = len(role_vector[old_role])
			old_centroid_old = sum(item*item for item in role_median[old_role])
			for new_role in xrange(no_roles): #Iteration through all the roles
				#print 'NEW ROLE:',new_role
				role_new = role.copy()
				role_new[candidate] = new_role
				if len(set(role_new.values())) == no_roles and new_role <> old_role: # Condition not to leave any roles unassigned and not use the same role
					role_vector_new = deepcopy(role_vector)
					role_vector_new[old_role].remove(candidate)
					role_vector_new[new_role].append(candidate)
					
					#Intermediate Centroid Calculation. Actual function is Centroid Update. Now it is commented out and all role centroid calculation is used for debugging purpose
					
					#intermediate_median = centroid_update(candidate,max_gain_role_median.copy(),role_vector_new,neighbor_role_vector,role_new)
					intermediate_median=centroid_calculation(role_vector_new,neighbor_role_vector)
				
					#Value A Calculation
					c_new = len(role_vector[new_role])

					intermediate_centroid_old = sum(item*item for item in intermediate_median[old_role])
					intermediate_centroid_new = sum(item*item for item in intermediate_median[new_role])
					old_centroid_new = sum(item*item for item in role_median[new_role])
					A =  c_old*old_centroid_old - (c_old-1)*intermediate_centroid_old + c_new*old_centroid_new - (c_new+1)*intermediate_centroid_new
					
					#B_w Calculation
					B_w = 0
					dl = defaultdict(int) #Will hold all the predecessors role counts
					if candidate in predecessor_nodes:
						for node in predecessor_nodes[candidate]:
							node_old_role = role[node]
							pw_i = neighbor_role_vector[node][old_role]
							pw_j = neighbor_role_vector[node][new_role]
							B_w += 2*pw_i - 2*pw_j - 2
							dl[node_old_role] += 1 
					#print 'B_w:',B_w
					#print 'DL VALUE IS:',dl
					
					#R_L Calculation
					R_l = 0
					for keys in dl:
					  R_l += 2*dl[keys] * ((intermediate_median[keys][old_role])-(intermediate_median[keys][new_role])-(dl[keys]/float(len(role_vector_new[keys]))))

					
					gain = B_w - R_l - A #Gain Calculation
					if gain > max_gain:
						max_gain = gain
						max_gain_role_ind = new_role
						max_gain_role = role_new.copy()
						max_gain_role_vector = role_vector_new.copy()


					    
			if max_gain_role_ind <> -1:
			  print 'Optimal Gain for ',candidate,' moving from ',old_role,' to ',max_gain_role_ind,' is ',max_gain
			  max_gain_neighbor_role_vector = role_update(candidate,old_role,new_role,deepcopy(neighbor_role_vector))
			  #Actual Function that updates centroid of the node and its predecessors. Commented out now for debugging and all role centroid calculation is used for debugging purpose
			  #max_gain_role_median = centroid_update(candidate,max_gain_role_median,max_gain_role_vector,max_gain_neighbor_role_vector,max_gain_role)
			  max_gain_role_median=centroid_calculation(max_gain_role_vector,max_gain_neighbor_role_vector) #All Role Centroid Calculation
			  #Distance Calculation used for debugging purpose    
			  fr_value_sum = sum(F_calculation_new(neighbor_role_vector,role,role_vector,role_median,node_count))
			  fr_value_new=F_calculation_new(max_gain_neighbor_role_vector,max_gain_role,max_gain_role_vector,max_gain_role_median,node_count)
			  fr_value_sum_new = sum(fr_value_new)
			  distance = fr_value_sum_new
			  print 'OLD DISTANCE:',fr_value_sum
			  print 'NEW DISTANCE:',distance
			  #Updating the profiles and centroids
			  role = max_gain_role.copy()
			  role_vector = max_gain_role_vector.copy()
			  neighbor_role_vector = max_gain_neighbor_role_vector
			  role_median = max_gain_role_median.copy()
			  fr_value_sum = fr_value_sum_new
			  
			else:
			  #print 'NO CHANGE IN ROLE FOR NODE',candidate
			  no_change_counter += 1


				
		i += 1
		if no_change_counter == node_count:
		#if i == 2:
			flag = False
	print 'Final Distance:',distance
	print 'Final Role:',role
	return role,distance
	


i_filename = sys.argv[1]
o_filename = sys.argv[2]
no_nodes = int(sys.argv[3])
no_roles = int(sys.argv[4])
'''
with open(o_filename,'ab') as outfile:
	text = 'NODE COUNT: '+str(no_nodes)+'\n'
	outfile.write(text)
	st_time = time.time()
	text = 'START TIME: '+ str(st_time)+'\n'
	outfile.write(text)
	roles_final,score = hill_climbing(i_filename,no_nodes,no_roles)
	end_time = time.time()
	text =  'FINAL SCORE: '+ str(score)+'\n'
	outfile.write(text)
	text = 'END TIME: '+ str(end_time)+'\n'
	outfile.write(text)
	total_time = end_time - st_time
	text = 'TOTAL TIME: '+ str(total_time)+'\n'
	outfile.write(text)
	'''
roles_final,score = hill_climbing(i_filename,no_nodes,no_roles)	
colors = ['red','green','blue','yellow','cyan','orange','brown','white','purple','pink','coral','violet','gold','plum','lightgreen']
#print colors
with open(o_filename,'ab') as outfile:
	for i in xrange(no_nodes):
		text = str((i+1))+' [style = \"filled\" color= \"' + colors[roles_final[i]] + '\"];\n'
		outfile.write(text)	
	outfile.write('}')
