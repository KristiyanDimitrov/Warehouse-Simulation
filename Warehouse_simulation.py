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
        Driver.draw_actor(self)

    def draw_actor(self):
        screen.blit(self.actor_png, (self.ax, self.ay))
        pygame.display.flip()

    def change_postion(self, ax, ay):
        self.ax = ax
        self.ay = ay

    def get_position(self):
        return self.ax, self.ay

def check_surroundings(ax, ay):  # function keeps driver on drivabl areas only ~~~~~~~~ no being called if not manual movement
    driver = (self.ax, self.ay)
    for i in static_obj:
        if driver == i:
            return False

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
    '''
        import pickle
    
        with open('outfile', 'wb') as fp:
            pickle.dump(map, fp)
    
        with open ('outfile', 'rb') as fp:
            itemlist = pickle.load(fp)
        print(itemlist)
    '''
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
"""
a
a
a
a
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaW@@@@@@@@@@@@@@@@@@@@@@@@@@@@OOOOO
a
a
a
a
a
"""
def worker(picks, worker_N):

    lock = threading.Lock()
    ax, ay = workers[worker_N].get_position()
    start = converter("pixel",(ax, ay))

    #print("picks:")
    #print("picks:"picks)

    for task in picks:
        
        print_lock = threading.Lock() # Locking the print function so that the threads can use it without mixing it up
        # Generate path for the goal
        lock.acquire()
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
                warehouse(screen)       # Draw the warehouse
                workers[worker_N].change_postion(ax, ay) # change position
                workers[worker_N].draw_actor()  # Draw the driver
                lock.release()
                with print_lock:
                    print("Target:")
                    print(task)
                    print(str(ax) + "/" + str(ay))
                time.sleep(1)
        except:
            print("Failed to find a path for: " )
            print("Start :")
            print(start)
            print("Goal")
    
    with print_lock:
        print(threading.current_thread().name,'Task')

def worker_thread():
    while True:
        job=q.get()
        print(job)
        worker(job, name)
        q.task_done() # Makes the thread available again, now that it has completed its job

def job_alocation(order):
    

    print(type(workers["worker0"]))
    for nameWorker in workers_name:
        print("Name: " + nameWorker)
        print(type(nameWorker))
        t = threading.Thread(target = worker_thread, name= nameWorker) # Define the thread at asign it to go through 'wroker_thread" function when started
        t.daemon =True # Dies when the main thread dies
        t.start()
    print(type(workers[nameWorker]))
    
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





if __name__ == "__main__":

    # screen size
    screen = pygame.display.set_mode((1260, 333))

    # screen name
    pygame.display.set_caption("Warehouse Simulation")

    # screen background colour (white)
    screen.fill((255, 255, 255))
    pygame.display.flip()

    # Agent spawn position

    warehouse(screen)       # Draw the warehouse

    # Create workers
    number_of_workers = 2
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
    print(map.shape[1]) # shape1 = 37 ////shape0  = 140

    # Generate pick batches for a racks lock
    lock = 8
    batch_quantity = 1
    batch_volume = 1
    batches = generate_picks(racks, lock, batch_quantity, batch_volume)
    print("Number of sectors: " + str(len(batches)))
    
    # Alocate work
    job_alocation(batches)
    
    """
    ISSUES:
        1) when drawing 2 separate workers one over-draws the other
        2) when one task is finished by worker 1 it teleports to worker 2 and caries on from there to it next task




"""
    Run = True
    while Run:
        for event in pygame.event.get():
            # code keeps the window open untill user closes it
            if event.type == pygame.QUIT:
                pygame.quit()
                Run = False

            # code to get cursor position for testing purposes
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                print("Cursor position: ", mouse)

            # code to move actor
            elif event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    if check_surroundings(ax, (ay - 9)) != False:
                        ay -= 9
                if event.key == K_DOWN:
                    if check_surroundings(ax, (ay + 9)) != False:
                        ay += 9
                if event.key == K_LEFT:
                    if check_surroundings((ax - 9), ay) != False:
                        ax -= 9
                if event.key == K_RIGHT:
                    if check_surroundings((ax + 9), ay) != False:
                        ax += 9

                # call room(screen) on every loop so that the display updates and the previous actor position is deleted
                print("Location: " + str(ax) + " // " + str(ay))
                warehouse(screen)
                Driver(screen, ax, ay)

"""

