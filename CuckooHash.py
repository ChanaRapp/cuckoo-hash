#I hereby certify that this program is solely the result of my own work, without referencing source code from any source, and is in compliance with the Academic Integrity policy of the course syllabus and the academic integrity policy of the CS department

# Created based off slides from Shannon Larson - March 11, 2011
# and wikipedia.org/wiki/Cuckoo_hashing  
# and lkozma.net/cuckoo_hashing_visualization

import pytest
import random
from BitHash import *
   
MAX_LOOPS = 20 # max amounts of loops before concluding that it is likely stuck in a loop and need to rehash
     
class CuckooHash(object):
    def __init__(self, size):       # initialize both underlying hash tables and a numKeys counter
        self.__hashOne = [None] * size
        self.__hashTwo = [None] * size
        self.__numKeys = 0
    
    # return current number of keys in the entire table - (both combined) 
    def __len__(self): return self.__numKeys
 
    # insert key/data if the key isn't already in the table
    # return False if the key is already in the table, True otherwise
    def insert(self, k, d): 
        if self.find(k) is not None: return False                                       # if the key is already in the table, fail to insert and return False
        for i in range(MAX_LOOPS):                                                      # keep trying to insert until successful or loops MAX_LOOPS times
            if self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)] is None: # if the goal position is empty, insert the key, data pair
                self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)] = k,d
                self.__numKeys += 1                                                     # increment numKeys 
                return True                                                             # return success and exit the loop         
            displacer = k,d                                                             # swap the value in the goal position and the key, data pair that is being inserted
            k,d = self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)][0], self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)][1]
            self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)] = displacer # put the new value in its position in the first hash table
            if self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)] is None: # if the displaced value can go to its position on the second hash table, move it to there
                self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)] = k,d
                self.__numKeys += 1                                                     # increment numKeys 
                return True                                                             # return success and exit the loop      
            displacer = k,d                                                             # swap the value in the goal position and the key, data pair that is being inserted
            k,d = self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)][0], self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)][1]
            self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)] = displacer            
        # if exited the loop and without success, assume we are in an infinite cycle
        ResetBitHash()                                                                  # choose new hashing functions
        self.__grow()                                                                   # grow the underlying hash tables - double their size
        self.insert(k,d)                                                                # try again with the larger hash tables
        return True                                                                     # finished the recursive insert and succeeded in inserting the key,data pair
  
    # return the data if the key is present, None if not
    def find(self, k): 
        # the 2 options where the key could be
        locationOne = BitHash(k, hashFuncNum=1) % len(self.__hashOne) 
        locationTwo = BitHash(k, hashFuncNum=2) % len(self.__hashTwo)
        
        if self.__hashOne[locationOne] is not None and self.__hashOne[locationOne][0] == k: # if it is in its position on hash table 1
            return self.__hashOne[locationOne][1]                                           # return the data
        if self.__hashTwo[locationTwo] is not None and self.__hashTwo[locationTwo][0] == k: # if it is in its position on hash table 2
            return self.__hashTwo[locationTwo][1]                                           # return the data

    def delete(self, k): # delete the value if present, if not do nothing. does not return anything because always succeeds
        # the 2 options where the key could be      
        locationOne = BitHash(k, hashFuncNum=1) % len(self.__hashOne)
        locationTwo = BitHash(k, hashFuncNum=2) % len(self.__hashTwo)
        if self.__hashOne[locationOne] is not None and self.__hashOne[locationOne][0] == k:   # if it is in its position on hash table 1
            self.__hashOne[locationOne] = None                                                # set the position in the hash table to None
            self.__numKeys -= 1                                                               # decrement numKeys
        elif self.__hashTwo[locationTwo] is not None and self.__hashTwo[locationTwo][0] == k: # if it is in its position on hash table 2
            self.__hashTwo[locationTwo] = None                                                # set the position in the hash table to None
            self.__numKeys -= 1                                                               # decrement numKeys           
    
    def __grow(self):
        size = len(self.__hashOne)              # current size of underlying hash tables
        newHash = CuckooHash(size*2)            # make a new Cuckoo hash with hash tables of double the size
        for i in range(size):                   # loop through both old hash tables, inserting all values into the new ones
            if self.__hashOne[i] is not None:
                newHash.insert(self.__hashOne[i][0], self.__hashOne[i][1])
        for i in range(len(self.__hashTwo)):
            if self.__hashTwo[i] is not None:
                newHash.insert(self.__hashTwo[i][0], self.__hashTwo[i][1])        
        self.__hashOne = newHash.__hashOne      # set the underlying hash tables to be the new ones
        self.__hashTwo = newHash.__hashTwo
        
    def display(self): # prints out all key, data pairs as a list. used in visual testing
        print('[', end=' ')
        for i in range(len(self.__hashOne)):    # loop through, printing out all key, data pairs
            if self.__hashOne[i] is not None:
                print(self.__hashOne[i][0], self.__hashOne[i][1], end=', ')
        for i in range(len(self.__hashTwo)):
            if self.__hashTwo[i] is not None:
                print(self.__hashTwo[i][0], self.__hashTwo[i][1], end=', ') 
        print(']')