from argparse import ArgumentParser

from utils import download_file, get_items, save_objects


def main(args):
    parser = ArgumentParser()
    parser.add_argument("-o", "--output", dest="output", required=True)
    options = parser.parse_args(args)
    try:
        res = download_file()
        items = get_items(res)
        out_path = save_objects(items, options.output)
        print(out_path)
    except Exception as err:
        print(err)
        return 1
    else:
        return 0


if __name__ == '__main__':
    main(["-o", "out.db"])

