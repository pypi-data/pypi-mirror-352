import json
from random import shuffle

from src.canadian_address_parser.address_parser import AddressParser
from src.canadian_address_parser.data.raw_address import RawAddress
from src.canadian_address_parser.errors.unable_parse_model_output import UnableToParseModelOutputError


def test_addresses(address_parser: AddressParser, jonas_samples_path: str):
    with open(jonas_samples_path, 'r') as file:
        file_content = file.read()

    json_content = json.loads(file_content)

    res = list(filter(lambda x: x.province_code is not None, [RawAddress(
            address_line_1=x["AddressLine1"],
            address_line_2=x["AddressLine2"],
            address_line_3=x["AddressLine3"],
            address_line_4=x["AddressLine4"],
            postal_code=x["PostalZipCode"],
            province_code=x["ProvinceStateCountyCode"],
        ) for x in [x['raw'] for x in json_content]]))
    shuffle(res)

    for sample in res:
        try:
            output = address_parser.parse_address(sample)
            print(f'\nInput:  {sample}')
            print(f'Output: {output}\n')
        except UnableToParseModelOutputError:
            print(f'Unable to parse model json output: {sample}')