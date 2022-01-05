import os
import requests
import random
import copy
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import Block
from backend.pubsub import PubSub
from backend.validator import validator



app = Flask(__name__)
CORS(app, resources={ r'/*' : { 'origins': 'http://localhost:3000' } })
blockchain = Blockchain()
pubsub =PubSub(blockchain)


candidate_list = []
start_time = datetime.now()
end_time = datetime.now()


@app.route('/votechain')
def default(): 
    return jsonify(blockchain.to_json()[::-1])


@app.route('/castvote', methods = ['POST'])
def addblock():

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
        return jsonify({"code":1})

@app.route('/getcandidatelist', methods=['GET'])
def getcandidatelist():
    print(candidate_list)
    print(jsonify(candidate_list))
    return jsonify(candidate_list)

@app.route('/addcandidates', methods = ['POST'])
def addcandidate():
    global candidate_list
    try:
        json = request.get_json()
        candidate_list = json['candidates']
        print(candidate_list)
        return jsonify({"code":0})
    except Exception as e:
        print(e)
        return jsonify({"code":1})
    

PORT = 5000

if os.environ.get('PEER') == 'True':
    PORT = random.randint(5001, 6000)

    result = requests.get('http://localhost:5000/votechain')
    
    result_blockchain = Blockchain.from_json(result.json())

    try:
        blockchain.replace_chain(result_blockchain)
        print('\n--Replaced blockchain successfully')
    except Exception as e:
        print(f'\n--Error while synchronizing : {e}')

app.run(port=PORT)