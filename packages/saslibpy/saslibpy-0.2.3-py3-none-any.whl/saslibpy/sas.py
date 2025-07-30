from enum import IntEnum
from solders.pubkey import Pubkey
from solders.keypair import Keypair

from borsh_construct import I8, I16, I32, I64, I128, U8, U16, U32, U64, U128
from borsh_construct import Bool, String, CStruct, Vec

SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
TOKEN_2022_PROGRAM_ID = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

DEVNET_PROGRAM_ID = Pubkey.from_string('22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG')
TESTNET_PROGRAM_ID = None
MAINNET_PROGRAM_ID = Pubkey.from_string('22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG')


id_to_type = {
    0:U8,
    1:U16,
    2:U32,
    3:U64,
    4:U128,
    5:I8,
    6:I16,
    7:I32,
    8:I64,
    9:I128,
    10:Bool,
    #11:Char,
    12:String,
    13:Vec(U8),
    14:Vec(U16),
    15:Vec(U32),
    16:Vec(U64),
    17:Vec(U128),
    18:Vec(I8),
    19:Vec(I16),
    20:Vec(I32),
    21:Vec(I64),
    22:Vec(I128),
    23:Vec(Bool),
   # 24:Vec(Char),
    25:Vec(String)
}

type_to_id = {
    U8:0,
    U16:1,
    U32:2,
    U64:3,
    U128:4,
    I8:5,
    I16:6,
    I32:7,
    I64:8,
    I128:9,
    Bool:10,
    #Char:11,
    String:12,
    Vec(U8):13,
    Vec(U16):14,
    Vec(U32):15,
    Vec(U64):16,
    Vec(U128):17,
    Vec(I8):18,
    Vec(I16):19,
    Vec(I32):20,
    Vec(I64):21,
    Vec(I128):22,
    Vec(Bool):23,
    #Vec(Char):24,
    Vec(String):25
}

class PdaSeed(object):

    ATTESTATION_SEED = b"attestation"
    CREDENTIAL_SEED = b"credential"
    SCHEMA_SEED = b"schema"
    EVENT_AUTHORITY_SEED = b"eventAuthority"
    SAS_SEED = b"sas"
    SCHEMA_MINT_SEED = b"schemaMint"
    ATTESTATION_MINT_SEED = b"attestationMint"


# Instruction variants for target program
class InstructionVariant(IntEnum):

    CREATE_CREDENTIAL_DISCRIMINATOR = 0
    CREATE_SCHEMA_DISCRIMINATOR = 1
    CHANGE_SCHEMA_STATUS_DISCRIMINATOR = 2
    CHANGE_AUTHORIZED_SIGNERS_DISCRIMINATOR = 3
    CHANGE_SCHEMA_DESCRIPTION_DISCRIMINATOR = 4
    CHANGE_SCHEMA_VERSION_DISCRIMINATOR = 5
    CREATE_ATTESTATION_DISCRIMINATOR = 6
    CLOSE_ATTESTATION_DISCRIMINATOR = 7
    EMIT_EVENT_DISCRIMINATOR = 8
    TOKENIZE_SCHEMA_DISCRIMINATOR = 9
    CREATE_TOKENIZED_ATTESTATION_DISCRIMINATOR = 10
    CLOSE_TOKENIZED_ATTESTATION_DISCRIMINATOR = 11


def convert_to_pubkey(_pubkey):

    if isinstance(_pubkey, Pubkey):
        return _pubkey
    elif isinstance(_pubkey, Keypair):
        return _pubkey.pubkey()
    elif isinstance(_pubkey, str):
        return Pubkey.from_string(_pubkey)
    elif isinstance(_pubkey, bytes):
        return Pubkey.from_bytes(_pubkey)
    elif isinstance(_pubkey, list):
        return Pubkey.from_bytes(bytes(_pubkey))
    else:
        return _pubkey


def get_associated_token_address( mint: Pubkey, owner: Pubkey) -> Pubkey:
    
    seeds = [
        bytes(owner),
        bytes(TOKEN_2022_PROGRAM_ID),
        bytes(mint)
    ]

    return Pubkey.find_program_address(seeds,
        ASSOCIATED_TOKEN_PROGRAM_ID
    )[0]
