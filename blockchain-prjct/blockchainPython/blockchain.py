##### Block Chain ############
##### works locally and i am working on its network #########
##### https://freecoursesite.com/ ######


import functools
import hashlib
import json
from collections import OrderedDict
from block import Block
from transaction import Transaction

G_mining_reward = 10
genes_is_block = Block('',0, 100 ,[] , 0)  # creating first block of blockchain  self, index, previous_hash, transactions, proof, time=time()
blockchain = [genes_is_block]
open_transaction = []
owner = 'Farzaneh'
participants = {'Farzaneh'}   # list of people that participant in transactions


def load_data():
    global blockchain
    global open_transaction
    try:
        with open('blockchain.txt' , mode = 'r') as file:
            file_content = file.readlines()
            global blockchain
            global open_transaction
            blockchain = json.loads(file_content[0][:-1]) # loading whole of blockchain from file   first line is proved transsactions 
            updated_blockchain = []
            for block in blockchain:
                # creating list of transactions : sender , recipient , amount , order is important so first we order them after that add them to blockchain (order is importnt because of hash)
                # updated_block_transaction = [OrderedDict([('sender' , tx['sender']) , ('recipient' , tx['recipient']) , ('amount' , tx['amount'])]) for tx in block['transaction']]
                updated_block_transaction = [Transaction(tx['sender'] , tx['recipient'] , tx['amount'] ) for tx in block['transaction']]
                updated_block = Block(block['previous_hash'],block ['index'],block ['proof'], updated_block_transaction, block['timestamp'])
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transaction = json.loads(file_content[1]) #seecond line is open transactions 
            updated_transaction = []
            for tx in open_transaction:
                # updated_transaction = OrderedDict([('sender' , tx['sender']) , ('recipient' , tx['recipient']) , ('amount' , tx['amount'])])
                updated_transaction = Transaction(tx['sender'] , tx['recipient'] , tx['amount'])  #loosing ordering 
            open_transaction = updated_transaction
    except (IOError, IndexError):
        # Our starting block for the blockchain
        genesis_block = Block('',0, 100 ,[] , 0)
        # Initializing our (empty) blockchain list
        blockchain = [genesis_block]
        # Unhandled transactions
        open_transactions = []
    finally:
        print('Cleanup!')    


def save_data():
    with open('blockchain.txt' , mode = 'w') as file:
        saveable_block = [block.__dict__ for block in [Block(block_el.previous_hash,block_el.index , block_el.proof , [tx.__dict__ for tx in block_el.transaction] ,block_el.timestamp ) for block_el in blockchain]] # order is important
        file.write(json.dumps(saveable_block)) #  first line verified transactions 
        file.write('\n')
        saveable_tx = [tx.__dict__ for tx in open_transaction] # order is important
        file.write(json.dumps (saveable_tx))    # open transactions 


def hash_block(block):
    hashable_block = block.__dict__.copy() # formating block to json needs dictionary converts json cant save class format variables 
    hashable_block ['transaction'] = [tx.to_ordered_dict() for tx in hashable_block['transaction']]
    return hashlib.sha256(json.dumps(hashable_block , sort_keys=True).encode()).hexdigest()


def valid_proof(transaction , last_hash , proof):
    guess = (str(tx.to_ordered_dict() for tx in transaction)+ str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    print(guess_hash) 
    return guess_hash[0:2] == '00' # if condition of valid block is satisfied return hashed value 


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transaction,last_hash , proof):
        proof += 1
    return True     


def get_balance(participants):
    tx_sender = [[tx.amount for tx in block.transaction if tx.sender== participants] for block in blockchain]
    open_tx_sender = [tx.amount for tx in open_transaction if tx.sender== participants]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum , tx_amt: tx_sum + sum (tx_amt) if len(tx_amt) > 0 else tx_sum + 0 , tx_sender , 0)
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0 :
    #         amount_sent += tx[0]
    tx_reciptient = [[tx.amount for tx in block.transaction if tx.recipient== participants] for block in blockchain]
    amount_reciptient = functools.reduce(lambda tx_sum , tx_amt: tx_sum + sum (tx_amt) if len(tx_amt) > 0 else tx_sum + 0 , tx_reciptient , 0)
    return amount_reciptient - amount_sent 


def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transactions):
    sender_balance = get_balance (transactions.sender)
    return sender_balance >= transactions.amount


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transaction])


def add_transaction(recipient,sender = owner , amount = 1.0 ):
    transactions = Transaction (sender , recipient , amount)
    if not verify_transaction(transactions):               
        open_transaction.append(transactions)
        save_data()
        return True
    return False

  
def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = Transaction ('MINING' , owner , G_mining_reward)
    copied_transaction = open_transaction[:]
    open_transaction.append(reward_transaction) #?????????
    block = Block(hashed_block , len(blockchain) , proof , copied_transaction)
    blockchain.append(block)
    return True


def get_transaction_value():
    tx_reciptient = input('Enter the recipient of the transaction: ')
    user_amount  = float (input('your transaction amount please: '))
    return tx_reciptient , user_amount


def get_user_choice():
    user_input = input('Your Choice: ')
    return user_input


def print_blockchain_elements():
    for block in blockchain:
        print('Block is: ' , block)


def verify_chain():
    
    for (block_index , block) in enumerate (blockchain):
        if block_index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[block_index - 1]):
            return False
        if not valid_proof ( block.transaction [:-1] , block.previous_hash , block.proof):
            print('Proof of work is invalid ')
            return False
            
    return True   


waiting_for_input = True


while waiting_for_input: 
    print ('please choose: ')
    print ('1: Add a new transaction value:  ')
    print ('2: mining blocks ')
    print ('3: print blocks ')
    print ('4: participants')
    print ('5: check transaction validity')
    print ('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient , amount = tx_data
        if add_transaction(recipient , amount = amount):
            print ( 'Added transaction')
        else:
            print ('transaction failed')   
        print (open_transaction)
    elif user_choice == '2':
        if mine_block() :
            open_transaction = []
            save_data()     
    elif user_choice == '3':
        print_blockchain_elements()  
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print ('All transaction are valid')
        else:
            print('there are invalid transaction')    
  
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list: ')    
    # if not verify_chain():
    #     print('Invalid blockchain !')
    #     break
    print ('Balance of {} : {:6.2f} '.format('Farzaneh' ,get_balance('Farzaneh')))    
else:
    print( '-' * 20 )
print('done')