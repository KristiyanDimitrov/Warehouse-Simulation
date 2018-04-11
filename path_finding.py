import numpy
from heapq import *
import time

def hscore(a, b):  # the distance from one point to another ( in this case from start node to end goal)
    dx, dy = b[0] - a[0], b[1] - a[1]
    return abs(dx) + abs(dy)

def astar(array, start, goal, red, green, in_rackings, previous): # array == map // start, goal == typle
    #print(" GOAL IS : " + str(goal))
    #print("IN_RAVKINGS IS :" + str(in_rackings))
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
    close_set = set()   # set so it dones't have dublicates
    came_from = {}
    gscore = {start:0} # hscore from starting node
    fscore = {start:hscore(start, goal)} # Usually used for diagonal movement but not in here (by combining hcost and gcost)
    oheap = []
    heappush(oheap, (fscore[start], start)) # heappush is an ND function 
    
    

    while oheap:

        if  previous == None:
            previous = []
        elif len(close_set) > 2:
            previous = [previous[-1]]

        if len(close_set) != 0: # don't set up previous if its the first itteration
            previous.append(current)

        sorted(oheap,key=lambda l:l[1], reverse=True) # Sort to be able to pop the lowest h score
        current = heappop(oheap)[1] # pops the start and maks it current

        if current == goal:  # check if it's reached the goal and returns the path
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current][0]
                in_rackings = (in_rackings[0], True) 
            return data, in_rackings, previous

        close_set.add(current) # add to visited
        adjacent = []
        for i, j in neighbors:      # Generates all the neighbors
            neighbor = current[0] + i, current[1] + j
           

            #print( "TENTATIVE G SCORE FROM " + str(current) + " to " + str(neighbor)
            tentative_g_score = hscore(start, neighbor) # adds the so far gscore with the one of the neighbor for total value of travel
            if 0 <= neighbor[0] < array.shape[0]: # if neiggbor[0] isn't bigger than 0 or bigger than the array size (going out of the map)
                if 0 <= neighbor[1] < array.shape[1]:   # shape[0] number if embeded lists, and shape[1] number items in each list              
                    if array[neighbor[0]][neighbor[1]] == 1 or neighbor in previous: 
                        continue # Skip the remaining code of the for lopp
                else:
                    # array is on y walls
                    continue # Skip the remaining code of the for lopp
            else:
                # array is on x walls
                continue # Skip the remaining code of the for lopp
            
            #print(in_rackings)
            #print("cheking out :" + str(neighbor))
          
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0): # if the location has been explored and if the current tota cost is bigger, skip the update
                continue

            # ~~~~~~~~~~~~~~~~~~~~~~ KEEP IF NEEDED TO BACK TO THIS SOLUTION ~~~~~~~~~~~~~~~~~~~~
            """
            if ((in_rackings[1] == True) and (neighbor not in close_set)): # If a new reakicng entry gets checked out and then passed, change in_racking to False
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!________________________!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(in_rackings)
                print(neighbor)
                print(neighbor[0] != in_rackings[0][0])
                print(in_rackings[1] == True)
                print("ALTER IN RACKING TO FALSE")
                in_rackings = (in_rackings[0], False)
"""

            if neighbor in red and in_rackings[1] == False: # If outside the racking, can't enter through the red
                #print("Can't enter red at: " + str(neighbor)) 
                continue
            elif (neighbor in red) and (in_rackings[1] == True) and (neighbor[0] == in_rackings[0][0]): # Exit the racking
                #print("Exiting red at: " + str(neighbor))
                #print(in_rackings)
                in_rackings = (neighbor, False)
            elif (neighbor in green) and (in_rackings[1] == True) and (in_rackings[0] == neighbor): # If inside the rakcing, can't exit through green
                #print("Can't exit green at: " + str(neighbor))
                continue
            elif (neighbor in green and neighbor != in_rackings[0]): # Enter the racking
                #print("Enter green at: " + str(neighbor))
                in_rackings = (neighbor, True)
            elif (neighbor in red):
                 #print("Can't enter red at: " + str(neighbor))
                 pass
                 continue

            
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]: # Log the neighbor
                came_from[neighbor] = (current, in_rackings[1])
                gscore[neighbor] = tentative_g_score
                #print("neighbor:" + str(neighbor))
                #print(str(tentative_g_score) +"//" + str(hscore(neighbor, goal)))
                #time.sleep(3)
                fscore[neighbor] = tentative_g_score + hscore(neighbor, goal)
                #print((fscore[neighbor], neighbor))
                adjacent.append((fscore[neighbor], neighbor))

            try:
                temp = (adjacent[0][0], adjacent[0][1])
            except:
                continue

            while len(adjacent) != 0:                       # Append neghbors to queue in order of proximity to goal
                for adjacent_location in adjacent:
                    if adjacent_location[0] < temp[0]:
                        temp = adjacent_location
                heappush(oheap, adjacent[adjacent.index(temp)])
                adjacent.remove(adjacent[adjacent.index(temp)])
        


    print("COUDN'T FIND PATH!")
    return False

