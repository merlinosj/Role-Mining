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

def degree_count(fname):
        global neighbor_nodes,predecessor_nodes,sigma
        f = open(fname, 'r+')
        fromNode = []
        #sigma = [[0 for j in xrange(no_roles)] for i in xrange(no_roles)]
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
        print 'Distinct Degrees',len(degree_set)

i_filename = sys.argv[1]

degree_count(i_filename)
