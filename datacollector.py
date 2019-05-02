# Put your solution here.

import networkx as nx
from math import ceil
import random
from heapq import heappop, heappush
from itertools import count
import random

# when you solve for any graph, we will keep a matrix of size nk to build and save to separate file at the end
def solve(client):
    f = open("results.txt", "a+")

    client.end()
    client.start()

    graph = client.G

    locations = list(graph.nodes())
    numlocations = len(list(graph.nodes()))
    print("numlocations is ", str(numlocations))


    all_students = list(range(1, client.students + 1))
    numstudents = client.students

    print("num students is", str(numstudents))

    minNumTruth = ceil(numlocations / 2)

    numTruth = [0 for _ in range(numstudents)]
    numLies = [0 for _ in range(numstudents)]


    matrix = [[0 for x in range(numstudents)] for y in range(numlocations)]

    #evaluate all locations but in random order
    loc = list(range(numlocations))
    random.shuffle(loc)


    for randomloc in loc:
        #scount on location and collect student reports
        studentreports = list(client.scout(locations[randomloc], all_students).values())



        #remote on location get the actual value
        target = locations[randomloc]
        nextEdges = list(graph.edges(target, 'weight', default=0))
        minEdgeIndex = 0
        minEdge = -1
        for i in range(len(nextEdges)):
            if i == 0:
                minEdge = nextEdges[i][2]
                minEdgeIndex = i
            if nextEdges[i][2] < minEdge:
                minEdge = nextEdges[i][2]
                minEdgeIndex = i
        actualvalue = client.remote(target, nextEdges[minEdgeIndex][1])




        tuplelist = []
        for i in range(numstudents):


            studentreport = studentreports[i]
            if studentreport == actualvalue: #is telling the truth
                numTruth[i] += 1
            else:
                numLies[i] -=1

            worstcaseprob = (minNumTruth - numTruth[i]) / (numlocations - numTruth[i] - numLies[i])

            tuple = (worstcaseprob,studentreport, actualvalue)

            tuplelist.append(tuple)
        matrix[randomloc] = tuplelist
    print(matrix)
    f.write(str(matrix))
    f.close()


    client.end()












def studentjudgment(probs, reports):
    judge = [0, 0]
    for i in range(len(probs)):
        if probs[i] == 1:
            if reports[i] == True:
                return 1
            else:
                return (-1, 1000)
        if reports[i] == 0:
            judge[0] += (probs[i] ** 2)
        if reports[i] == 1:
            judge[1] += (probs[i] ** 2)
    if judge[0] >= judge[1]:
        return (-1, judge[0])
    else:
        return (1, judge[1])


def prim_mst_edges(G, weight='weight', data=True):
    """Generate edges in a minimum spanning forest of an undirected
    weighted graph.

    A minimum spanning tree is a subgraph of the graph (a tree)
    with the minimum sum of edge weights.  A spanning forest is a
    union of the spanning trees for each connected component of the graph.

    Parameters
    ----------
    G : NetworkX Graph

    weight : string
       Edge data key to use for weight (default 'weight').

    data : bool, optional
       If True yield the edge data along with the edge.

    Returns
    -------
    edges : iterator
       A generator that produces edges in the minimum spanning tree.
       The edges are three-tuples (u,v,w) where w is the weight.

    Examples
    --------
    >> G=nx.cycle_graph(4)
    >> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >> mst=nx.prim_mst_edges(G,data=False) # a generator of MST edges
    >> edgelist=list(mst) # make a list of the edges
    >> print(sorted(edgelist))
    [(0, 1), (1, 2), (2, 3)]

    Notes
    -----
    Uses Prim's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be used.
    """

    if G.is_directed():
        raise nx.NetworkXError(
            "Mimimum spanning tree not defined for directed graphs.")

    push = heappush
    pop = heappop

    nodes = list(G.nodes())
    c = count()

    while nodes:
        u = nodes.pop(0)
        frontier = []
        visited = [u]
        for u, v in G.edges(u):
            push(frontier, (G[u][v].get(weight, 1), next(c), u, v))

        while frontier:
            W, _, u, v = pop(frontier)
            if v in visited:
                continue
            visited.append(v)
            nodes.remove(v)
            for v, w in G.edges(v):
                if not w in visited:
                    push(frontier, (G[v][w].get(weight, 1), next(c), v, w))
            if data:
                yield (u, v, G[u][v])
            else:
                yield (u, v)


def prim_mst(G, weight='weight'):
    """Return a minimum spanning tree or forest of an undirected
    weighted graph.

    A minimum spanning tree is a subgraph of the graph (a tree) with
    the minimum sum of edge weights.

    If the graph is not connected a spanning forest is constructed.  A
    spanning forest is a union of the spanning trees for each
    connected component of the graph.

    Parameters
    ----------
    G : NetworkX Graph

    weight : string
       Edge data key to use for weight (default 'weight').

    Returns
    -------
    G : NetworkX Graph
       A minimum spanning tree or forest.

    Examples
    --------
    >> G=nx.cycle_graph(4)
    >> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >> T=nx.prim_mst(G)
    >> print(sorted(T.edges(data=True)))
    [(0, 1, {}), (1, 2, {}), (2, 3, {})]

    Notes
    -----
    Uses Prim's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be used.
    """
    T = nx.Graph(prim_mst_edges(G, weight=weight, data=True))
    # Add isolated nodes
    if len(T) != len(G):
        T.add_nodes_from([n for n, d in G.degree().items() if d == 0])
    # Add node and graph attributes as shallow copy
    for n in T:
        T.node[n].update(G.node[n].copy())
    T.graph = G.graph.copy()
    return T


def prim_mst_edges_sparse(G, weight='weight', data=True):
    """Generate edges in a minimum spanning forest of an undirected
    weighted graph.

    A minimum spanning tree is a subgraph of the graph (a tree)
    with the minimum sum of edge weights.  A spanning forest is a
    union of the spanning trees for each connected component of the graph.

    Parameters
    ----------
    G : NetworkX Graph

    weight : string
       Edge data key to use for weight (default 'weight').

    data : bool, optional
       If True yield the edge data along with the edge.

    Returns
    -------
    edges : iterator
       A generator that produces edges in the minimum spanning tree.
       The edges are three-tuples (u,v,w) where w is the weight.

    Examples
    --------
    >> G=nx.cycle_graph(4)
    >> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >> mst=nx.prim_mst_edges(G,data=False) # a generator of MST edges
    >> edgelist=list(mst) # make a list of the edges
    >> print(sorted(edgelist))
    [(0, 1), (1, 2), (2, 3)]

    Notes
    -----
    Uses Prim's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be used.
    """

    if G.is_directed():
        raise nx.NetworkXError(
            "Mimimum spanning tree not defined for directed graphs.")

    push = heappush
    pop = heappop

    nodes = list(G.nodes())
    c = count()

    while nodes:
        u = nodes.pop(0)
        frontier = []
        visited = [u]
        for u, v in G.edges(u):
            push(frontier, (G[u][v].get(weight, 1), next(c), u, v))

        while frontier:
            W, _, u, v = pop(frontier)
            if v in visited:
                continue
            visited.append(v)
            nodes.remove(v)
            for v, w in G.edges(v):
                if not w in visited:
                    push(frontier, (G[v][w].get(weight, 1), next(c), v, w))
            if data:
                yield (u, v, G[u][v])
            else:
                yield (u, v)


def prim_mst_sparse(G, weight='weight'):
    """Return a minimum spanning tree or forest of an undirected
    weighted graph.

    A minimum spanning tree is a subgraph of the graph (a tree) with
    the minimum sum of edge weights.

    If the graph is not connected a spanning forest is constructed.  A
    spanning forest is a union of the spanning trees for each
    connected component of the graph.

    Parameters
    ----------
    G : NetworkX Graph

    weight : string
       Edge data key to use for weight (default 'weight').

    Returns
    -------
    G : NetworkX Graph
       A minimum spanning tree or forest.

    Examples
    --------
    >> G=nx.cycle_graph(4)
    >> G.add_edge(0,3,weight=2) # assign weight 2 to edge 0-3
    >> T=nx.prim_mst(G)
    >> print(sorted(T.edges(data=True)))
    [(0, 1, {}), (1, 2, {}), (2, 3, {})]

    Notes
    -----
    Uses Prim's algorithm.

    If the graph edges do not have a weight attribute a default weight of 1
    will be used.
    """
    T = nx.Graph(prim_mst_edges(G, weight=weight, data=True))
    # Add isolated nodes
    if len(T) != len(G):
        T.add_nodes_from([n for n, d in G.degree().items() if d == 0])
    # Add node and graph attributes as shallow copy
    for n in T:
        T.node[n].update(G.node[n].copy())
    T.graph = G.graph.copy()
    return T

