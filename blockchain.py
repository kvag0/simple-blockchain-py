import hashlib
import json
from time import time

class Block:
    def __init__(self, index, timestamp, transactions, proof, previous_hash):
        """
        Construtor para um Bloco.
        """
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

    def calculate_hash(self):
        """
        Cria um hash SHA-256 de um Bloco.
        """
        # Devemos garantir que o dicionário está ordenado (sort_keys=True)
        # para garantir que o hash seja sempre o mesmo para os mesmos dados.
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        """
        Retorna uma representação do Bloco em dicionário, incluindo o seu hash.
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'proof': self.proof,
            'previous_hash': self.previous_hash,
            'hash': self.calculate_hash()
        }

class Blockchain:
    def __init__(self):
        """
        Construtor da Blockchain.
        """
        self.chain = []
        self.current_transactions = []

        # Criar o Bloco Génese - o primeiro bloco da corrente
        self.new_block(previous_hash='1', proof=100)

    @property
    def last_block(self):
        """Retorna o último bloco da corrente."""
        return self.chain[-1]

    def new_block(self, proof, previous_hash=None):
        """
        Cria um novo bloco e o adiciona à corrente.
        :param proof: <int> A Prova de Trabalho.
        :param previous_hash: (Opcional) <str> Hash do bloco anterior.
        :return: <Block> O novo Bloco.
        """
        prev_hash = previous_hash or self.last_block.calculate_hash()

        block = Block(
            index=len(self.chain) + 1,
            timestamp=time(),
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=prev_hash,
        )

        # Reseta a lista de transações pendentes
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Adiciona uma nova transação à lista de transações pendentes.
        :return: <int> O índice do Bloco que irá conter esta transação.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block.index + 1

    def proof_of_work(self, last_proof):
        """
        Encontra um número 'proof' que satisfaça a nossa condição (hash com 4 zeros).
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida se o hash(last_proof, proof) contém 4 zeros à esquerda.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"