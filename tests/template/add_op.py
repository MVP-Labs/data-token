import json
import argparse

if __name__ == '__main__':
    print('hello world, data token')

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)

    args = parser.parse_args()
    op_args = json.load(open(args.config))

    print(op_args['arg1'] + op_args['arg2'])
