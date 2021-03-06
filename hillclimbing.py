'''Syntax to run the file:
  python hillclimbing_init1.py <Input_file_name> <no_of_roles>
Example:
 python hillclimbing_init1.py karate_directed.txt 4
'''
import sys
import numpy as np
from copy import deepcopy
from collections import defaultdict,OrderedDict,Counter
import time
from operator import sub,add
from os.path import basename
neighbor_nodes = {}
predecessor_nodes = {}
sigma = {}

'''This computes centroids by using sigma(sum of neighbor role vector)'''
def compute_centroid(role, sigma, role_vector_length):
        if role_vector_length[role] == 0:
                return np.zeros(len(sigma[role]))
        else:
                return sigma[role] / float(role_vector_length[role])

     

'''Intermediate Centroid calculation which updates the centroid of the old role and new role of the node. The rest are intact'''
def intermediate_median_calculation(candidate,old_role,new_role,role_median,role_vector_length,neighbor_role_vector):
        global sigma
        role_median[old_role] = compute_centroid(old_role, sigma, role_vector_length)
        role_median[new_role] = compute_centroid(new_role, sigma, role_vector_length)
        return role_median

 
'''Profile Update Function that updates the centroids of the node and its predecessors'''
def centroid_update(candidate,role_median,role_vector_length,neighbor_role_vector,role,old_role,new_role):
        global predecessor_nodes,sigma
        if candidate in predecessor_nodes:
                neighbors = predecessor_nodes[candidate]
                neighbor_roles = set()
                neighbor_roles.add(old_role)
                neighbor_roles.add(new_role)
                for j in neighbors:
                        neighbor_roles.add(role[j])
                for neighbor_role in neighbor_roles:
                        role_median[neighbor_role] = compute_centroid(neighbor_role, sigma, role_vector_length)
        return role_median

'''Centroid Calculation for all the roles using the profiles of the nodes'''
def centroid_calculation(role_vector,neighbor_role_vector, no_roles):
        role_median = [None] * no_roles
        for key in role_vector:
                role_candidates = role_vector[key]
                median_vector = []
                for node in role_candidates:
                        median_vector.append(neighbor_role_vector[node])
                role_median[key]= np.mean(median_vector, axis = 0)
        for key in xrange(no_roles):
          if key not in role_vector.keys():
            role_median[key] = np.zeros(no_roles)
        return role_median

'''Sum of neigbor role vector is calculated for each role. This is calculated once and is updated by add/subtract when a node is moved from one role to another'''      
def sigma_calculation(role_vector,neighbor_role_vector,no_roles):
        global sigma
        for key in role_vector:
                role_candidates = role_vector[key]
                median_vector = []
                for node in role_candidates:
                        median_vector.append(neighbor_role_vector[node])
                sigma[key] = np.sum(median_vector, axis = 0)
        for key in xrange(no_roles):
          if key not in sigma.keys():
            sigma[key] = [0 for i in xrange(no_roles)]
  

      
'''Profile Creation using the neighbor details and their respective roles'''
def role_population(role,node_count,no_roles,role_vector):
        global neighbor_nodes,sigma
        neighbor_role_vector = np.zeros((node_count,no_roles))
        #neighbor_role_vector = [[0 for j in xrange(no_roles)] for i in xrange(node_count)]
        for key in  neighbor_nodes:
                neighbors = neighbor_nodes[key]
                for j in xrange(len(neighbors)):
                        neighbor_role = role[neighbors[j]]
                        neighbor_role_vector[key][neighbor_role] += 1
        role_median = centroid_calculation(role_vector,neighbor_role_vector, no_roles)
        sigma_calculation(role_vector,neighbor_role_vector,no_roles)
        return neighbor_role_vector,role_median

'''Profile updating function for a node for which the role is changed. The profile of predecessor of the node is updated'''
def role_update(candidate,candidate_old_role,candidate_new_role,neighbor_role_vector,role):
        global predecessor_nodes,sigma
        if candidate in predecessor_nodes:
                neighbors = predecessor_nodes[candidate]

                for j in neighbors:
                        #print 'PREDECESSOR:',j,role[j]
                        neighbor_role = role[j]
                        sigma[neighbor_role][candidate_old_role] -=  1
                        sigma[neighbor_role][candidate_new_role] +=  1
                        neighbor_role_vector[j][candidate_new_role] +=  1
                        neighbor_role_vector[j][candidate_old_role] -=  1
        return neighbor_role_vector
      
      
'''Distance Calculation using profile and role centroids'''
def F_calculation_new(neighbor_role_vector,role,role_median,node_count):
        distance = 0
        for i in xrange(node_count):
                node_role_id = int(role[i])
                distance += sum(list(np.power(np.array(role_median[node_role_id]) - np.array(neighbor_role_vector[i]),2)))
        return distance

'''The main function that reads the graph and calls functions to develop profiles and use them for clustering'''

def hill_climbing(fname,no_roles):
        global neighbor_nodes,predecessor_nodes,sigma
        f = open(fname, 'r+')
        fromNode = []
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
        degrees = {}
        for x in a:
          degrees[int(x[0])]=x[1]
        degree_set = set(degrees.values())
        #print 'degree_set',degree_set
        degree_numpy = np.array(degrees.values())
        print 'Degree Calculation done...'
        window_size = len(degree_set)/no_roles
        if len(degree_set)/float(no_roles) > window_size:
                window_size += 1
        role = [0 for i in xrange(node_count)]
        i = 0
        range_count = 1
        for degree in degree_set:
          ind = np.where(degree_numpy == degree)[0]
          
          for element in ind:
                  role[element] = i

          if range_count == window_size:
                i += 1
                range_count = 0
          range_count += 1
          
        print 'Role Assignment based on degree is done... '

        role_vector = defaultdict(list)
        role_vector_length = defaultdict(int)

        #Role Vector Update
        for key in xrange(len(role)):
          role_id = role[key]
          role_vector[role_id].append(key)
          role_vector_length[role_id] += 1
        neighbor_role_vector,role_median = role_population(role,node_count,no_roles,role_vector)
        fr_value_sum = F_calculation_new(neighbor_role_vector,role,role_median,node_count)
        print 'Initial Distance',fr_value_sum
        print 'TIME:',time.time()
        iteration = 1
        node_list = [i for i in xrange(node_count)]
        flag = True
        distance = 0
        node_list_count = node_count
        while flag:
                print 'Iteration: ',iteration
                beg = time.time()
                no_change_counter = 0
                for candidate in node_list:
                        max_gain = 0
                        max_gain_role_ind = -1
                        old_role = role[candidate]
                        c_old = role_vector_length[old_role]
                        old_centroid_old = role_median[old_role].dot(role_median[old_role]) # sum(item*item for item in role_median[old_role])

                        dl = defaultdict(int) #Will hold all the predecessors role counts
                        pw = np.zeros(no_roles)
                        pred_count = 0
                        if candidate in predecessor_nodes:
                                pred_count = len(predecessor_nodes[candidate])
                                for node in predecessor_nodes[candidate]:
                                        node_old_role = role[node]
                                        pw += neighbor_role_vector[node]
                                        dl[node_old_role] += 1 

                        for new_role in xrange(no_roles): #Iteration through all the roles
                                role[candidate] = new_role
                                if new_role <> old_role: # Condition not use the same role
                                        role_vector_length[old_role] -= 1
                                        role_vector_length[new_role] += 1
                                        sigma[old_role] -= neighbor_role_vector[candidate] 
                                        sigma[new_role] += neighbor_role_vector[candidate]
                                        intermediate_old = compute_centroid(old_role, sigma, role_vector_length)
                                        intermediate_new = compute_centroid(new_role, sigma, role_vector_length)

                                        #Value A Calculation
                                        c_new = role_vector_length[new_role]

                                        intermediate_centroid_old = intermediate_old.dot(intermediate_old) 
                                        intermediate_centroid_new = intermediate_new.dot(intermediate_new) 
                                        old_centroid_new = role_median[new_role].dot(role_median[new_role])
                                        A =  c_old*old_centroid_old - (c_old-1)*intermediate_centroid_old + c_new*old_centroid_new - (c_new+1)*intermediate_centroid_new

                                        B_w = 2*pw[old_role] - 2*pw[new_role] - 2*pred_count

                                        #R_L Calculation
                                        R_l = 0
                                        for keys in dl:
                                                if role_vector_length[keys] == 0:
                                                        dl_cl = 0
                                                else:
                                                        dl_cl = dl[keys]/float(role_vector_length[keys])
                                                if keys == old_role:
                                                        R_l += 2*dl[keys] * ((intermediate_old[old_role])-(intermediate_old[new_role])-dl_cl)
                                                elif keys == new_role:
                                                        R_l += 2*dl[keys] * ((intermediate_new[old_role])-(intermediate_new[new_role])-dl_cl)
                                                else:
                                                        R_l += 2*dl[keys] * ((role_median[keys][old_role])-(role_median[keys][new_role])-dl_cl)
                                          


                                        gain = B_w - R_l - A #Gain Calculation
                                        if gain > max_gain and gain > 1/float(node_count)**2:
                                                max_gain = gain
                                                max_gain_role_ind = new_role
                                        role[candidate] = old_role
                                        role_vector_length[old_role] += 1
                                        role_vector_length[new_role] -= 1
                                        sigma[old_role] += neighbor_role_vector[candidate]
                                        sigma[new_role] -= neighbor_role_vector[candidate]



                        if max_gain_role_ind <> -1:
                          role[candidate] = max_gain_role_ind
                          role_vector_length[old_role] -= 1
                          role_vector_length[max_gain_role_ind] += 1

                          sigma[old_role] -= neighbor_role_vector[candidate]
                          sigma[max_gain_role_ind] += neighbor_role_vector[candidate]
                        
                          neighbor_role_vector = role_update(candidate,old_role,max_gain_role_ind,neighbor_role_vector,role)
                          role_median = centroid_update(candidate,role_median,role_vector_length,neighbor_role_vector,role,old_role,max_gain_role_ind)                    
                             
                          
                        else:
                          #print 'NO CHANGE IN ROLE FOR NODE',candidate
                          #idle[candidate] += 1
                          no_change_counter += 1
                          

                iteration += 1
                if no_change_counter == node_count:
                        flag = False

                print 'TIME SPENT:',time.time() - beg
                distance=F_calculation_new(neighbor_role_vector,role,role_median,node_count)
                print 'DISTANCE:',distance
                print 'NODES UNCHANGED:',no_change_counter
        print 'Final Distance:',distance
        return node_count,role,distance,iteration-1,flag2


'''Main part that takes input arguments, calls the functions and writes the final output to files'''
if __name__ == '__main__':
	i_filename = sys.argv[1]
	no_roles = int(sys.argv[2])
	file_name = basename(i_filename).split('.')[0]
	print file_name
	stats_filename = 'logs/'+file_name +'_hill_statistics.txt'
	output_filename = 'output/'+file_name +'_hill_output.txt'
	st_time = time.time()
	node_count,roles_final,score,iteration,flag = hill_climbing(i_filename,no_roles)
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
		text =  'FINAL DISTANCE: '+ str(score)+'\n'
		outfile.write(text)
		text = 'START TIME: '+ str(st_time)+'\n'
		outfile.write(text)
		text = 'END TIME: '+ str(end_time)+'\n'
		outfile.write(text)
		total_time = end_time - st_time
		text = 'TOTAL TIME: '+ str(total_time)+'\n'
		outfile.write(text)
	with open(output_filename,'wb') as outfile:
	  for key in xrange(len(roles_final)):
	    if flag == 1:
	      text = str(key+1) +'\t' +str(roles_final[key]) +'\n'
	    else:
	      text = str(key) +'\t' +str(roles_final[key]) +'\n'
	    outfile.write(text)
