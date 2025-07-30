import json
from dataclasses import asdict

from .models.canadian_address_model import AddressParserModel
from .data.clean_address import CleanAddress
from .data.raw_address import RawAddress
from .errors.unable_parse_model_output import UnableToParseModelOutputError


class AddressParser:
    def __init__(self, hf_token: str, hf_model_path: str) -> None:
        self.__address_model = AddressParserModel(hf_model_path, hf_token)
        self.__model_loaded = False

    @staticmethod
    def __create_raw_address_text(raw_address: RawAddress) -> str:
        return f'{asdict(raw_address)}'

    def parse_address(self, raw_address: RawAddress) -> CleanAddress:
        if not self.__model_loaded:
            self.__address_model.load()
            self.__model_loaded = True

        raw_address_text = self.__create_raw_address_text(raw_address)

        try:
            model_output_text = self.__address_model.parse_address(raw_address_text)
            json_parsed = json.loads(model_output_text)
        except (json.decoder.JSONDecodeError, ValueError):
            raise UnableToParseModelOutputError()

        try:
            clean_address = CleanAddress(
                postal_code=json_parsed['POSTAL_CODE'],
                city=json_parsed['CITY'],
                province_code=json_parsed['PROVINCE_CODE'],
                address_line=json_parsed['ADDRESS_LINE'],
            )
        except KeyError:
            raise UnableToParseModelOutputError()

        return clean_address
