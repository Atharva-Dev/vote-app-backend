from backend.validator import csvfile
from backend.app.__init__ import candidate_list
from backend.blockchain.block import Block, genesis
from backend.utils.crypto_hash import crypto_hash
import backend.serverList as ServerList
class Blockchain:
    """
    Blockchain class holds list of blocks and operations
    """

    def __init__(self, name='chain'):
        self.name = name
        self.__chain = [genesis()]
        self.result = False
    
    def get_chain(self) :
        return self.__chain[:]

    def add_dirty_block(self):
        block = Block()
        block.to = 10
        block.last_hash = self.__chain[-1].hash
        block.hash = crypto_hash(block)
        self.__chain.append(block)

    def add_block(self, block):
        block.last_hash = self.__chain[-1].hash
        block.hash = crypto_hash(block)
        try :
            is_valid_chain(self.__chain)
        except Exception as e:
            self.replace_chain_from_server()

        self.__chain.append(block)

    def replace_chain_from_server(self):
        for port in ServerList.get_all_servers() :
            try:
                result = requests.get(serverList.baseURL+':' + str(port) + '/votechain')
                result_blockchain = Blockchain.from_json(result.json())
                is_valid_chain(result_blockchain)
                self.__chain = result_blockchain
                
                return
            except Exception as e: 
                pass

    def replace_chain(self, new_blockchain):
        # print(chain)
        # print('-'*10)
        # print(self.__chain)
        # print(type(chain))
        if(type(new_blockchain) != type(self.__chain)) : new_blockchain = new_blockchain.get_chain()
        if len(new_blockchain) <= len(self.__chain):
            print('new chain length:' ,len(new_blockchain))
            print('old chain length:', len(self.get_chain()))
            raise Exception('Cannot replace, new chain must be longer')
        
        print('check1')
        try:
            Blockchain.is_valid_chain(new_blockchain)
            print('check2')
            self.__chain = new_blockchain 
        except Exception as e:
            raise Exception(f'Cannot replace, new chain is invalid: {e}')

    

    def to_json(self):
        return list(map(lambda block: block.to_json(),self.__chain))

    def __repr__(self):
        return "\n".join(list(map(str,self.__chain)))

    def prepare_result(self):
        if self.result is False :
            with open(csvfile, 'w') as csv:
                csv.write('time, vote to\n')
                for i in range(1, len(self.__chain)) :
                    print(i)
                    csv.write(str(self.__chain[i].time))
                    csv.write(',')
                    csv.write(str(candidate_list[self.__chain[i].vote_to]))
                    csv.write('\n')
        self.result = True

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
        blockchain.__chain = list(map(lambda block_json: Block.from_json(block_json), chain_json))
        return blockchain




def main():
    b = Block()
    ch = Blockchain()
    ch.add_block(b)
    


if __name__ == "__main__":
    main()
    
