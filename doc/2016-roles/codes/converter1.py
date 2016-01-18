#python converter1.py karate.txt karate_directed.txt
import sys
i_filename = sys.argv[1]
o_filename = sys.argv[2]
edgelist = {}
f = open(i_filename, 'r+')
cnt = 0
for record in f:
	cnt += 1
	record= record.strip().split('\t')
	if cnt == 1:
		node_count = int(record[0])
	else:
		src_node = int(record[0])
		dst_node = int(record[1])
		edgelist.setdefault(src_node,[]).append(dst_node)
		edgelist.setdefault(dst_node,[]).append(src_node)

with open(o_filename,'wb') as outfile:
	outfile.write(str(len(edgelist)))
	for x in edgelist.keys():
		for y in edgelist[x]:
			text = '\n'+str(x) +'\t'+str(y)
			outfile.write(text)	
		
  