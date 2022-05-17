from datetime import datetime
from backend.utils.crypto_hash import crypto_hash

def genesis():
    """
    Generate The Genesis block
    """
    genesis_block = Block()
    genesis_block.to=-1
    genesis_block.last_hash = 'last_hash'
    genesis_block.hash = crypto_hash(genesis_block)
    genesis_block.time = 'now'
    return genesis_block



class Block:
   
    def __init__(self):
        """
        Creates an Empty Block
        """
        self.vote_to=-1
        self.last_hash = None
        self.hash = None
        self.time = str(datetime.now())
   
    def __eq__(self, other):
        if not isinstance(other, Block):

            return NotImplemented
        
        return self.vote_to == other.vote_to and self.hash == other.hash and self.last_hash == other.last_hash



    def to_json(self):
        return self.__dict__

    def __repr__(self):
        return (
            'Block('
            f'vote: {self.vote_to}, '
            f'hash: {self.hash}, '
            f'last_hash: {self.last_hash} )'
        )
    
    def __eq__(self, other):
        return self.__dict__==other.__dict__

    @staticmethod
    def is_valid_block(last_block, block):
        
        try:
            if block.last_hash != last_block.hash:
                raise Exception('The block last hash is incorrect')
            eblk = Block()
            eblk.vote_to = block.vote_to
            eblk.last_hash = block.last_hash
            if block.hash != crypto_hash(eblk):
                raise Exception('The block hash is incorrect')
        except Exception as e:
            raise Exception(f'inside is_valid_block: {e}')

    @staticmethod
    def from_json(data):
        print("-"*10)
        print(data)
        print("-"*10)
        block = Block()
        block.vote_to = data['vote_to']
        block.last_hash = data['last_hash']
        block.hash = data['hash']
        return block


def main():
    pass

if __name__ == "__main__":
    main()