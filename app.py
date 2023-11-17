from flask import Flask, render_template, jsonify, request
from web3 import Web3
import json

app = Flask(__name__)

private_keys = [
    "0x7cb9c880394dfb8466e782cd1b455c79586c55efd9fdeef35fa4441ef266e66d", # given after ganache-cli --port 7545
    "0x7cb9c880394dfb8466e782cd1b455c79586c55efd9fdeef35fa4441ef266e66d", # given after ganache-cli --port 7545
]

contract_address = "0x88254406c2c0bA2D48562Bd1F1F50e1E696c5Fdd"  # given after truffle migrate --reset (take 2_deploy_contracts.js)


private_key = private_keys[0] #lets take first key for demoing

# connect to ganash local server
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

if not w3.is_connected():
    print("Failed to connect.")
    exit()
else:
    print("Connected.")

# retrieve smart contract
with open("build/contracts/Voting.json", 'r') as f:
    info_json = json.load(f)
    contract_abi = info_json["abi"]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)


# ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/candidatesCount')
def get_candidates_count():
    count = contract.functions.candidatesCount().call()
    return str(count)

@app.route('/getCandidates', methods=['GET'])
def get_candidates():
    candidates = []
    count = contract.functions.candidatesCount().call()
    for i in range(1, count+1):
        candidate = contract.functions.candidates(i).call()
        candidates.append({
            'id': candidate[0],
            'name': candidate[1],
            'voteCount': candidate[2]
        })
    return jsonify(candidates)

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    candidate_id = int(data['candidateId'])

    # using first ganache adress for demoing
    sender_address = w3.eth.accounts[0]

    # update nounce
    nonce = w3.eth.get_transaction_count(sender_address, 'latest')

    # transaction data
    function_obj = contract.functions.vote(candidate_id)
    trx_data = function_obj._encode_transaction_data()

    trx = {
        'to': contract_address,
        'value': 0,
        'gas': 70000,    # I hard coded it but could be estimated as well
        'gasPrice': w3.to_wei('1', 'gwei'),
        'nonce': nonce,
        'data': trx_data,
        'chainId': 5777  # ganache chain id
    }

    # sign
    signed_trx = w3.eth.account.sign_transaction(trx, private_key)

    # send
    trx_hash = w3.eth.send_raw_transaction(signed_trx.rawTransaction)

    # confirm
    w3.eth.wait_for_transaction_receipt(trx_hash)

    return jsonify({"message": "Vote registered."}), 200
@app.route('/results', methods=['GET'])
def get_results():
    candidates = []
    count = contract.functions.candidatesCount().call()
    for i in range(1, count+1):
        candidate = contract.functions.candidates(i).call()
        candidates.append({
            'id': candidate[0],
            'name': candidate[1],
            'voteCount': candidate[2]
        })
    return render_template('results.html', results=candidates)






if __name__ == '__main__':
    app.run(debug=False)
