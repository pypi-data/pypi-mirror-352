from saslibpy.sas import InstructionVariant, PdaSeed, SYS_PROGRAM_ID, convert_to_pubkey
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta

from solana.rpc.api import Client

import json
import base64

from borsh_construct import U8, String, CStruct, Vec

class Credential(object):

    account_data_borsh_struct = CStruct( 
        "discriminator" / U8,
        "authority" / U8[32],
        "name" / String,
        "signers" / Vec(U8[32])
    )

    create_borsh_struct = CStruct( 
        "id" / U8,
        "name" / String,
        'signers' / Vec(U8[32])
    )

    change_signers_borsh_struct = CStruct( 
        "id" / U8,
        'signers' / Vec(U8[32])
    )

    def __init__(self, settings: dict) -> None: 

        self.discriminator = InstructionVariant.CREATE_CREDENTIAL_DISCRIMINATOR
        self.authority = convert_to_pubkey(settings["authority"])
        self.name = settings["name"]
        self.signers = [ convert_to_pubkey(x) for x in settings["signers"]]

    
    def __str__(self):
        return self.to_json()
    

    def to_dict(self):
        return {
            "discriminator": self.discriminator,
            "authority": str(self.authority),
            "name": self.name,
            "signers": [ str(x) for x in self.signers],
        }
    

    def to_json(self):
        return json.dumps(self.to_dict())


    @staticmethod
    def from_address(client: Client, pubkey) -> "Credential": 

        _pubkey = convert_to_pubkey(pubkey)
        _pda_data = json.loads(client.get_account_info(_pubkey).to_json())
        _decode_data = base64.b64decode(_pda_data["result"]["value"]["data"][0])
        _parsed = dict(Credential.account_data_borsh_struct.parse(_decode_data))
        
        return Credential(_parsed)
    

    def calc_pda(self, program_id):
        
        _credential_pda = Pubkey.find_program_address(
            [PdaSeed.CREDENTIAL_SEED, bytes(self.authority), self.name.encode()], 
            convert_to_pubkey(program_id)
        )[0]

        return _credential_pda
    

    def create_instruction(self, _payer, program_id):

        credential_pda = self.calc_pda(program_id)
        
        payload_ser = Credential.create_borsh_struct.build({
            "id": InstructionVariant.CREATE_CREDENTIAL_DISCRIMINATOR, 
            "name": self.name, 
            "signers": [ list(bytes(x)) for x in self.signers]
        })

        instruction = Instruction(
                accounts=[
                    AccountMeta(convert_to_pubkey(_payer), True, True),
                    AccountMeta(credential_pda, False, True),
                    AccountMeta(self.authority, True, True),
                    AccountMeta(SYS_PROGRAM_ID, False, False),
                    ],
                program_id=convert_to_pubkey(program_id), 
                data=payload_ser
            )
        
        return instruction


    @staticmethod
    def parse_instruction(raw_instruction):
        
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

        decode_data = Credential.create_borsh_struct.parse(instruction.data)
        authority = instruction.accounts[2].pubkey

        credential = Credential({
                "discriminator": decode_data["id"],
                "authority": authority,
                "name": decode_data["name"],
                "signers": decode_data["signers"],
            }
        )
        
        return credential, program_id
    

    def change_signers_instruction(self, _payer, new_signers, program_id):

        credential_pda = Pubkey.find_program_address(
            [b"credential", bytes(self.authority), self.name.encode()], 
            convert_to_pubkey(program_id)
        )[0]
        
        payload_ser = Credential.change_signers_borsh_struct.build({
            "id": InstructionVariant.CHANGE_AUTHORIZED_SIGNERS_DISCRIMINATOR, 
            "signers": [ list(bytes(convert_to_pubkey(x))) for x in new_signers]
        })

        instruction = Instruction(
                accounts=[
                    AccountMeta(convert_to_pubkey(_payer), True, True),
                    AccountMeta(self.authority, True, True),
                    AccountMeta(credential_pda, False, True),
                    AccountMeta(SYS_PROGRAM_ID, False, False),
                    ],
                program_id=convert_to_pubkey(program_id), 
                data=payload_ser
            )
        
        return instruction


