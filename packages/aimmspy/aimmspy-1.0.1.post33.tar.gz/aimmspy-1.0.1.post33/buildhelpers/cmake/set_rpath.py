#     subprocess.run(['patchelf', '--set-rpath', '$ORIGIN/.', args.binary_path], check=True)

# python main
import argparse
import subprocess

def main(args):
    subprocess.run(['patchelf', '--set-rpath', '$ORIGIN/.', args.binary_path], check=True)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Strip debug symbols from a binary file.')
    parser.add_argument('binary_path', help='The path to the binary file.')
    
    args = parser.parse_args()
    main(args)