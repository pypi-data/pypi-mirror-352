from saslibpy.sas import InstructionVariant, PdaSeed, SYS_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, convert_to_pubkey, get_associated_token_address
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta

from solana.rpc.api import Client

import json
import base64

from borsh_construct import U8, U16, String, CStruct, Vec, I64

from saslibpy.schema import Schema
from saslibpy.credential import Credential

class Attestation(object):

    account_data_borsh_struct = CStruct( 
        "discriminator" / U8,
        "nonce" / U8[32],
        "credential" / U8[32],
        "schema" / U8[32],
        "data" / Vec(U8),
        "signer" / U8[32],
        "expiry" / I64
    )

    create_borsh_struct = CStruct( 
        "id" / U8,
        "nonce" / U8[32],
        "data" / Vec(U8),
        'expiry' / I64
    )

    tokenize_borsh_struct = CStruct( 
        "id" / U8,
        "nonce" / U8[32],
        "data" / Vec(U8),
        'expiry' / I64,
        'name' / String,
        'uri' / String,
        'symbol' / String,
        'mintAccountSpace' / U16
    )

    close_borsh_struct = CStruct( 
        "id" / U8
    )

    close_tokenize_borsh_struct = CStruct( 
        "id" / U8
    )

    
    def __init__(self, settings: dict) -> None: 

        self.discriminator = InstructionVariant.CREATE_ATTESTATION_DISCRIMINATOR
        self.nonce = convert_to_pubkey(settings["nonce"])

        self.credential_pda = convert_to_pubkey(settings["credential"])
        self.credential: Credential = settings["credential_data"]

        self.schema_pda = convert_to_pubkey(settings["schema"])
        self.schema: Schema = settings["schema_data"]

        self.data: dict = settings["data"]
        self.signer = convert_to_pubkey(settings["signer"])
        self.expiry = settings["expiry"]

        self.mint_name = settings.get("mint_name")
        self.mint_uri = settings.get("mint_uri")
        self.mint_symbol = settings.get("mint_symbol")
        self.mint_account_space = settings.get("mint_account_space")


    def __str__(self):
        return self.to_json()
    

    def to_dict(self):
        return {
            "discriminator": self.discriminator,
            "nonce": str(self.nonce),
            "credential": str(self.credential_pda),
            "schema": str(self.schema_pda),
            "data": self.data,
            "signer": str(self.signer),
            "expiry": self.expiry
        }
    

    def to_json(self):
        return json.dumps(self.to_dict())



    @staticmethod
    def from_address(client: Client, pubkey:Pubkey) -> "Attestation": 

        _pubkey = convert_to_pubkey(pubkey)
        _pda_data = json.loads(client.get_account_info(_pubkey).to_json())
        _decode_data = base64.b64decode(_pda_data["result"]["value"]["data"][0])

        _parsed =dict(Attestation.account_data_borsh_struct.parse(_decode_data))
        
        _parsed["schema_data"] = Schema.from_address(client, _parsed["schema"])
        _parsed["credential_data"] = _parsed["schema_data"].credential
        _parsed["data"] = _parsed["schema_data"].decode_attestation_data(bytes(_parsed["data"]))
        
        return Attestation(_parsed)
    

    def calc_pda(self, program_id):

        _attestation_pda = Pubkey.find_program_address([PdaSeed.ATTESTATION_SEED, bytes(self.credential_pda), bytes(self.schema_pda), bytes(self.nonce)], program_id)[0]
        
        _tokenize_attestation_mint_pda = Pubkey.find_program_address([PdaSeed.ATTESTATION_MINT_SEED, bytes(_attestation_pda)], program_id)[0]

        _event_auth_pda = Pubkey.find_program_address([PdaSeed.EVENT_AUTHORITY_SEED], program_id)[0]

        return _attestation_pda, _tokenize_attestation_mint_pda, _event_auth_pda
    
    
    def create_instruction(self, _payer, _author, program_id):

        attestation_pda, tokenize_attestation_mint_pda, event_auth_pda = self.calc_pda(program_id)

        encode_data = self.schema.encode_attestation_data(self.data)
        
        payload_ser = Attestation.create_borsh_struct.build({
            "id": InstructionVariant.CREATE_ATTESTATION_DISCRIMINATOR, 
            "nonce": list(bytes(self.nonce)),
            "data": encode_data,
            "expiry": int(self.expiry),
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(convert_to_pubkey(_payer), True, True),
                AccountMeta(convert_to_pubkey(_author), True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(self.schema_pda, False, False),
                AccountMeta(attestation_pda, False, True),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                ],
            program_id=program_id, 
            data=payload_ser
        )

        return instruction


    def tokenize_instruction(self, _payer, _author, program_id, recipient):

        sas_pda, schema_pda, schema_mint_pda = self.schema.calc_pda(program_id)
        attestation_pda, tokenize_attestation_mint_pda, event_auth_pda = self.calc_pda(program_id)

        _recipient = convert_to_pubkey(recipient)
        recipient_token_account = get_associated_token_address(tokenize_attestation_mint_pda, _recipient)

        encode_data = self.schema.encode_attestation_data(self.data)
        
        payload_ser = Attestation.tokenize_borsh_struct.build({
            "id": InstructionVariant.CREATE_TOKENIZED_ATTESTATION_DISCRIMINATOR,
            "nonce": list(bytes(self.nonce)),
            "data": encode_data,
            "expiry": int(self.expiry),
            "name": self.mint_name,
            "uri": self.mint_uri,
            "symbol": self.mint_symbol,
            "mintAccountSpace": self.mint_account_space
        })

        instruction = Instruction(
            accounts=[
               AccountMeta(convert_to_pubkey(_payer), True, True),
                AccountMeta(convert_to_pubkey(_author), True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(self.schema_pda, False, False),
                AccountMeta(attestation_pda, False, True),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                AccountMeta(schema_mint_pda, False, True),
                AccountMeta(tokenize_attestation_mint_pda, False, True),
                AccountMeta(sas_pda, False, False),
                AccountMeta(recipient_token_account, False, True),
                AccountMeta(_recipient, False, False),
                AccountMeta(TOKEN_2022_PROGRAM_ID, False, False),
                AccountMeta(ASSOCIATED_TOKEN_PROGRAM_ID, False, False),
                ],
            program_id=program_id, 
            data=payload_ser
        )

        return instruction


    @staticmethod
    def parse_instruction(client, raw_instruction):
        
        instruction = None
        if isinstance(raw_instruction, bytes):
            instruction = Instruction.from_bytes(raw_instruction)
        elif isinstance(raw_instruction, str):
            instruction = Instruction.from_json(raw_instruction)
        else:
            pass

        if instruction is None:
            return None
        
        program_id = instruction.program_id

        decode_data = dict(Attestation.create_borsh_struct.parse(instruction.data))

        credential_pda = instruction.accounts[2].pubkey
        schema_pda = instruction.accounts[3].pubkey
        schema = Schema.from_address(client, schema_pda)
        signer = instruction.accounts[1].pubkey

        attestation_data = schema.decode_attestation_data(bytes(decode_data["data"]))


        attestation = Attestation({
                "nonce": decode_data["nonce"],
                "credential": credential_pda,
                "credential_data": schema.credential,
                "schema": schema_pda,
                "schema_data": schema,
                "data": attestation_data,
                "signer": signer,
                "expiry": decode_data["expiry"],
            }
        )
        
        return attestation, program_id
    

    def close_instruction(self, _payer, _author, program_id, _service_program_id=None):

        service_program_id = program_id if _service_program_id is None else _service_program_id

        attestation_pda, tokenize_attestation_mint_pda, event_auth_pda = self.calc_pda(program_id)

        payload_ser = Attestation.close_borsh_struct.build({
            "id": InstructionVariant.CLOSE_ATTESTATION_DISCRIMINATOR
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(convert_to_pubkey(_payer), True, True),
                AccountMeta(convert_to_pubkey(_author), True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(attestation_pda, False, True),
                AccountMeta(event_auth_pda, False, False),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                AccountMeta(convert_to_pubkey(service_program_id), False, False),
                ],
            program_id=program_id, 
            data=payload_ser
        )

        return instruction



    def close_tokenize_instruction(self, _payer, _author, recipient, program_id, _service_program_id=None):

        service_program_id = program_id if _service_program_id is None else _service_program_id

        sas_pda, schema_pda, schema_mint_pda = self.schema.calc_pda(program_id)
        attestation_pda, tokenize_attestation_mint_pda, event_auth_pda = self.calc_pda(program_id)

        _recipient = convert_to_pubkey(recipient)
        recipient_token_account = get_associated_token_address(tokenize_attestation_mint_pda, _recipient)

        payload_ser = Attestation.close_tokenize_borsh_struct.build({
            "id": InstructionVariant.CLOSE_TOKENIZED_ATTESTATION_DISCRIMINATOR
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(convert_to_pubkey(_payer), True, True),
                AccountMeta(convert_to_pubkey(_author), True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(attestation_pda, False, True),
                AccountMeta(event_auth_pda, False, False),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                AccountMeta(convert_to_pubkey(service_program_id), False, False),
                AccountMeta(tokenize_attestation_mint_pda, False, True),
                AccountMeta(sas_pda, False, False),
                AccountMeta(convert_to_pubkey(recipient_token_account), False, True),
                AccountMeta(TOKEN_2022_PROGRAM_ID, False, False),
            ],
            program_id=program_id, 
            data=payload_ser
        )

        return instruction