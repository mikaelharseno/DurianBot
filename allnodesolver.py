# Put your solution here.

import networkx as nx
import random
from heapq import heappop, heappush
from itertools import count

def solve(client):
    client.end()
    client.start()

    graph = client.G

    mst = nx.minimum_spanning_tree(graph)

    degrees = list(mst.degree)
    print(degrees)

    while (len(mst) > 1):
        nodeindex = 0
        lenNodes = len(degrees)
        while nodeindex < lenNodes:
            if degrees[nodeindex][1] == 1 and degrees[nodeindex][0] != client.home:
                break
            nodeindex += 1
        u = degrees[nodeindex][0]
        v = list(mst[u].keys())[0]
        client.remote(u,v)
        print(client.bot_count[client.home])
        mst.remove_node(u)
        degrees = list(mst.degree)

    print("Number of bots needed to be resqued:")
    print(client.l)
    print("Number of final rescued bots:")
    print(client.bot_count[client.home])

    client.end()