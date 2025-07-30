# Solana attestation service
The Solana Attestation Service (SAS) architecture guide is a technical overview of a credibly neutral attestation registry protocol. The SAS is built to enable the association of off-chain data with on-chain wallets through trusted attestations, serving as verifiable claims issued by trusted entities while preserving user privacy.

# Solana attestation service python SDK

## install
```
pip install saslibpy
```

## import 

### saslib
```
from saslibpy.credential import Credential
from saslibpy.schema import Schema
from saslibpy.attestation import Attestation
from saslibpy.sas import DEVNET_PROGRAM_ID
```

### solana rpc client
```
from solana.rpc.api import Client
```

### solders tool
```
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
```

### borsh_construct types
```
from borsh_construct import I64, U8
from borsh_construct import String, CStruct, Vec
```

## create client
```
client = Client("https://api.devnet.solana.com")
```

## set sas programId
```
#devnet
program_id = DEVNET_PROGRAM_ID
```

## create credential
```
def create_credential():

    _settings = {
            "authority": auth_account.pubkey(),
            "name": "sdk_credential_0.2.0",
            "signers": [payer.pubkey(), auth_account.pubkey()]
        }

    credential = Credential(_settings)

    instruction_construct = credential.create_instruction(payer, program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, auth_account])

    resp = client.send_transaction(transaction)
    print(resp)


```


## change credential signers
```
def change_credential_signers():

    credential = Credential.from_address(client, credential_pda)

    instruction_construct = credential.change_signers_instruction(payer, [signer_1.pubkey(), signer_2.pubkey()], program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, auth_account])

    resp = client.send_transaction(transaction)
    print(resp)
```

## create schema
```
def create_schema():

    credential = Credential.from_address(client, credential_pda)

    layout_type = [String, String, String, String, String]
    layout = Schema.encode_layout_data(layout_type)

    fields = ["index", "chain", "subject", "score", "timestamp"]

    _settings = {
        "credential": credential_pda,
        "credential_data": credential,
        "name": "sdk_schema_0.2.0",
        "description": "sdk_schema media score",
        "layout": layout,
        "fieldNames": fields,
        "isPaused": 0,
        "version": "1"
        }

    schema = Schema(_settings)

    instruction_construct = schema.create_instruction(payer, program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, auth_account])

    resp = client.send_transaction(transaction)
    print(resp)
    
```

## change description schema
```
def change_description_schema():

    schema = Schema.from_address(client, schema_pda)

    instruction_construct = schema.change_description_instruction("second description", program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, auth_account])

    resp = client.send_transaction(transaction)
    print(resp)
```

## change status schema
```
def change_status_schema():

    schema = Schema.from_address(client, schema_pda)

    instruction_construct = schema.change_status_instruction(True, program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, auth_account])

    resp = client.send_transaction(transaction)
    print(resp)
```

## change version schema
```
def change_version_schema():

    old_schema = Schema.from_address(client, schema_pda)

    layout_type = [U32, String, String, String, String]
    layout = Schema.encode_layout_data(layout_type)

    fields = ["new_index", "new_chain", "new_subject", "new_score", "new_timestamp"]

    _settings = {
        "credential": old_schema.credential_pda,
        "credential_data": old_schema.credential,
        "name": old_schema.name,
        "description": old_schema.description,
        "layout": layout,
        "fieldNames": fields,
        "isPaused": old_schema.isPaused,
        "version": int(old_schema.version) + 1
        }

    new_schema = Schema(_settings)

    instruction_construct = new_schema.change_version_instruction(payer, schema_pda, program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, auth_account])

    resp = client.send_transaction(transaction)
    print(resp)
```


## tokenize schema
```
def tokenize_schema():

    schema = Schema.from_address(client, schema_pda)

    instruction_construct = schema.tokenize_instruction(payer, program_id, max_size=100)
    
    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, auth_account])

    resp = client.send_transaction(transaction)
    print(resp)
```


## create attestation
```
def create_attestation():
    
    schema = Schema.from_address(client, schema_pda)
    attestaion_nonce: Keypair =  Keypair()
    ts = int(datetime.datetime.now().timestamp())

    attestation_data = {
        "new_index": 0,
        "new_chain": "soalna",
        "new_subject": str(payer.pubkey()),
        "new_score": "71.23",
        "new_timestamp": str(ts)
    }

    _settings = {
        "nonce": attestaion_nonce.pubkey(),
        "credential": schema.credential_pda,
        "credential_data": schema.credential,
        "schema": schema_pda,
        "schema_data": schema,
        "data": attestation_data,
        "signer": schema.credential.signers[0],
        "expiry": ts + 3600 * 24 * 90
        }
    
    attestation = Attestation(_settings)

    instruction_construct = attestation.create_instruction(payer, signer_1, program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, signer_1])

    resp = client.send_transaction(transaction)
    print(resp)
```


## close attestation
```
def close_attestation():
    
    attestation = Attestation.from_address(client, attestation_pda)

    instruction_construct = attestation.close_instruction(payer, signer_1, program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, signer_1])

    resp = client.send_transaction(transaction)
    print(resp)
```


## create tokenize attestation
```
def create_tokenize_attestation():

    schema = Schema.from_address(client, schema_pda)
    
    ts = int(datetime.datetime.now().timestamp())

    tokenize_attestaion_nonce: Keypair =  Keypair()

    attestation_data = {
        "new_index": 1,
        "new_chain": "soalna",
        "new_subject": str(payer.pubkey()),
        "new_score": "75.3",
        "new_timestamp": str(ts)
    }

    mint_name = "Test Asset"
    mint_uri = "https://x.com"
    mint_symbol = "VAT"
    mint_account_space = 700

    _settings = {
        "nonce": tokenize_attestaion_nonce.pubkey(),
        "credential": schema.credential_pda,
        "credential_data": schema.credential,
        "schema": schema_pda,
        "schema_data": schema,
        "data": attestation_data,
        "signer": signer_1,
        "expiry": ts + 3600 * 24 * 90,
        "mint_name": mint_name,
        "mint_uri": mint_uri,
        "mint_symbol": mint_symbol,
        "mint_account_space": mint_account_space

        }
    
    attestation = Attestation(_settings)

    instruction_construct = attestation.tokenize_instruction(payer, signer_1, program_id, recipient)
    
    
    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, signer_1])

    resp = client.send_transaction(transaction)
    print(resp)
```


## close tokenize attestation
```
def close_tokenize_attestation():
    
    attestation = Attestation.from_address(client, attestation_pda)

    instruction_construct = attestation.close_tokenize_instruction(payer, signer_1, recipient, program_id)

    # Create a message
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    message = MessageV0.try_compile(payer.pubkey(), [instruction_construct], [], recent_blockhash)

    transaction = VersionedTransaction(message, [payer, signer_1])

    resp = client.send_transaction(transaction)
    print(resp)
```


## fetch credential 
```
def fetch_credential():

    credential = Credential.from_address(client, credential_pda)

    print("credential:", credential)

    instruction = credential.create_instruction(payer, program_id)

    new_credential, pid = Credential.parse_instruction(bytes(instruction))

    print("new_credential:", new_credential)
    print("pid:", pid)
```

## fetch schema
```
def fetch_schema():

    schema = Schema.from_address(client, schema_pda)

    print("schema:", schema)

    instruction = schema.create_instruction(payer, program_id)

    new_schema, pid = Schema.parse_instruction(client, bytes(instruction))

    print("new_schema:", new_schema)
    print("pid:", pid)
```


## fetch attestation 
```
def fetch_attestation():

    attestation = Attestation.from_address(client, attestation_pda)

    print("attestation:", attestation)
    
    instruction = attestation.create_instruction(payer, signer_1, program_id)

    new_attestation, pid = Attestation.parse_instruction(client, bytes(instruction))

    print("new_attestation:", new_attestation)
    print("pid:", pid)
```
