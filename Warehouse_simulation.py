import pygame
from pygame.locals import *
from path_finding import astar
import numpy
import time
import threading
from queue import Queue
from random import *
import random
import pickle


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
        self.lock = None
        self.actor_size = [9, 9]
        self.actor_png = pygame.image.load("driver image.png")

    def draw_actor(self):
        #print("UPDATE AX/AY:" + str(self.ax) + "/" + str(self.ay))
        screen.blit(self.actor_png, (self.ax, self.ay))
        pygame.display.flip()

    def change_postion(self, ax, ay):
        #print("NEW POSITION: " + str(ax) + "/" + str(ay))
        self.ax = ax
        self.ay = ay

    def get_position(self):
        position = (self.ax, self.ay)
        return position

    def eddit_lock(self, lock):
        self.lock = lock

    def get_lock(self):
        return self.lock

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

    alphabet = []                # Generate the alphabet for vertical point
    for letter in range(97,123):
        alphabet.append(chr(letter))

    for current_rack in racks: # Splits the racking in lock sectors by deviding them into sublists
        if (current_rack[0] == (start_lock[0] + 18*lock)): 
            start_lock = current_rack
            lock_list.append(lock_temp)
            lock_temp = []
        else:
            lock_temp.append(current_rack)

    for sector in lock_list: # For secktor of 'lock' nuber of racks
        print("nNUBER OF SECTORS ARE : " + str(len(lock_list)))
        min_x = sector[0][0] 
        max_x = sector[-1][0]
        min_y = sector[0][1]
        max_y = sector[-1][1]
        number_sector = lock_list.index(sector)
        
        for work in range(batch_quantity): # For number of requred batches
            for items in range(batch_volume): # For number of requred items per batch
                is_racking = True
                while (is_racking == True): # Make sure it doesn't generare picks on the position of the racking
                    x = randrange((min_x + 9), max_x, 9) # Generate random order withing the sector
                    y = randrange(min_y, max_y, 9) 
                    position = (x ,y)
                    vertical_level = random.choice(alphabet) # Vertical level of pick
                    if position not in racks:
                        batches_temp.append((x, y, vertical_level))
                        is_racking = False
                    else:
                        pass
                sector_queues[str(number_sector)].put(batches_temp) # Put the batch in a queue for the specific lock sector
                batches.append(batches_temp)
                batches_temp = []

            

        

    with open('batches', 'wb') as fp:    # Dump the batches genrated last time
        pickle.dump(batches, fp)

    return batches

def worker(picks):

    name =  threading.currentThread().name 
    lock = threading.Lock()
    start = workers[name].get_position()
    start = converter("pixel", start)
    print_lock = threading.Lock() # Locking the print function so that the threads can use it without mixing it up

    condition = threading.Condition()             # Deploy workers one by one
    condition.acquire()
    
    if (start == converter("pixel", (1251, 54))):
        print(name)
        #print("PRINT THIS : " + workers_queue[0] + " / " + name) this is printing for all workers
        while (workers_queue[0] != name):           
            time.sleep(3)
            #print(name + " ? " +  str(workers_queue[0])) #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HERE THE PROBLEM CAN SPOTED

        time.sleep(1)
        print("Deploy " + workers_queue[0]) 
        workers_queue.pop(0)
        print(workers_queue)
        print(workers_queue[0] != name)
    condition.release()

    for task in reversed(picks):
       
        
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
                    #print("Target:" + str(task[0]) + "/" + str(task[1]))
                    #print("Position: " + name + " is " + str(ax) + "/" + str(ay))
                    pass   
                time.sleep(1)
        except:
            with print_lock:
                print("@@@@@@Failed to find a path for: " )
                print("Start :" + str(start[0]) + "/" + str(start[1]))
                print("Goal: " +  str(task[0]) + "/" + str(task[1]))


def worker_thread():
    name =  threading.currentThread().name
    lock = threading.Lock()
    while True:

        lock.acquire()
        queue = workers[name].get_lock()
        a = str(queue)
        #print ("SEE IF THERE IS ANYTHIG WRONG HERE -----queue name: " + a)
        job = sector_queues[a].get()
        lock.release()

        #print("GIVE WORK TO :" + name + " in sector --" + a )
        worker(job)
        sector_queues[queue].task_done() # Makes the thread available again, now that it has completed its job

def job_alocation(order):
    
    for nameWorker in workers_name:      
        print("START THREAD FOR:" + nameWorker)
        t = threading.Thread(target = worker_thread, name= nameWorker) # Define the thread at asign it to go through 'wroker_thread" function when started
        t.daemon =True # Dies when the main thread dies
        t.start()

    start=time.time() # start time for testing
    
    queue = workers[name].get_lock()
    sector_queues[queue].join() # Blocks until all items in the queue have been gotten and processed.
    
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

    # pygame support
    pygame.mouse.set_visible(False)
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
    pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
    pygame.event.clear()

    # map and its static objects in (0 and 1s)
    map, static_obj, racks = map_cord()

    # Generate map with new cordinates
    map =  numpy.array(map)
    #print(map.shape[1]) # shape1 = 37 ////shape0  = 140

    # Setting up settings
    global workers, workers_name, workers_queue, sector_queues
    number_of_workers = 15
    lock = 8
    batch_quantity = 20
    batch_volume = 10
    

    # Create sector job queues
    sector_queues = {}
    for i in range(lock):
        #print("Making  queue with the name of " + str(i))
        sector_queues[str(i)] = Queue()

    # Generate pick batches for a racks lock
    batches = generate_picks(racks, lock, batch_quantity, batch_volume) 

    # Create workers
    workers = {} # Contains workers as instances of class Driver
    workers_name = [] # global for names
    workers_queue = [] # Queue for deployment
    #workers_lock = number_of_workers
    for i in range(number_of_workers + 1):
        name = "worker" + str(i)
        workers_name.append(name)
        workers_queue.append(name)
        workers[name] =  Driver(screen)

    # Alocate lock sector for each worker
    i = 0 # Number of sectors up to the specified in variable lock
    y = 0
    while (number_of_workers != (i + y)):
        if (i == lock):
            i = 0
            y += lock
        name = "worker" + str(i + y)
        print("Lock " + name + " for sector " + str(i))
        workers[name].eddit_lock(str(i))
        print(workers[name].get_lock())
        i += 1


    # Controll thread
    controller_thread()

    # Alocate work
    job_alocation(batches)
    





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