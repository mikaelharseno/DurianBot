# Put your solution here.

import networkx as nx
from math import ceil
import random
from heapq import heappop, heappush
from itertools import count

def solve(client):
    client.end()
    client.start()

    graph = client.G

    #Start by finding location of all bots using scout and remote.
    all_students = list(range(1, client.students + 1))
    totalNodes = len(graph.nodes)
    minNumTruth = ceil(totalNodes / 2)

    numTruth = [0 for _ in range(client.students)]
    numLies = [0 for _ in range(client.students)]
    worstcaseprob = [(minNumTruth - numTruth[i]) / (totalNodes - numTruth[i] - numLies[i]) for i in range(client.students)]

    nodeReports = {}
    nodeDistance = {}
    botsAt = {}
    unvisited = list(graph.nodes())
    botsleft = client.bots - sum(client.bot_count)
    counter = 0

    while botsleft > 0 and len(unvisited) > 0:
        #Pick node selector
        unvisitedOrHasBot = combinelist(unvisited, client.bot_locations)
        #   Pick a subset of nodes from unvisited
        #       Use shortest path mst
        mst = produce_shortest_path_mst(graph, unvisited, client.h)
        #       Use sparse mst for unvisited
        mst = produce_sparse_mst(graph, unvisited, client.h)
        #       Use sparse mst for unvisited or has bot, but remove leaves until all leaves are unvisited
        totalMst = produce_sparse_mst(graph, unvisitedOrHasBot, client.h)
        totalMstLeaves = get_leaf_nodes(totalMst)
        allLeavesUnvisited = False
        while not allLeavesUnvisited:
            allLeavesUnvisited = True
            for checkLeaf in totalMstLeaves:
                if checkLeaf not in unvisited:
                    totalMst.remove_node(checkLeaf)
                    allLeavesUnvisited = False
            totalMstLeaves = get_leaf_nodes(totalMst)
        mst = totalMst
        leaves = get_leaf_nodes(mst)
        #   Pick all nodes in unvisited
        leaves = unvisited
        #   Remove home node if it is in leaves
        if client.h in leaves:
            leaves.remove(client.h)

        #Pick best node
        #   Scout and get reports for all node candidates
        for leaf in leaves:
            if leaf not in nodeReports:
                nodeReports[leaf] = list(client.scout(leaf, all_students).values())
        #   Pick distance measure mst
        mstDist = nx.minimum_spanning_tree(graph)
        mstDist = produce_shortest_path_mst(graph, list(graph.nodes()), client.h)
        mstDist = produce_sparse_mst(graph, leaves, client.h)
        mstDist = produce_sparse_mst(graph, unvisited, client.h)
        mstDist = produce_sparse_mst(graph, unvisitedOrHasBot, client.h)
        for leaf in leaves:
            nodeDistance[leaf] = nx.shortest_path_length(mstDist, source=leaf, target=client.h)
        targetLeaf = student_judgment(numTruth, numLies, leaves, nodeReports, nodeDistance)

        #Pick remote direction
        mstRemote = nx.minimum_spanning_tree(graph)
        mstRemote = produce_shortest_path_mst(graph, list(graph.nodes()), client.h)
        mstRemote = produce_sparse_mst(graph, leaves, client.h)
        mstRemote = produce_sparse_mst(graph, unvisited, client.h)
        mstRemote = produce_sparse_mst(graph, unvisitedOrHasBot, client.h)
        remoteToNode = nx.shortest_path(mstRemote, source=targetLeaf, target=client.h)[1]
        botsRemoted = client.remote(targetLeaf, remoteToNode)
        unvisited.remove(targetLeaf)
        initialTargetLeafBots = botsRemoted - botsAt[targetLeaf]
        botsAt[targetLeaf] = 0
        botsAt[remoteToNode] += botsRemoted
        #   Update truth/lie arrays for scouts
        if initialTargetLeafBots == 1:
            targetLeafBot = True
        else:
            targetLeafBot = False
        targetReports = nodeReports[targetLeaf]
        for i in range(client.students):
            if targetReports[i] == targetLeafBot:
                numTruth[i] += 1
            else:
                numLies[i] += 1
            worstcaseprob[i] = (minNumTruth - numTruth[i]) / (totalNodes - numTruth[i] - numLies[i])

        botsleft = client.bots - sum(client.bot_count)
        counter += 1

    print("Bots recovered in remote(s): ")
    print(counter)

    # When all the locations discovered, we do algorithm in q2. (Prim's combined with Uniform Cost Search)
    # Uses client.bot_count

    sparsemst = produce_sparse_mst(graph, client.bot_locations, client.h)

    mst_remote(sparsemst, client)

    print("Number of bots needed to be rescued:")
    print(client.l)
    print("Number of final rescued bots:")
    print(client.bot_count[client.home])

    client.end()

def student_judgment(probs, reports):
    judge = [0, 0]
    for i in range(len(probs)):
        if probs[i] == 1:
            if reports[i] == True:
                return 1
            else:
                return (-1, 1000)
        if reports[i] == 0:
            judge[0] += (probs[i]**1)
        if reports[i] == 1:
            judge[1] += (probs[i]**1)
    if judge[0] >= judge[1]:
        return (-1, judge[0])
    else:
        return (1, judge[1])

def produce_sparse_mst(G, bot_locs, client_home):
    # Note: Relaxation not applied yet. Might be applied for further improvement.
    bot_exist_locs = bot_locs.copy()
    set_locs = [client_home]
    mst = nx.Graph()
    mst.add_node(client_home)
    while len(bot_exist_locs) > 0:
        init = False
        for bot_loc in bot_exist_locs:
            for node_in_set in set_locs:
                if not init:
                    cur_best_path = nx.shortest_path(G, source=bot_loc, target=node_in_set)
                    cur_best_length = nx.shortest_path_length(G, source=bot_loc, target=node_in_set)
                    cur_bot_loc = bot_loc
                    init = True
                this_length = nx.shortest_path_length(G, source=bot_loc, target=node_in_set)
                if this_length < cur_best_length:
                    cur_best_path = nx.shortest_path(G, source=bot_loc, target=node_in_set)
                    cur_best_length = this_length
                    cur_bot_loc = bot_loc
        for i in range(len(cur_best_path)-1):
            mst.add_node(cur_best_path[i])
            mst.add_edge(cur_best_path[i],cur_best_path[i+1])
            set_locs.append(cur_best_path[i])
        bot_exist_locs.remove(cur_bot_loc)
    return mst

def produce_shortest_path_mst(G, bot_locs, client_home):
    bot_exist_locs = bot_locs.copy()
    mst = nx.Graph()
    mst.add_node(client_home)
    while len(bot_exist_locs) > 0:
        init = False
        for bot_loc in bot_exist_locs:
            if not init:
                cur_best_path = nx.shortest_path(G, source=bot_loc, target=client_home)
                cur_best_length = nx.shortest_path_length(G, source=bot_loc, target=client_home)
                cur_bot_loc = bot_loc
                init = True
            this_length = nx.shortest_path_length(G, source=bot_loc, target=client_home)
            if this_length < cur_best_length:
                cur_best_path = nx.shortest_path(G, source=bot_loc, target=client_home)
                cur_best_length = this_length
                cur_bot_loc = bot_loc
        for i in range(len(cur_best_path)-1):
            mst.add_node(cur_best_path[i])
            mst.add_edge(cur_best_path[i],cur_best_path[i+1])
        bot_exist_locs.remove(cur_bot_loc)
    return mst

def mst_remote(mst, client):
    degrees = list(mst.degree)
    while (len(degrees) > 1):
        nodeindex = 0
        lenNodes = len(degrees)
        while nodeindex < lenNodes:
            if degrees[nodeindex][1] == 1 and degrees[nodeindex][0] != client.h:
                break
            nodeindex += 1
        u = degrees[nodeindex][0]
        v = list(mst[u].keys())[0]
        client.remote(u, v)
        mst.remove_node(u)
        degrees = list(mst.degree)
    return 1

def get_leaf_nodes(mst):
    return [x for x in mst.nodes() if len(mst.edges(x)) == 1]

def combinelist(list1, list2):
    combined_list = []
    for x in list1:
        combined_list.append(x)
    for x in list2:
        if x not in list1:
            combined_list.append(x)
    return combined_list
