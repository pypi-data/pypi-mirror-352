import argparse

from src.canadian_address_parser.address_parser import AddressParser
from src.canadian_address_parser.data.command_args import CommandArgs
from test_addresses import test_addresses


def get_params() -> CommandArgs:
    parser = argparse.ArgumentParser()

    parser.add_argument("model_path", default="", type=str)
    parser.add_argument("samples_path", default="", type=str)
    parser.add_argument('--device', default='cuda', type=str)

    args = parser.parse_args()

    return CommandArgs(
        model_path=args.model_path,
        device=args.device,
        samples_path=args.samples_path,
    )

if __name__ == "__main__":
    params = get_params()
    address_parser = AddressParser(params.model_path)

    test_addresses(address_parser, params.samples_path)