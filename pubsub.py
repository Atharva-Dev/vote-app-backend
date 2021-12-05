import time
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from backend.blockchain.block import Block
from backend.blockchain.blockchain import Blockchain

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-ec69896a-321e-11eb-9d95-7ab25c099cb1'
pnconfig.publish_key = 'pub-c-c70ece11-d1b1-4c3c-a6a3-94f2147b503b'


CHANNELS = {
    'TEST':'TEST',
    'BLOCK':'BLOCK'
}



class Listener(SubscribeCallback):

    def __init__(self, blockchain):
        self.blockchain = blockchain

    def message(self, pubnub, message_obj):
        print(f'\nChannel:{message_obj.channel}\nMessage: {message_obj.message}')

        if message_obj.channel == CHANNELS['BLOCK']:
            block = Block.from_json(message_obj.message)
            new_chain = self.blockchain.chain[:]
            new_chain.append(block)
            try:
                self.blockchain.replace_chain(new_chain)
                print(f'\n-- Blockchain replaced successfully')
            except Exception as e:
                raise Exception(f'\n-- Unable to replace chain: {e}')

class PubSub():
    """
    Handles publish/subscribe layer in application
    provides communication between blockchain networks 
    """

    def __init__(self, blockchain):
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(blockchain))

    def publish(self, channel, message):
        self.pubnub.publish().channel(channel).message(message).sync()

    def broadcast_block(self, block):
        self.publish(CHANNELS['BLOCK'], block.to_json())





def main():
    pubsub = PubSub(Blockchain())
    time.sleep(1)
    pubsub.publish(CHANNELS['BLOCK'], Block().to_json())
    

if __name__ == "__main__":
    main()