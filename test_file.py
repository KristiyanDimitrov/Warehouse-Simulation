import pygame
from pygame.locals import *
from path_finding import astar
import numpy
import time
import threading
from queue import Queue
from random import *

nameWorker = "worker5"
print ("aaaaa")
clock.tick(int(nameWorker[6:]))
print("bbbbb")


    event = threading.Event()
    lock.acquire()
    if (start == (1251, 54)):
        print(workers_queue[0] + " ? " +  name)
        while (workers_queue[0] != name):
             event.wait()
        print("AAAAAAAAAAAAAAAA")
        workers_queue.pop(0)
        event.set(1)
        lock.release()




        alphabet = []                # Generate the alphabet for vertical point
    for letter in range(97,123):
        alphabet.append(chr(letter))

        with open('batches', 'wb') as fp:    # Dump the batches genrated last time
        pickle.dump(batches, fp)




                print("tick " + str(pygame.time.get_ticks()))


                import random
import pickle
