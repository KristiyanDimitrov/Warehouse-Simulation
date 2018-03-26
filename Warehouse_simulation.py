import pygame
from pygame.locals import *
from path_finding import astar
import numpy
import time
import threading
from queue import Queue
from random import *

q = Queue()

print("Starting the simulation!")
pygame.init()

class Shape:  # class for drawing the screen

    def __init__(self, screen, color, x, y, l, h):
        self.screen = screen
        self.color = color
        self.x = x
        self.y = y
        self.l = l
        self.h = h
        Shape.draw_shape(self)

    def draw_shape(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.l, self.h))
        pygame.display.flip()

class Driver:

    def __init__(self, screen):
        self.screen = screen
        self.ax = 1251
        self.ay = 54
        self.actor_size = [9, 9]
        self.actor_png = pygame.image.load("driver image.png")

    def draw_actor(self):
        #print("UPDATE AX/AY:" + str(self.ax) + "/" + str(self.ay))
        screen.blit(self.actor_png, (self.ax, self.ay))
        pygame.display.flip()

    def change_postion(self, ax, ay):
        print("NEW POSITION: " + str(ax) + "/" + str(ay))
        self.ax = ax
        self.ay = ay

    def get_position(self):
        position = (self.ax, self.ay)
        return position







def warehouse(screen):
    """
    Draw the map
    """
    bg = pygame.image.load("Map_T.png")
    screen.blit(bg, (0, 0))
    pygame.display.flip()

def map_cord():
     # map
    map = []
    racks = []
   

    # Static objects not drivable on ( must be typels )
    static_obj = []
    
    for i in range(0, 333, 9):
        static_obj.append((0, i)) # walls left
    
    for i in range(0, 1260, 9):
        static_obj.append((i, 0)) # walls right
    
    for i in range(0, 1260, 9):
        static_obj.append((i, 315)) # walls bottom
    
    for i in range(0, 333, 9):
        static_obj.append((1251, i)) # walls top
    
    # (1206, 63) - (18, 63)
    # (18, 63) - (18, 288)
    for i in range (18, 1215, 18):
        for y in range (63, 288, 9):
            static_obj.append((i, y)) # all the racks
            racks.append((i, y))

    line = []
    incr = 0
    for i in range(0, 1260, 9):
        incr += 1
        for y in range(0, 333, 9):
            if ((i, y) in static_obj):
                line.append(1)
            else:
                line.append(0)
        map.append(line)
        line = []

    return (map, static_obj, racks)

def converter(type, location):
    new_type = [0, 0]
    if (type == "pixel"):       
        new_type[0] = location[0] / 9
        new_type[1] = location[1] / 9
    elif (type == "bin"):
        new_type[0] = location[0] * 9
        new_type[1] = location[1] * 9
    new = (new_type[0],new_type[1])
    return new

def generate_picks(racks, lock, batch_quantity, batch_volume):
    count_racks = 0
    lock_list = []
    lock_temp = []
    start_lock = racks[0]
    batches_temp = []
    batches = []

    for current_rack in racks: # Splits the racking in lock sectors by deviding them into sublists
        if (current_rack[0] == (start_lock[0] + 18*lock)): 
            start_lock = current_rack
            lock_list.append(lock_temp)
            lock_temp = []
        else:
            lock_temp.append(current_rack)

    for sector in lock_list: # For secktor of 'lock' nuber of racks
        min_x = sector[0][0] 
        max_x = sector[-1][0]
        min_y = sector[0][1]
        max_y = sector[-1][1]
        
        for work in range(batch_quantity): # For number of requred batches
            for items in range(batch_volume): # For number of requred items per batch
                x = randint(min_x, max_x) # Generate random order withing the sector
                y = randint(min_y, max_y) 
                batches_temp.append((x, y))
        batches.append(batches_temp)
        batches_temp = []
    return batches

def worker(picks):

    name =  threading.currentThread().name
    lock = threading.Lock()
    start = workers[name].get_position()
    start = converter("pixel", start)



    for task in reversed(picks):
        
        print_lock = threading.Lock() # Locking the print function so that the threads can use it without mixing it up
        # Generate path for the goal
        lock.acquire()
        start = workers[name].get_position()
        start = converter("pixel", start)
        task = converter("pixel", task)
        path = astar(map, start, task)
        lock.release()
        
        # reach the goal
        try:
            for i in reversed(path):
                y = converter('bin', i)
                ax = y[0]
                ay = y[1]
       
                lock.acquire()
                #
                workers[name].change_postion(ax, ay) # change position
                #
                lock.release()
                with print_lock:
                    print("Target:" + str(task[0]) + "/" + str(task[1]))
                    print("Position: " + name + " is " + str(ax) + "/" + str(ay))   
                time.sleep(1)
        except:
            with print_lock:
                print("@@@@@@Failed to find a path for: " )
                print("Start :" + str(start[0]) + "/" + str(start[1]))
                print("Goal: " +  str(task[0]) + "/" + str(task[1]))
    

def worker_thread():
    while True:
        job=q.get()
       # print("GIVE WORK TO :" + name)
        worker(job)
        q.task_done() # Makes the thread available again, now that it has completed its job

def job_alocation(order):
    

    for nameWorker in workers_name:      
        print("START THREAD FOR:" + nameWorker)
        t = threading.Thread(target = worker_thread, name= nameWorker) # Define the thread at asign it to go through 'wroker_thread" function when started
        t.daemon =True # Dies when the main thread dies
        t.start()

    start=time.time() # start time for testing
    
    for job in order:
        q.put(job)
    
    q.join() # Blocks until all items in the queue have been gotten and processed.
    
    print('Entire job took:', time.time()-start)
    
    
    """ 
    ln(24) define and create threads that go thrrough...
    ln(13) where they constantly wait for jobs to get from the queue 
    At this point they are active and waiting so on...
    ln(32) we add all the jobs to get finished and on...
    ln(35) we wait for the queue to be empty"""


def controller_thread():
    c = threading.Thread(target = Draw_main, name= "Draw_thread")
    c.daemon =True # Dies when the main thread dies
    c.start()


def Draw_main():

    starttime=time.time()
    while True:
        warehouse(screen)       # Draw the warehouse
        for worker in workers_name:
            workers[worker].draw_actor()  # Draw the driver
        time.sleep(1.0 - ((time.time() - starttime) % 1.0))
        

   


if __name__ == "__main__":

    # screen size
    screen = pygame.display.set_mode((1260, 333))

    # screen name
    pygame.display.set_caption("Warehouse Simulation")

    # screen background colour (white)
    screen.fill((255, 255, 255))
    pygame.display.flip()

    # Agent spawn position

    #

    # Create workers
    number_of_workers = 6
    global workers, workers_name
    workers = {}
    workers_name = []
    for i in range(number_of_workers):
        name = "worker" + str(i)
        workers_name.append(name)
        workers[name] =  Driver(screen)

    # map and its static objects in (0 and 1s)
    map, static_obj, racks = map_cord()

    # Generate map with new cordinates
    map =  numpy.array(map)
    #print(map.shape[1]) # shape1 = 37 ////shape0  = 140

    # Generate pick batches for a racks lock
    lock = 8
    batch_quantity = 4
    batch_volume = 3
    batches = generate_picks(racks, lock, batch_quantity, batch_volume)
    #print("Number of sectors: " + str(len(batches)))
    
    # Controll thread
    controller_thread()

    # Alocate work
    job_alocation(batches)
    



    # RESOLVE BY MAKING ANOTHER THREAD THAT W8S FOR ALL THE OTHER THREADS TO SAY THEY ARE READY SO IT CAN DRAW THE MAP AND ALL OF THEM


'''
    import pickle

    with open('outfile', 'wb') as fp:
        pickle.dump(map, fp)

    with open ('outfile', 'rb') as fp:
        itemlist = pickle.load(fp)
    print(itemlist)
'''

'''class Draw:

def __init_(self, names):
    self.workers_position = {}
    for name in names:
        self.workers_position[name] = (0, 0)

def set_worker_position(name, position):
    slef.workers_position[name] = position


def get_wrokers_position():
    return self.workers_positio
'''