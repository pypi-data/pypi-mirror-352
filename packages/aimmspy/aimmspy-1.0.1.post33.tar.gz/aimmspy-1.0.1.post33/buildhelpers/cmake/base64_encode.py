import argparse
import base64

def main():
    parser = argparse.ArgumentParser(description='Encode or decode a string into base64')
    parser.add_argument('input_string', type=str, help='The string to be processed')
    parser.add_argument('-d', '--decode', action='store_true', help='Decode the input string')
    parser.add_argument('-e', '--encode', action='store_true', help='Encode the input string')

    args = parser.parse_args()

    if args.encode:
        encoded_string = base64.b64encode(args.input_string.encode()).decode()
        print(f'{encoded_string}')
    elif args.decode:
        decoded_string = base64.b64decode(args.input_string).decode()
        print(f'{decoded_string}')
    else:
        print('Error: Please specify either --encode or --decode')
        exit(1)

if __name__ == '__main__':
    main()