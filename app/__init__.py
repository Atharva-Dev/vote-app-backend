import os
import requests
import random
import copy
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.blockchain.candidates import Candidate
from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import Block
from backend.pubsub import PubSub



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


@app.route('/castvote', methods = ['GET','POST'])
def addblock():

    b = Block()
    b.vote_to = request.form['candidate']
    curr_time = datetime.now()
    try:
        print(Candidate.getTotalCandidates() )
        if curr_time > end_time :
            raise Exception("Time period expired!")
        if int(b.vote_to) < 0 or int(b.vote_to) > Candidate.getTotalCandidates() :
            raise Exception("Candidate error, No such candidate exist!")

        new_chain = copy.deepcopy(blockchain)
        new_chain.add_block(b)
        pubsub.broadcast_block(b)
    except Exception as e:
        print(e)
        return "500" " malicious vote"
    return "200" " vote casted successfully"



@app.route('/status', methods = ['GET'])
def getstatus():
    curr_time = datetime.now()

    if curr_time < start_time : 
        return jsonify({"status":500, "message": "Voting has not started yet!"})
    if curr_time > end_time :
        return jsonify({"status":500,"message": " Voting time ended!"})
    return jsonify({"status":200, "message": "ok"})



@app.route('/admin/setvotingperiod' ,methods = ['POST'])
def setvotingperiod():
    global start_time
    global end_time
    try:
        rec_start_time = request.form['start_time'] #yyyy-mm-dd-hh:mm:ss
        start_time = datetime.strptime(rec_start_time, "%d-%m-%Y-%H:%M")
        rec_end_time = request.form['end_time']     #yyyy-mm-dd-hh:mm:ss
        end_time = datetime.strptime(rec_end_time, "%d-%m-%Y-%H:%M")
        return "200" " ok"
    except Exception as e:
        print(e)
        return "500" " Error setting time"
    pass


@app.route('/admin/addcandidate', methods = ['POST'])
def addcandidate():
    candidate_name = request.form['name']
    candidate_list.append(Candidate(candidate_name))
    return "200" " ok"

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