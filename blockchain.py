import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

class Block:
    def __init__(self, index, timestamp, transactions, proof, previous_hash):
        """
        Construtor para um Bloco.
        :param index: <int> O ID do bloco na corrente.
        :param timestamp: <float> O tempo de criação (em segundos desde 1970).
        :param transactions: <list> Lista de transações a serem incluídas no bloco.
        :param proof: <int> A "Prova de Trabalho" que validou o bloco.
        :param previous_hash: <str> O hash do bloco anterior na corrente.
        """
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

    def calculate_hash(self):
        """
        Cria um hash SHA-256 deste Bloco.
        """
        # Convertemos o dicionário do bloco para uma string JSON.
        # É crucial usar sort_keys=True para garantir que a saída seja sempre a mesma (determinismo).
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        
        # Retornamos o hash em formato hexadecimal.
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        """
        Retorna uma representação do Bloco em formato de dicionário,
        útil para a resposta da API, incluindo o seu hash atual.
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'proof': self.proof,
            'previous_hash': self.previous_hash,
            'hash': self.calculate_hash() # Adiciona o hash do bloco atual à saída
        }

class Blockchain:
    def __init__(self):
        """
        Construtor da Blockchain.
        """
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Criar o Bloco Génese - Esta linha DEVE estar DENTRO do __init__
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Adiciona um novo nó à lista de nós.
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Aceita um URL sem http://, ex: '192.168.0.5:5001'
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('URL Inválido')

    def valid_chain(self, chain):
        """
        Determina se uma dada blockchain é válida.
        """
        last_block_obj = chain[0]
        current_index = 1

        while current_index < len(chain):
            block_obj = chain[current_index]
            # Verifica se o hash do bloco está correto
            if block_obj.previous_hash != last_block_obj.calculate_hash():
                return False

            # Verifica se a Prova de Trabalho está correta
            if not self.valid_proof(last_block_obj.proof, block_obj.proof):
                return False

            last_block_obj = block_obj
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Este é o nosso Algoritmo de Consenso.
        """
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain_data = response.json()['chain']

                    chain_objects = []
                    for block_data in chain_data:
                        block = Block(block_data['index'], block_data['timestamp'], block_data['transactions'], block_data['proof'], block_data['previous_hash'])
                        chain_objects.append(block)

                    if length > max_length and self.valid_chain(chain_objects):
                        max_length = length
                        new_chain = chain_objects
            except requests.exceptions.RequestException:
                continue

        if new_chain:
            self.chain = new_chain
            return True

        return False

    @property
    def last_block(self):
        """Retorna o último bloco da corrente."""
        return self.chain[-1]

    def new_block(self, proof, previous_hash=None):
        """
        Cria um novo bloco e o adiciona à corrente.
        """
        prev_hash = previous_hash or self.last_block.calculate_hash()
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time(),
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=prev_hash,
        )
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Adiciona uma nova transação à lista de transações pendentes.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block.index + 1

    def proof_of_work(self, last_proof):
        """
        Encontra a Prova de Trabalho.
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida a prova.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"