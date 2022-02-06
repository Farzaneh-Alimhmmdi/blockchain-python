##### Block Chain ############
##### works locally and i am working on its network #########
##### https://freecoursesite.com/ ######


import functools
import hashlib
import json
from collections import OrderedDict

G_mining_reward = 10
genes_is_block = {
    'previous_hash' : '',
    'index' : 0,
    'transaction' : [],
    'proof' : 100
}
blockchain = [genes_is_block]
open_transaction = []
owner = 'Farzaneh'
participants = {'Farzaneh'}


def load_data():
    with open('blockchain.txt' , mode = 'r') as file:
        file_content = file.readlines()
        global blockchain
        global open_transaction
        blockchain = json.loads(file_content[0][:-1])
        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash' : block['previous_hash'],
                'index' : block ['index'],
                'proof' : block ['proof'],
                'transaction' : [OrderedDict(
                    [('sender' , tx['sender']) , ('recipient' , tx['recipient']) , ('amount' , tx['amount'])]) for tx in block['transaction']]
            }
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain
        open_transaction = json.loads(file_content[1])
        updated_transaction = []
        for tx in open_transaction:
            updated_transaction = OrderedDict(
                    [('sender' , tx['sender']) , ('recipient' , tx['recipient']) , ('amount' , tx['amount'])])
        open_transaction = updated_transaction


def save_data():
    with open('blockchain.txt' , mode = 'w') as file:
        file.write(json.dumps(blockchain))
        file.write('\n')
        file.write(json.dumps (open_transaction))    


def hash_block(block):
    return hashlib.sha256(json.dumps(block , sort_keys=True).encode()).hexdigest()


def valid_proof(transaction , last_hash , proof):
    guess = (str(transaction)+ str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transaction,last_hash , proof):
        proof += 1
    return True    


def get_balance(participants):
    tx_sender = [[tx['amount'] for tx in block['transaction'] if tx['sender']== participants] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transaction if tx['sender']== participants]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum , tx_amt: tx_sum + sum (tx_amt) if len(tx_amt) > 0 else tx_sum + 0 , tx_sender , 0)
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0 :
    #         amount_sent += tx[0]
    tx_reciptient = [[tx['amount'] for tx in block['transaction'] if tx['recipient']== participants] for block in blockchain]
    amount_reciptient = functools.reduce(lambda tx_sum , tx_amt: tx_sum + sum (tx_amt) if len(tx_amt) > 0 else tx_sum + 0 , tx_reciptient , 0)
    return amount_reciptient - amount_sent


def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance (transaction['sender'])
    return sender_balance >= transaction ['amount']


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transaction])


def add_transaction(recipient,sender = owner , amount = 1.0 ):

    transaction = OrderedDict([('sender' , sender) , ('recipient' , recipient) , ('amount' , amount)])
    if not verify_transaction(transaction):               
        open_transaction.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False

  
def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = OrderedDict([('sender' , 'MINING') , ('recipient' , owner) , ('amount' , G_mining_reward)])
    copied_transaction = open_transaction[:]
    open_transaction.append(reward_transaction)
    block = {
        'previous_hash' : hashed_block,
        'index' : len(blockchain),
        'transaction' : copied_transaction,
        'proof' : proof
    }
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
        if block['previuos_hash'] != hash_block(blockchain[block_index - 1]):
            return False
        if not valid_proof ( block['transaction'] [:-1] , block['previous_hash'] , block['proof']):
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
    print ('h: manipulate the chain ')
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
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = [2]   
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list: ')    
    # if not verify_chain():
    #     print('Invalid blockchain !')
    #     break
    print ('Balance of {} : {:6.2f} '.format('Max' ,get_balance('Farzaneh')))    
else:
    print( '-' * 20 )
print('done')