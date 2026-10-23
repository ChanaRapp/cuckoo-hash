# Created based off slides from Shannon Larson - March 11, 2011
# and wikipedia.org/wiki/Cuckoo_hashing  
# and lkozma.net/cuckoo_hashing_visualization

from BitHash import *

# max amounts of loops before concluding that it is likely stuck in a loop and need to rehash
MAX_LOOPS = 20 
     
class CuckooHash(object):
    # initialize both underlying hash tables and a numKeys counter
    def __init__(self, size):      
        self.__hashOne = [None] * size
        self.__hashTwo = [None] * size
        self.__numKeys = 0
    
    # return current number of keys in the entire table - (both combined) 
    def __len__(self): return self.__numKeys
 
    # insert key/data if the key isn't already in the table
    # return False if the key is already in the table, True otherwise
    def insert(self, k, d): 
        # if the key is already in the table, fail to insert and return False
        if self.find(k) is not None: return False   
           
        # keep trying to insert until successful or loops MAX_LOOPS times
        for i in range(MAX_LOOPS):                         
           
            # if the goal position is empty, insert the key, data pair
            if self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)] is None: 
                self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)] = k,d
                self.__numKeys += 1
                return True 
              
            # swap the value in the goal position and the key, data pair that is being inserted 
            displacer = k,d     
            k,d = self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)][0], self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)][1]
         
            # put the new value in its position in the first hash table 
            self.__hashOne[BitHash(k, hashFuncNum=1) % len(self.__hashOne)] = displacer 
            # if the displaced value can go to its position on the second hash table, move it to there
            if self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)] is None: 
                self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)] = k,d
                # increment numKeys 
                self.__numKeys += 1                                                     
                # return success and exit the loop
                return True    
            # swap the value in the goal position and the key, data pair that is being inserted
            displacer = k,d   
            k,d = self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)][0], self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)][1]
            self.__hashTwo[BitHash(k, hashFuncNum=2) % len(self.__hashTwo)] = displacer       
           
        # if exited the loop and without success, assume we are in an infinite cycle
        # choose new hashing functions
        ResetBitHash()                     
        # grow the underlying hash tables - double their size
        self.__grow()   
        # try again with the larger hash tables
        self.insert(k,d)      
        # finished the recursive insert and succeeded in inserting the key,data pair
        return True                                                                     
  
    # return the data if the key is present, None if not
    def find(self, k): 
        # the 2 options where the key could be
        locationOne = BitHash(k, hashFuncNum=1) % len(self.__hashOne) 
        locationTwo = BitHash(k, hashFuncNum=2) % len(self.__hashTwo)
        # if it is in its position on hash table 1
        if self.__hashOne[locationOne] is not None and self.__hashOne[locationOne][0] == k: 
            # return the data
            return self.__hashOne[locationOne][1]                    
            # if it is in its position on hash table 2
        if self.__hashTwo[locationTwo] is not None and self.__hashTwo[locationTwo][0] == k: 
            # return the data
            return self.__hashTwo[locationTwo][1]                                           

    # delete the value if present, if not do nothing. does not return anything because always succeeds
    def delete(self, k):
        # the 2 options where the key could be      
        locationOne = BitHash(k, hashFuncNum=1) % len(self.__hashOne)
        locationTwo = BitHash(k, hashFuncNum=2) % len(self.__hashTwo)
        # if it is in its position on hash table 1
        if self.__hashOne[locationOne] is not None and self.__hashOne[locationOne][0] == k: 
            self.__hashOne[locationOne] = None                                               
            self.__numKeys -= 1                                                   
        # if it is in its position on hash table 2
        elif self.__hashTwo[locationTwo] is not None and self.__hashTwo[locationTwo][0] == k: 
            self.__hashTwo[locationTwo] = None                                               
            self.__numKeys -= 1
    
    def __grow(self):
        # current size of underlying hash tables
        size = len(self.__hashOne)    
        # make a new Cuckoo hash with hash tables of double the size
        newHash = CuckooHash(size*2)            
        # loop through both old hash tables, inserting all values into the new ones 
        for i in range(size):                   
            if self.__hashOne[i] is not None:
                newHash.insert(self.__hashOne[i][0], self.__hashOne[i][1])
        for i in range(len(self.__hashTwo)):
            if self.__hashTwo[i] is not None:
                newHash.insert(self.__hashTwo[i][0], self.__hashTwo[i][1])       
        # set the underlying hash tables to be the new ones
        self.__hashOne = newHash.__hashOne      
        self.__hashTwo = newHash.__hashTwo

    # prints out all key, data pairs as a list. used in visual testing
    def display(self): 
        print('[', end=' ')
        # loop through, printing out all key, data pairs
        for i in range(len(self.__hashOne)):    
            if self.__hashOne[i] is not None:
                print(self.__hashOne[i][0], self.__hashOne[i][1], end=', ')
        for i in range(len(self.__hashTwo)):
            if self.__hashTwo[i] is not None:
                print(self.__hashTwo[i][0], self.__hashTwo[i][1], end=', ') 
        print(']')
