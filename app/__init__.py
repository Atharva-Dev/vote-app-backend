import os
from time import sleep
import requests
import random
import copy
from datetime import datetime
from faker import Faker
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import Block
from backend.pubsub import PubSub
from backend.validator import validator, candidate_list, result
import backend.serverList as ServerList



app = Flask(__name__)
CORS(app, resources={ r'/*' : { 'origins': 'http://localhost:3000' } })
blockchain = Blockchain()
pubsub =PubSub(blockchain)

# candidate_list = []

start_time = datetime.now()
end_time = datetime.now()


@app.route('/votechain')
def default(): 
    return jsonify(blockchain.to_json())


@app.route('/castvote', methods = ['POST'])
def addblock():
    global blockchain
    b = Block()
    print("request:", request.get_json())
    b.vote_to = request.get_json()['to']
    curr_time = datetime.now()
    try:
        if curr_time > end_time :
            raise Exception("Time period expired!")
        if int(b.vote_to) < 0 or int(b.vote_to) > len(candidate_list) :
            raise Exception("Candidate error, No such candidate exist!")
        new_chain = copy.deepcopy(blockchain)
        new_chain.add_block(b)
        pubsub.broadcast_block(b)
        # print("voter id:",request.get_json()['by'])
        validator.add_voter(request.get_json()['by'])
    except Exception as e:
        print(e)
        return jsonify({"code": 1, "message": "malicious vote"})
    return jsonify({"code":0, "message": " vote casted successfully"})



@app.route('/status/<id>', methods = ['GET'])
def getstatus(id):
    curr_time = datetime.now()
    if curr_time < start_time : 
        return jsonify({"code":1, "message": "Voting has not started yet!"})
    if curr_time > end_time :
        return jsonify({"code":1,"message": "Voting time ended!"})
    if validator.has_voted(id) :
        return jsonify({"code":1,"message": "Voter has already voted!"})

    return jsonify({"code":0, "message": "ok"})



@app.route('/setvotingperiod' ,methods = ['POST'])
def setvotingperiod():
    global start_time
    global end_time
    try:
        json = request.get_json()
        dt_format = "%a %b %d %Y %H:%M:%S"
        rec_start_time = json['start_time'] #yyyy-mm-dd-hh:mm:ss
        rec_start_time = ' '.join(list(rec_start_time.split(' ')[:5]))
        print(rec_start_time)
        start_time = datetime.strptime(rec_start_time, dt_format)
        rec_end_time = json['end_time']     #yyyy-mm-dd-hh:mm:ss
        rec_end_time = ' '.join(list(rec_end_time.split(' ')[:5]))
        end_time = datetime.strptime(rec_end_time, dt_format)
        return jsonify({"code":0})
    except Exception as e:
        print(e)
        result=False
        return jsonify({"code":1})

@app.route('/getcandidatelist', methods=['GET'])
def getcandidatelist():
    print(candidate_list)
    print(jsonify(candidate_list))
    return jsonify(candidate_list)

@app.route('/addcandidates', methods = ['POST'])
def addcandidate():
   
    try:
        json = request.get_json()
        candidate_list = json['candidates']
        print(candidate_list)
        return jsonify({"code":0})
    except Exception as e:
        print(e)
        return jsonify({"code":1})

@app.route('/addSampleBlock', methods=['GET'])
def addSampleBlock():
    global blockchain
    max_index = len(candidate_list)
    b = Block()
    b.vote_to = random.randint(0, max_index-1)
    new_chain = copy.deepcopy(blockchain)
    new_chain.add_block(b)
    pubsub.broadcast_block(b)
    blockchain.add_block(b)
    return jsonify({"length":len(blockchain.get_chain()), "to": b.vote_to})


@app.route('/addSampleBlocks', methods=['GET'])
def addSampleBlocks():
    global blockchain
    fake = Faker()
    max_index = len(candidate_list)
    for i in range(50):
        sleep(3)
        b = Block()
        b.time = str(fake.date_time_between(start_date='now', end_date='+5d'))
        b.vote_to = random.randint(0, max_index-1)
        new_chain = copy.deepcopy(blockchain)
        try:
            new_chain.add_block(b)
            pubsub.broadcast_block(b)
            # print("voter id:",request.get_json()['by'])
            #validator.add_voter(request.get_json()['by'])
        except Exception as e:
            print(e)
            return jsonify({"code": 1, "message": "malicious vote"})
    # blockchain.prepare_result()
    return jsonify({"length":len(blockchain.get_chain())})

@app.route('/mutateBlock', methods=['GET'])
def mutateBlock():
    blockchain.add_dirty_block()



@app.route('/getResult')
def getReult() :
    global blockchain
    blockchain.prepare_result()
    print(os.system('ls'))
    return send_file('result.csv')




PORT = 5000

if os.environ.get('PEER') == 'True':
    # PORT = random.randint(5001, 6000)
    # while(PORT in ServerList.get_all_servers()) : 
    #     PORT = random.randint(5001, 6000)
    # ServerList.addServer(PORT)
    PORT = 5010
    result = requests.get(ServerList.baseURL+':5000/votechain')
    
    result_blockchain = Blockchain.from_json(result.json())

    try:
        blockchain.replace_chain(result_blockchain)
        print('\n--Replaced blockchain successfully')
    except Exception as e:
        print(f'\n--Error while synchronizing : {e}')

app.run(port=PORT)
