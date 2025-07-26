from flask import Flask, jsonify, request, send_from_directory
from blockchain import Blockchain
from uuid import uuid4

# Inicializa a aplicação Flask
app = Flask(__name__)
# Cria um endereço único para este nó
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

# --- ROTAS DA API ---

@app.route('/')
def index():
    """Serve a nossa interface web (o ficheiro index.html)."""
    return send_from_directory('.', 'index.html')

@app.route('/mine', methods=['GET'])
def mine_block():
    """
    Este endpoint aciona a mineração. Ele executa o Proof of Work,
    adiciona a recompensa de mineração e cria o novo bloco.
    """
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    # A recompensa por encontrar a prova. O sender "0" significa que é uma nova moeda.
    # Na função mine_block()
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier, # Mude para esta variável
        amount=1,
    )

    # Cria o novo bloco e o adiciona à corrente
    new_block = blockchain.new_block(proof)

    response = {
        'message': "Novo Bloco Minerado com Sucesso!",
        'block': new_block.to_dict()
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Adiciona uma nova transação à lista de transações pendentes."""
    values = request.get_json()

    # Valida se os campos necessários estão no corpo do pedido
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Valores em falta no corpo do pedido', 400

    # Cria uma nova transação
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'A sua transação será adicionada ao Bloco {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """Retorna a blockchain completa."""
    response = {
        'chain': [block.to_dict() for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Erro: Forneça uma lista de nós válida", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Novos nós foram adicionados',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'A nossa corrente foi substituída pela autoritativa',
            'new_chain': [block.to_dict() for block in blockchain.chain]
        }
    else:
        response = {
            'message': 'A nossa corrente é a autoritativa',
            'chain': [block.to_dict() for block in blockchain.chain]
        }

    return jsonify(response), 200

# --- PONTO DE ENTRADA ---
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='porta para escutar')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)
