from backend.blockchain.block import Block, genesis
from backend.utils.crypto_hash import crypto_hash

class Blockchain:
    """
    Blockchain class holds list of blocks and operations
    """

    def __init__(self, name='chain'):
        self.name = name
        self.chain = [genesis()]
    
    
    def add_block(self, block):
        block.last_hash = self.chain[-1].hash
        block.hash = crypto_hash(block)
        self.chain.append(block)


    def replace_chain(self, chain):
        if len(chain) <= len(self.chain):
            raise Exception('Cannot replace, new chain must be longer')
        try:
            Blockchain.is_valid_chain(chain)
            self.chain = chain 
        except Exception as e:
            raise Exception(f'Cannot replace, new chain is invalid: {e}')

    

    def to_json(self):
        return list(map(lambda block: block.to_json(),self.chain))

    def __repr__(self):
        return "\n".join(list(map(str,self.chain)))


    @staticmethod
    def is_valid_chain(chain):

        try:
            if chain[0] != genesis():
                raise Exception('The genesis block is invalid')
            
            for i in range(1, len(chain)):
                block = chain[i]
                last_block = chain[i-1]
                Block.is_valid_block(last_block,block)
        except Exception as e:
            raise Exception(f'inside is_valid_chain: {e}')

    @staticmethod
    def from_json(chain_json):
        blockchain = Blockchain()
        blockchain.chain = list(map(lambda block_json: Block.from_json(block_json), chain_json))
        return blockchain




def main():
    b = Block()
    ch = Blockchain()
    ch.add_block(b)
    


if __name__ == "__main__":
    main()
    