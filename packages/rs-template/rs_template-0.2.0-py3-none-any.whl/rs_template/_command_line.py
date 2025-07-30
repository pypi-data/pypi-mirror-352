
"""Example command-line utility"""

import argparse


def do_boring_thing(first_arg, second_arg, third_arg):

    print(f"First argument provided: {first_arg}")

    print(f"Second argument is {second_arg}, which can be rounded to {int(second_arg)}")

    print(f"Third argument: {third_arg}")

    return

def create_parser():
    """
    This function defines the argument parser for your command-line utility.

    In order for documentation to build properly, this function must exist and return an argparse.ArgumentParser object
    """

    parser = argparse.ArgumentParser(
        description='This is a basic parser, showing how command-line options are displayed in online documentation.'
    )

    parser.add_argument("--first-arg",
                        required=True,
                        help="First command line argument. This argument is required.")

    parser.add_argument("--second-arg",
                        required=True,
                        type=float,
                        help="Second command line argument. This argument is required and must be a float.")

    parser.add_argument("--third-arg",
                        required=False,
                        default="typical value",
                        help="Third command line argument. This argument is optional, defaults to 'typical value'")

    # note that this line must be "return parser" and NOT "return parser.parse_args()".
    # The latter will throw an error when trying to build online docs
    return parser

def main():

    parser = create_parser()
    args = parser.parse_args()

    do_boring_thing(args.first_arg,
                    args.second_arg,
                    args.third_arg)

    return

if __name__=="__main__":
    main()
