import sys

from nft_generator.Collection import Collection


def main():
    collection = Collection(sys.argv)
    collection.generate()
    collection.render()
    collection.print_stat()
    collection.generate_metadata()


if __name__ == "__main__":
    main()
