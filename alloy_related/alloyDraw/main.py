from parser import parseXML
import networkx as nx
import matplotlib.pyplot as plt
import sys


(nelems, nrels) = parseXML(sys.argv[1])

g = nx.Graph()

l = []
for nrel in nrels:
    nodeA = f'{nrel.elementA}{nrel.positionOnA}'
    nodeB = f'{nrel.elementB}{nrel.positionOnB}'

    found = False
    for ll in l:
        if nodeA in ll or nodeB in ll:
            ll.add(nodeB)
            ll.add(nodeA)
            found = True
        if found:
            break
    if not found:
        l.append(set([nodeA, nodeB]))


for i in range(len(nelems)):
    node0 = f'{i}0'
    node1 = f'{i}1'
    found0 = False
    found1 = False
    for ll in l:
        if node0 in ll and not found0:
            node0 = '#'.join(ll)
            found0 = True
        if node1 in ll and not found1:
            node1 = '#'.join(ll)
            found1 = True
        if found0 and found1:
            break
    g.add_node(node0)
    g.add_node(node1)
    g.add_edge(node0, node1)

plt.plot()
nx.draw(g, with_labels=True, font_weight='bold')
plt.show()

