from time import time

class Block:
    def __init__(self , previous_hash, index  , proof, transactions , time = time()):
        self.index = index
        self.previous_hash = previous_hash
        self.proof = proof
        self.transaction = transactions 
        self.timestamp = time

        self, index, previous_hash, transactions, proof, time=time()