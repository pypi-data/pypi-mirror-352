from saslibpy.sas import InstructionVariant, PdaSeed, SYS_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, convert_to_pubkey, id_to_type, type_to_id
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta

from solana.rpc.api import Client

import json
import base64

from borsh_construct import I64, U8
from borsh_construct import String, CStruct, Vec

from saslibpy.credential import Credential


class Schema(object):

    account_data_borsh_struct = CStruct( 
        "discriminator" / U8,
        "credential" / U8[32],
        "name" / String,
        "description" / String,
        "layout" /  String,
        "fieldNames" / String,
        "isPaused" / U8,
        "version" / U8,
    )

    create_borsh_struct = CStruct( 
        "id" / U8,
        "name" / String,
        "description" / String,
        'layout' / Vec(U8),
        'fieldNames' / Vec(String)
    )

    change_description_borsh_struct = CStruct( 
        "id" / U8,
        "description" / String
    )

    change_status_borsh_struct = CStruct( 
        "id" / U8,
        "isPaused" / U8
    )

    change_version_borsh_struct = CStruct( 
        "id" / U8,
        'layout' / Vec(U8),
        'fieldNames' / Vec(String)
    )

    tokenize_borsh_struct = CStruct( 
        "id" / U8,
        "max_size" / I64
    )

    def __init__(self, settings: dict) -> None: 

        self.discriminator = InstructionVariant.CREATE_SCHEMA_DISCRIMINATOR
        self.credential_pda = convert_to_pubkey(settings["credential"])
        self.credential: Credential = settings["credential_data"]
        self.name = settings["name"]
        self.description = settings["description"]
        self.layout: list = settings["layout"]
        self.fieldNames: list = settings["fieldNames"]
        self.isPaused = settings.get("isPaused")
        self.version = settings.get("version")
        self.mint_max_size = settings.get("mint_max_size")
        self.attestation_data_borsh_struct = CStruct( *[
            self.fieldNames[i] / id_to_type[int(self.layout[i])]  for i in range(len(self.fieldNames))
        ] )

    def __str__(self):
        return self.to_json()
    

    def to_dict(self):
        return {
            "discriminator": self.discriminator,
            "credential_pda": str(self.credential_pda),
            "name": self.name,
            "description": self.description,
            "layout": self.layout,
            "fieldNames": self.fieldNames,
            "isPaused": self.isPaused,
            "version": self.version,
        }
    

    def to_json(self):
        return json.dumps(self.to_dict())
    

    @staticmethod
    def encode_layout_data(type_list):
        _layout = [
            type_to_id[x] for x in type_list
        ]
        return _layout
    

    @staticmethod
    def decode_layout_data(layout):
        _type_list = [
            id_to_type[int(x)] for x in layout
        ]
        return _type_list
    
    
    def encode_attestation_data(self, data:dict):
        return self.attestation_data_borsh_struct.build(data)
    

    def decode_attestation_data(self, data:bytes):
        _r = dict(self.attestation_data_borsh_struct.parse(data))
        del _r["_io"]
        return _r


    @staticmethod
    def from_address(client: Client, pubkey) -> "Schema": 

        _pubkey = convert_to_pubkey(pubkey)
        _pda_data = json.loads(client.get_account_info(_pubkey).to_json())
        _decode_data = base64.b64decode(_pda_data["result"]["value"]["data"][0])

        _parsed = dict(Schema.account_data_borsh_struct.parse(_decode_data))
        _parsed["credential_data"] = Credential.from_address(client, _parsed["credential"])
        _parsed["layout"] = list(bytes(_parsed["layout"].encode()))
        field_count = len(_parsed["layout"])
        _parsed["fieldNames"] = String[field_count].parse(_parsed["fieldNames"].encode())
        
        return Schema(_parsed)
    

    def calc_pda(self, program_id):
        _sas_pda = Pubkey.find_program_address([PdaSeed.SAS_SEED], program_id)[0]

        _schema_pda = Pubkey.find_program_address([PdaSeed.SCHEMA_SEED, bytes(self.credential_pda), self.name.encode('utf-8'), bytes([int(self.version)])], program_id)[0]

        _schema_mint_pda = Pubkey.find_program_address([PdaSeed.SCHEMA_MINT_SEED, bytes(_schema_pda)], program_id)[0]

        return _sas_pda, _schema_pda, _schema_mint_pda
    
    
    def create_instruction(self, _payer, program_id):

        sas_pda, schema_pda, schema_mint_pda = self.calc_pda(program_id)
        
        payload_ser = Schema.create_borsh_struct.build({
            "id": InstructionVariant.CREATE_SCHEMA_DISCRIMINATOR, 
            "name": self.name, 
            "description": self.description,
            "layout": self.layout,
            "fieldNames": self.fieldNames
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(convert_to_pubkey(_payer), True, True),
                AccountMeta(self.credential.authority, True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(schema_pda, False, True),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                ],
            program_id=program_id, 
            data=payload_ser
        )
        
        return instruction
    

    def tokenize_instruction(self, _payer, program_id, max_size=None):

        sas_pda, schema_pda, schema_mint_pda = self.calc_pda(program_id)

        payload_ser = Schema.tokenize_borsh_struct.build({
            "id": InstructionVariant.TOKENIZE_SCHEMA_DISCRIMINATOR, 
            "max_size": max_size if max_size is not None else self.mint_max_size,
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(convert_to_pubkey(_payer), True, True),
                AccountMeta(self.credential.authority, True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(schema_pda, False, False),
                AccountMeta(schema_mint_pda, False, True),
                AccountMeta(sas_pda, False, False),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                AccountMeta(TOKEN_2022_PROGRAM_ID, False, False),
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

        decode_data = Schema.create_borsh_struct.parse(instruction.data)
        authority = instruction.accounts[2].pubkey

        schema = Schema({
                "credential": authority,
                "credential_data": Credential.from_address(client, authority),
                "name": decode_data["name"],
                "description": decode_data["description"],
                "layout": decode_data["layout"],
                "fieldNames": decode_data["fieldNames"]
            }
        )
        
        return schema, program_id
    

    def change_description_instruction(self, description, program_id):

        sas_pda, schema_pda, schema_mint_pda = self.calc_pda(program_id)
        
        payload_ser = Schema.change_description_borsh_struct.build({
            "id": InstructionVariant.CHANGE_SCHEMA_DESCRIPTION_DISCRIMINATOR, 
            "description": description
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(self.credential.authority, True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(schema_pda, False, True),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                ],
            program_id=program_id, 
            data=payload_ser
        )
        
        return instruction
    

    def change_status_instruction(self, isPaused, program_id):

        sas_pda, schema_pda, schema_mint_pda = self.calc_pda(program_id)
        
        payload_ser = Schema.change_status_borsh_struct.build({
            "id": InstructionVariant.CHANGE_SCHEMA_STATUS_DISCRIMINATOR, 
            "isPaused": isPaused
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(self.credential.authority, True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(schema_pda, False, True)
                ],
            program_id=program_id, 
            data=payload_ser
        )
        
        return instruction

    

    def change_version_instruction(self, _payer, _old_schema, program_id):

        sas_pda, schema_pda, schema_mint_pda = self.calc_pda(program_id)
        
        payload_ser = Schema.change_version_borsh_struct.build({
            "id": InstructionVariant.CHANGE_SCHEMA_VERSION_DISCRIMINATOR, 
            "layout": self.layout,
            "fieldNames": self.fieldNames
        })

        instruction = Instruction(
            accounts=[
                AccountMeta(convert_to_pubkey(_payer), True, True),
                AccountMeta(self.credential.authority, True, True),
                AccountMeta(self.credential_pda, False, False),
                AccountMeta(convert_to_pubkey(_old_schema), False, False),
                AccountMeta(schema_pda, False, True),
                AccountMeta(SYS_PROGRAM_ID, False, False),
                ],
            program_id=program_id, 
            data=payload_ser
        )
        
        return instruction
    


