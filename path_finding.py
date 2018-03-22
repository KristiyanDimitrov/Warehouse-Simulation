import numpy
from heapq import *

def distance(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    return abs(dx) + abs(dy)

def astar(array, start, goal): # array == map // start, goal == typle

    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]

    close_set = set()   # set so it dones't have dublicates
    came_from = {}
    gscore = {start:0}
    fscore = {start:distance(start, goal)}  # the distance from onepoint to another
    oheap = [] #(fscore[start], start)

    heappush(oheap, (fscore[start], start)) # heappush is an ND function 
    
    while oheap:

        current = heappop(oheap)[1] # pops the start and maks it current

        if current == goal:  # check if it's reached the goal
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current) # add to visited
        for i, j in neighbors:       # Generates all the neighbors
            neighbor = current[0] + i, current[1] + j            
            tentative_g_score = gscore[current] + distance(current, neighbor) # adds the so far gscore with the one of the neighbor
            if 0 <= neighbor[0] < array.shape[0]: # if neiggbor[0] isn't bigger than 0 or bigger than the array size (going out of the map)
                if 0 <= neighbor[1] < array.shape[1]:   # shape[0] number if embeded lists, and shape[1] items in each list              
                    if array[neighbor[0]][neighbor[1]] == 1: 
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0): # ????
                continue
               # current g score < g score for neigbor or neighbor not in heap 
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + distance(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))
    #print("FINISH")           
    return False
'''
nmap1 = numpy.array([
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,1,0,1],
    [1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,0,1,1,1,1,0,1,1,1,0,0,0,1,0,0],
    [1,0,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,1,1,1,0,0,0,1],
    [1,1,0,1,0,1,0,1,0,1,1,0,1,0,0,0,0,0,1],
    [1,0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,1,1,1],
    [1,0,0,1,0,1,1,0,0,0,1,0,0,0,1,1,1,0,1],
    [1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1]])

 # (11, 8), (12, 8), (13, 8), (13, 7), (13, 6), (12, 6), (11, 6), (10, 6), (10, 5), (10, 4), (9, 4), (8, 4), (7, 4), (7, 3), (7, 2), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1)

start = (1,1)
goal = (11, 8)
l = len(astar(nmap1, start, goal)) - 1
l = astar(nmap1, start, goal)
print(l)
'''

