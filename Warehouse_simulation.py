import pygame
from pygame.locals import *
from path_finding import astar
from path_finding import hscore
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
        self.previous = None
        self.actor_size = [9, 9]
        self.in_racking = ((self.ax, self.ay),False)
        self.actor_png = pygame.image.load("driver image.png")
        self.tote_number = max_tote_number
        self.tote_inventory = 0
        self.full_totes = 0

    def draw_actor(self):
        screen.blit(self.actor_png, (self.ax, self.ay))
        pygame.display.flip()

    def change_postion(self, ax, ay):
        self.ax = ax
        self.ay = ay

    def get_position(self):
        position = (self.ax, self.ay)
        return position

    def eddit_lock(self, lock):
        self.lock = lock

    def get_lock(self):
        return self.lock

    def set_in_racking(self, in_racking, previous):
        self.in_racking = in_racking
        self.previous = previous

    def get_in_racking(self):
        return self.in_racking, self.previous

    def update_tote(self,tote_number, tote_inventory, full_totes):
        self.tote_number = tote_number
        self.tote_inventory = tote_inventory
        self.full_totes = full_totes

    def info_tote(self):
        return self.tote_number, self.tote_inventory, self.full_totes

def warehouse(screen):
    """
    Draw the map
    """
    bg = pygame.image.load("Map_T.png")
    screen.blit(bg, (0, 0))
    pygame.display.flip()

def map_cord():
    # Map
    map = []
    racks = []
    # Entrance // Exit
    red = []
    green = []
    # Drop zones
    drop_zone_1 = ((7 ,2), ( (3 ,2),(4 ,2),(5 ,2),(6 ,2),(7 ,2),(8 ,2),(9 ,2),(10 ,2),(11 ,2),(12 ,2)))
    drop_zone_3 = ((133 ,2), ((136 ,2),(135 ,2),(134 ,2),(133 ,2),(132 ,2),(131 ,2),(130 ,2)))
    drop_zone_2 = ((88 ,2), ( (84 ,2),(85 ,2),(86 ,2),(87 ,2),(88 ,2),(89 ,2),(90 ,2),(91 ,2),(92 ,2),(93 ,2)))
    drop_zones = (drop_zone_1[1] + drop_zone_2[1] + drop_zone_3[1])
    

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
    
    for i in range (9 , 1215 , 9): # Space not accessible arround on drop zone level
        if converter("pixel", (i, 18)) not in drop_zones:
            static_obj.append((i, 18 ))
     

    for i in range (18, 1215, 18):
        for y in range (63, 288, 9):
            static_obj.append((i, y)) # all the racks
            racks.append((i, y))
    # Exit // Entry
    for i in range (9, 1215, 36): # All the red exits
        red.append((i, 63))
    for i in range (27, 1215, 36): # All the red exits
        red.append((i, 279))

    for i in range (27, 1215, 36): # All the green
        green.append((i, 63))
    for i in range (9, 1215, 36): # All the green
        green.append((i, 279))


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

    return (map, static_obj, racks, red, green, drop_zone_1, drop_zone_2, drop_zone_3, drop_zones)

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

def generate_picks(alphabet,racks, lock, batch_quantity, batch_volume):
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
        #print("nNUBER OF SECTORS ARE : " + str(len(lock_list)))
        min_x = sector[0][0] 
        max_x = sector[-1][0]
        min_y = sector[0][1]
        max_y = sector[-1][1]
        number_sector = lock_list.index(sector)
        
        for work in range(batch_quantity): # For number of requred batches
            for items in range(batch_volume): # For number of requred items per batch
                is_racking = True
                while (is_racking == True): # Make sure it doesn't generare pick on the position of the racking
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
                batches.append([batches_temp, str(number_sector)])
                batches_temp = []
  

    with open('batches', 'wb') as fp:    # Dump the batches genrated last time
        pickle.dump(batches, fp)

    return batches

def worker(pick, drop):

    global all_deployed
    name =  threading.currentThread().name 
    lock = threading.Lock()
    start = workers[name].get_position()
    tote_number, tote_inventory, full_totes = workers[name].info_tote()
    start = converter("pixel", start)
    print_lock = threading.Lock() # Locking the print function so that the threads can use it without mixing it up

    if (full_totes > max_full_tote or tote_number == 0):   # If the worker needs to drop --- Find the closest drop zone and go drop
        zone_1 = hscore(start, drop_zone_1[0])
        zone_2 = hscore(start, drop_zone_2[0])
        zone_3 = hscore(start, drop_zone_3[0])
        closest_zone = min(z for z in (zone_1, zone_2, zone_3))
        if (closest_zone == zone_1):
            closest_zone = drop_zone_1[0]
        elif (closest_zone == zone_2):
            closest_zone = drop_zone_2[0]
        else:
            closest_zone = drop_zone_3[0]
        closest_zone = converter("bin", closest_zone)
        closest_zone = (closest_zone[0], closest_zone[1], "a") # passig the drop zone in the format of a pick so no ajustments need to be made in order to handle it
        workers[name].update_tote(max_tote_number, 0, 0) # reseting worker as he is dropping everythig off #drop totes
        worker([closest_zone], True) 
        time.sleep(10)
    
    # Deploy workers one by one and set up some base variables
    condition = threading.Condition()             
    condition.acquire()
    if (start == converter("pixel", (1251, 54))):
        while (workers_queue[0] != name):           
            time.sleep(3)

        time.sleep(1)
        print("Deploy " + workers_queue[0]) 
        workers_queue.pop(0)
    condition.release()
    if (name[6:] == str(number_of_workers - 1)):
        print("All workers deployed!")
        all_deployed = True


    # Generate path for the goal
    lock.acquire()
    start = workers[name].get_position()
    start = converter("pixel", start)

    pick = (converter("pixel", (pick[0][0], pick[0][1])), pick[0][2])
    in_racking, previous =  workers[name].get_in_racking()
    in_racking = (converter('pixel', in_racking[0]), in_racking[1])
    path, in_racking, previous = astar(map, start, pick[0], red, green, in_racking, previous)
    workers[name].set_in_racking((converter('bin', in_racking[0]), in_racking[1]), previous)
    
    # print(path)
    lock.release()
     
    # keeping track of in/out of racking for being able to move vertically
    in_racking = False
    time_in_racking = 0


    # Reaching the goal
    for i in reversed(path):
        y = converter('bin', i)
        ax = y[0]
        ay = y[1]
        
        # Dealing with agents that have other agents in their path
        lock.acquire()
        global positions_taken
        total_wait_time = 0
        jam_time = [0, 0] # How much time to wait before trying an alternative path
        while (all_deployed == True): # If two workers are facing eachother, one moves aside to et the other one go ( all deployes instead of True because is should work before all are deployed)
            
            current_state = workers[name].get_position()
            wait = True
            for position in positions_taken:
                if current_state != position and position == (ax, ay) or position == converter('bin' ,path[path.index(i) - 1]) or position == converter('bin' ,path[path.index(i) - 2]) :
                    wait = False
            if (wait == True):
                break
            else:
                if  (in_racking == False):
                    jam_time[0] += 1
                    
                time.sleep(1)
                total_wait_time += 1
            
            if (jam_time[0] == 2):
                jam_time[0] = 0
                jam_time[1] += 1

                if (jam_time[1] == 2) or total_wait_time > 20:
                    break

                global static_obj
                try_side = randint(0,1)
                if  (((ax, ay + 9) not in static_obj) and try_side == 0):
                    workers[name].change_postion(ax, ay + 9)
                    ay += 9
                    time.sleep(random.randint(0, 3))
                elif  (((ax, ay - 9) not in static_obj) and try_side == 1):                           
                    workers[name].change_postion(ax - 9, ay)
                    ax -= 9
                    time.sleep(random.randint(0, 3))
                elif  (((ax, ay + 9) not in static_obj) and try_side == 0):                           
                    workers[name].change_postion(ax + 9, ay)
                    ax += 9
                    time.sleep(random.randint(0, 3))
                elif  (((ax, ay - 9) not in static_obj) and try_side == 1):                           
                    workers[name].change_postion(ax, ay - 9)
                    ay -= 9
                    time.sleep(random.randint(0, 3))

        # Increase time in racking for moving vertically as well as horizontally
        if (  converter("pixel",(ax, ay)) in green):
            in_racking = True
            if time_in_racking < alphabet.index(vertical_level_rule):
                time_in_racking += 1   
        elif ( converter("pixel",(ax, ay)) in red):
            in_racking = False
            sleep_time = alphabet.index(pick[1]) - time_in_racking
            time_in_racking = 0
        elif (in_racking == True): 
            if time_in_racking < alphabet.index(vertical_level_rule):
                time_in_racking += 1

        
        # Vertical movement
        if  ( converter("pixel", (ax, ay)) == (pick[0][0], pick[0][1]) ): 
            sleep_time = max ((alphabet.index(pick[1]) - time_in_racking) + (alphabet.index(pick[1]) - alphabet.index(vertical_level_rule)), 0) # Max in case it is < 0 *sleeps forever
            sleep_time = (sleep_time * 0.5) + 5 + randint(0,5)   # each vertical movement take (0.5) + pick time (5 sec) + human factor(0-5 sec)
            time_in_racking = 0

            tote_inventory += 1
            if tote_inventory == max_tote_inventory:
                tote_inventory = 0
                tote_number -= 1
                full_totes += 1
            workers[name].update_tote(tote_number, tote_inventory, full_totes)
            time.sleep(sleep_time)

        # If worker enteres the drop zone 
        if ( ( drop == True) and (converter("pixel", (ax, ay)) in drop_zones ) ): 
            workers[name].change_postion(ax, ay) # change position
            time.sleep(5)
            break

        workers[name].change_postion(ax, ay) # change position
        lock.release()

        with print_lock:
            #print("Target:" + str(pick[0][0]) + "/" + str(pick[0][1]))
            #print("Position: " + name + " is " + str(converter("pixel", (ax, ay))))
            pass   
        time.sleep(1)

def worker_thread():
    name =  threading.currentThread().name
    lock = threading.Lock()
    while True:

        lock.acquire()
        queue = str(workers[name].get_lock())
        job = sector_queues[queue].get()
        lock.release()

        worker(job, False)
        sector_queues[queue].task_done() # Makes the thread available again, now that it has completed its job

def job_alocation(order):
    
    for nameWorker in workers_name:      
        t = threading.Thread(target = worker_thread, name= nameWorker) # Define the thread at asign it to go through 'wroker_thread" function when started
        t.daemon =True # Dies when the main thread dies
        t.start()

    start=time.time() # start time for testing
    
    queue = workers[name].get_lock()
    sector_queues[queue].join() # Blocks until all items in the queue have been gotten and processed.
    
    print('Entire job took:', time.time()-start)
    

def controller_thread():
    c = threading.Thread(target = Draw_main, name= "Draw_thread")
    c.daemon =True # Dies when the main thread dies
    c.start()

def Draw_main():
    global positions_taken
    
    starttime=time.time()
    while True:
        warehouse(screen)       # Draw the warehouse
        positions_taken = []
        for worker in workers_name:
            positions_taken.append(workers[worker].get_position())
            workers[worker].draw_actor()  # Draw the driver
        time.sleep(1.0 - ((time.time() - starttime) % 1.0))
        

if __name__ == "__main__":

    # set up global vars
    global workers, workers_name, workers_queue, sector_queues, old_batch, all_deployed, static_obj
    global red, green, vertical_level_rule, drop_zone_1, drop_zone_2, drop_zone_3, max_tote_number, max_tote_inventory, max_full_tote, drop_zones

    # screen size
    screen = pygame.display.set_mode((1260, 333))

    # screen name
    pygame.display.set_caption("Warehouse Simulation")

    # screen background colour (white)
    screen.fill((255, 255, 255))
    pygame.display.flip()

    # map and its static objects in (0 and 1s)
    map, static_obj, racks, red, green, drop_zone_1, drop_zone_2, drop_zone_3, drop_zones = map_cord()
    
    # Coverting the coordinates of the green and red felds
    for feld in green:
        green[green.index(feld)] = converter('pixel', feld)
    for feld in red:
        red[red.index(feld)] = converter('pixel', feld)

    # Generate map with new cordinates
    map =  numpy.array(map)


    # Setting up settings  
    number_of_workers = 20
    lock = 8
    vertical_level_rule = "k"
    max_tote_number = 12
    max_tote_inventory = 10
    max_full_tote = 15
    batch_quantity = 200
    batch_volume = 40
    old_batch = True  # Using old batch is when this variable is 'True'
    all_deployed = False

    # Create sector job queues
    sector_queues = {}
    for i in range(lock):
        #print("Making  queue with the name of " + str(i))
        sector_queues[str(i)] = Queue()

    
    # Generate the alphabet for vertical point
    alphabet = []                
    for letter in range(97,123):
        alphabet.append(chr(letter))

    # Generate pick batches for a racks lock or uses old load
    if (old_batch == False):
        batches = generate_picks(alphabet, racks, lock, batch_quantity, batch_volume)
    else:
        with open('batches', 'rb') as fp:
            batches = pickle.load(fp)

        for order in batches:
            sector_queues[order[1]].put(order[0]) # Feeding work from previously generated batch

    # Create workers
    workers = {} # Contains workers as instances of class Driver
    workers_name = [] # global for names
    workers_queue = [] # Queue for deployment
    #workers_lock = number_of_workers
    for i in range(number_of_workers):
        name = "worker" + str(i)
        workers_name.append(name)
        workers_queue.append(name)
        workers[name] =  Driver(screen)

    # Alocate lock sector for each worker
    i = 0 # Number of sectors up to the specified in variable lock
    y = 0
    while ((number_of_workers ) > (i + y)):
        if (i == lock):
            i = 0
            y += lock
        name = "worker" + str(i + y)
        print("Lock " + name + " for sector " + str(i))
        workers[name].eddit_lock(str(i)) 
        print(workers[name].get_lock())
        i += 1
    print("EDDITED POSITION FOR NUMBER OF WORKERS : " + str((i + y)))


    # Controll thread
    controller_thread()

    # Alocate work
    job_alocation(batches)