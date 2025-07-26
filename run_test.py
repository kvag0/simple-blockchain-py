from blockchain import Blockchain
import json

# Instanciar a nossa blockchain
my_blockchain = Blockchain()

print("--- Blockchain Criada ---")
print("Minerando o primeiro bloco após o Génese...")

# Minerar o Bloco 2
last_proof_1 = my_blockchain.last_block.proof
proof_1 = my_blockchain.proof_of_work(last_proof_1)
my_blockchain.new_transaction(sender="0", recipient="Meu Endereço", amount=1) # Recompensa
my_blockchain.new_block(proof_1)

print("\n--- Mineração do Bloco 2 Concluída ---")

# Minerar o Bloco 3
print("Minerando o próximo bloco...")
last_proof_2 = my_blockchain.last_block.proof
proof_2 = my_blockchain.proof_of_work(last_proof_2)
my_blockchain.new_transaction(sender="Alice", recipient="Bob", amount=5)
my_blockchain.new_transaction(sender="0", recipient="Meu Endereço", amount=1) # Recompensa
my_blockchain.new_block(proof_2)

print("\n--- Mineração do Bloco 3 Concluída ---")


# Imprimir a corrente de blocos de forma legível
print("\n⛓️⛓️⛓️ Corrente Final da Blockchain ⛓️⛓️⛓️")
for block in my_blockchain.chain:
    # Usamos o método to_dict() que criámos para incluir o hash do bloco atual
    print(json.dumps(block.to_dict(), indent=2))
    print("-" * 40)
