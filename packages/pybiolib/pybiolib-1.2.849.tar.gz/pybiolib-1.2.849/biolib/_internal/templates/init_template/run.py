import argparse

from biolib.sdk import Runtime


def parse_args():
    parser = argparse.ArgumentParser(description='Process some biological sequences.')
    parser.add_argument('--input', type=str, required=True, help='Input protein sequences')
    return parser.parse_args()


def main(args):
    sequence = args.input
    # Add your processing logic here
    print(f'Received sequence: {sequence}')


if __name__ == '__main__':
    args = parse_args()
    Runtime.set_result_name_prefix_from_fasta(args.input)
    main(args)
