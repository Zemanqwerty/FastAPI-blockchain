from time import time
import json
import hashlib
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4


app = FastAPI()


class Blockchain(object):
    def __init__(self) -> None:
        self.chain = []
        self.cur_transactions = []

        self.new_block(previous_hash=1, proof=100)
    

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.cur_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.cur_transactions = []

        self.chain.append(block)
        return(block)


    def new_transaction(self, sender, recipient, amount):
        self.cur_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1
    

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        return self.chain[-1]

    
    def proof_of_work(self, last_proof):
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof

    
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        print(guess_hash)

        return guess_hash[:4] == '0000'


bc = Blockchain()

class Transaction(BaseModel):
    sender : str
    recipient : str
    amount : int

node_identifier = str(uuid4()).replace('-', '')

@app.post('/transactions/new')
async def new_tansactions(transaction: Transaction):
    
    if bc.new_transaction(transaction.sender, transaction.recipient, transaction.amount):
        return {'status': 'success'}
    else:
        return {'status': 'failed'}


@app.get('/mine')
async def mine():
    last_proof = bc.last_block['proof']
    previous_hash = bc.hash(bc.last_block)
    proof = bc.proof_of_work(last_proof)
    new_block = bc.new_block(proof, previous_hash)

    if new_block:
        if bc.new_transaction('0', node_identifier, 1):
            return {'status': 'success', 'function': 'mine'}
        else:
            return {'status': 'failed', 'function': 'transaction'}
    else:
        return {'status': 'failed', 'function': 'mine'}


@app.get('/chain/get')
async def get_chain_list():
    return bc.chain

# print(bc.cur_transactions)