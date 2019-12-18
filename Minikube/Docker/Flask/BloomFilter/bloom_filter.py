#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import hashlib
import argparse
import string
import random
import zlib     # for crc32
"""
    Microsoft code assessment
    -------------------------
    http://codekata.com/kata/kata05-bloom-filters/
    This is a commandline tool implemented in python3. It has been developed
    and tested on Debian 9.
    Usage:
        1. Build bitmap and save:
        python3 bloom_filter.py build 
        
        2. Spell check a word
        python3 bloom_filter.py check _word_
        
        3. Generate _num_ random words to compute accuracy
        python3 bloom_filter.py accuracy
"""
__author__ = "Yongjian Feng"
__email__ = "kin.feng@gmail.com"

# Constants
BUILD_SUBCOMMAND = "build"
CHECK_SUBCOMMAND = "check"
ACCURACY_SUBCOMMAND = "accuracy"
# @TODO following suggestion of the author of the webpage. Could be something else
NUM_CHAR_PER_WORD = 5
LOWER_CHARS = string.ascii_letters[:26]     # The first 26 are lower case chars


class BloomFilter:

    def __init__(self, sz=0, filename=None):
        """
        Need at least sz or filename to init bitmap
        :param sz:
        :param filename:
        """
        if sz > 0:
            self.bitmap = bytearray(sz)
            self.bitmap_sz = sz
        elif filename:
            self._read_file(filename)
            self.bitmap_sz = len(self.bitmap)
        else:
            raise Exception("Need sz or filename to initialize the bitmap")
        self.num_bits = self.bitmap_sz*8

        self.hex_digits = self._count_hex_digits()

    def check_word(self, word, num_checksum=1):
        """
        Spell check. Check whether the checksum(s) of this word is stored in
        the bitmap
        :param word:
        :param num_checksum:
        :return:
        """
        num_checksum = min(HashGenerator.MAX_CHECKSUMS, num_checksum)
        good = True
        for i in range(num_checksum):
            # hash_funcs contains 3 hash funcs we support so far
            cs = HashGenerator.get_hash(word, self.hex_digits, i) % self.num_bits
            bc, bm = BloomFilter.get_set_byte(cs)
            good = good and (self.bitmap[bc] & bm) > 0

        return good

    def create_bitmap(self, word_file, bitmap_file, num_checksum=1):
        """
        Read words from word_file, compute checksum
        :param word_file:
        :param bitmap_file:
        :return:
        """
        words = WordSource.get_words(word_file)

        for word in words:
            # @TODO. Remove the last '\n'. Need more clean up?
            word = word.replace('\n', '')
            # @TODO Convert word to lower case? Refer to Discussion in README.md
            num_checksum = min(HashGenerator.MAX_CHECKSUMS, num_checksum)
            for i in range(num_checksum):
                cs = HashGenerator.get_hash(word, self.hex_digits, i) % self.num_bits
                bc, bm = BloomFilter.get_set_byte(cs)
                self.bitmap[bc] = self.bitmap[bc] | bm

        self._write_file(bitmap_file)

    def check_accuracy(self, word_file, num_words, num_checksum=1):
        """
        Randomly generate num_words count of words with 5 chars.
        Use spell check to verify. If spell check returns good,
        look into the word_file dict to verify it is indeed there
        :param word_file:
        :param num_words:
        :param num_checksum:
        :return:
        """
        count_unfound = 0
        words = WordSource.get_words(word_file)

        for _ in range(num_words):
            word = make_random_word()
            good = self.check_word(word=word,
                                   num_checksum=num_checksum)
            if good:
                if word not in words:
                    count_unfound += 1

        ret = float(count_unfound) / num_words
        return ret

    def _read_file(self, name):
        """
        Read bitmap from a file
        :param name: file name
        :return:
        """
        self.bitmap = None
        try:
            with open(name, "rb") as infile:
                self.bitmap = infile.read()
        except FileNotFoundError:
            print("File {} not found".format(name))

    def _write_file(self, name):
        """
        Write the bitmap into a file
        :param arr: bitmap bytearray
        :param name: file name
        :return:
        """
        with open(name, "wb") as outfile:
            outfile.write(self.bitmap)

    def _count_hex_digits(self):
        """
        Use this to figure out how many hex digit we want from the checksum
        :return:
        """
        hex_count = len(hex(int(self.num_bits))) - 2
        return hex_count

    @staticmethod
    def get_set_byte(n):
        """
        Given an integer count which byte to modify
        :param n:
        :return:
        """
        byte_count = (n - 1)//8
        bit_shift = (n - 1) % 8
        bit_mask = 1 << bit_shift

        return byte_count, bit_mask


class HashGenerator:
    MAX_CHECKSUMS = 3  # only support md5, sha256, and crc32 at this point!

    @staticmethod
    def get_hash(in_str, digits, hash_type):
        """
        Facade design pattern. A unified interface for getting different types of hash.
        :param in_str:
        :param digits:
        :param hash_type: 1: md5, 2: sha256, 3: crc
        :return:
        """
        hash_funcs = [HashGenerator.get_md5_hash, HashGenerator.get_sha256_hash, HashGenerator.get_crc32_hash]
        if hash_type < len(hash_funcs):
            return hash_funcs[hash_type](in_str, digits)
        return 0

    @staticmethod
    def get_md5_hash(in_str, digits):
        """
        Compute md5 checksum of a given string, and return the
        last _digits_ count of hex
        :param in_str:
        :param digits:
        :return:
        """
        md5 = hashlib.md5()
        md5.update(in_str.encode("utf-8"))
        # @TODO: Here we assumed that the md5 checksum is longer than we want
        cs = md5.hexdigest()
        return int(cs[-digits:], 16)

    @staticmethod
    def get_sha256_hash(in_str, digits):
        """
        Compute sha256 checksum of a given string/word, and return the
        last _digits_ count of hex
        :param in_str:
        :param digits:
        :return:
        """
        sha256 = hashlib.sha256()
        sha256.update(in_str.encode("utf-8"))
        # @TODO: Here we assumed that the sha256 checksum is longer than we want
        cs = sha256.hexdigest()
        return int(cs[-digits:], 16)

    @staticmethod
    def get_crc32_hash(in_str, digits):
        """
        Compute crc32 checksum of a given string/word
        :param in_str:
        :param digits:
        :return:
        """
        hex_checksum = hex(zlib.crc32(in_str.encode("utf-8")) & 0xffffffff)
        # this is small enough to be stored in a long
        return int(hex_checksum, 16)


class WordSource:
    @staticmethod
    def get_words(name):
        """
        Facade design pattern. Provide flexibility to support more
        word source in the future.
        :param name:
        :return:
        """
        if name == "nltk":
            words = WordSource.read_nltk_words()
        else:
            words = WordSource.read_dict(name)
        return words

    @staticmethod
    def read_dict(name):
        """
        read words from dict
        :param name: file name
        :return: return list of words
        """
        words = []
        with open(name, "r") as infile:
            for line in infile:
                words.append(line)
        print("Using {} words from {}.".format(len(words), name))
        return words

    @staticmethod
    def read_nltk_words():
        """
        If you have nltk installed and you run this with network connection (for nltk to download
        latest resources), you can try words from nltk. Please note that nltk words are
        all in lower case.
        :return:
        """
        try:
            import nltk
            from nltk.corpus import words as nltk_words
            nltk.download("words", quiet=True)
            words = set(nltk_words.words())
            print("Using {} words from nltk.".format(len(words)))
            return list(words)
        except ImportError as e:
            print("nltk not installed. Install it first if you want to use words from nltk.")
            return []


def make_random_word():
    """
    Generate a random word of 5 chars. Note only the first char can be
    either upper or lower case, the rest are lower case. So this method
    is specifically for /usr/share/dict/words!
    @TODO: string.ascii_letters only contains ascii, not extended ascii. But our dict contains extended ascii
    :return:
    """
    # The first char can be upper or lower
    word = random.choice(string.ascii_letters)
    for __ in range(NUM_CHAR_PER_WORD - 1):
        # @TODO Assume that user is smart enough to use lower for the rest 4 chars
        word = word + random.choice(LOWER_CHARS)
    return word


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    sub_parser = parser.add_subparsers(title="Subcommands",
                                       help="One of these must be provided",
                                       description="valid subcommand",
                                       dest="cmd")
    sub_parser.required = True
    # 1. Build
    build_parser = sub_parser.add_parser(BUILD_SUBCOMMAND,
                                         help="build bitmap")
    build_parser.add_argument("-i", "--input",
                              help="word file with words separated by new line. Default /usr/share/dict/words",
                              default="/usr/share/dict/words")
    build_parser.add_argument("-o", "--output",
                              help="file to save the bitmap. Default bitmap.bin",
                              default="bitmap.bin")

    build_parser.add_argument("-n", "--num",
                              help="1 or 2. For number of kinds of checksum to use. Default 1, only md5",
                              default="1")
    #   Note on Debian, the word count is 99171
    #   16kB or 16KB is around 128000 to 131072. 75% will be set to 1 even for one checksum
    #   Default to 64KB. Note that we are using KB not kB here
    build_parser.add_argument("-s", "--size",
                              help="size of bitmap in KB. Default 64",
                              default="64")
    # 2. Check
    check_parser = sub_parser.add_parser(CHECK_SUBCOMMAND,
                                         help="spell check of a word")
    check_parser.add_argument("word",
                              help="word for spell check")
    check_parser.add_argument("-i", "--input",
                              help="bitmap file to use",
                              default="bitmap.bin")
    check_parser.add_argument("-n", "--num",
                              help="Num of checksums to use. Must match what used to create the bitmap",
                              default="1")
    # 3. Accuracy
    accuracy_parser = sub_parser.add_parser(ACCURACY_SUBCOMMAND,
                                            help="Generate random words to check accuracy")
    accuracy_parser.add_argument("-i", "--input",
                                 help="bitmap file to use",
                                 default="bitmap.bin")
    accuracy_parser.add_argument("-w", "--words",
                                 help="word dict of words to validate",
                                 default="/usr/share/dict/words")
    accuracy_parser.add_argument("-n", "--num",
                                 help="number of random words to generate",
                                 default="1000")
    accuracy_parser.add_argument("-c", "--checksum",
                                 help="Num of checksums to use. MUST match what used to create the bitmap",
                                 default="1")
    #@TODO handle unkown args...
    args, unkown_args = parser.parse_known_args()

    if args.cmd == BUILD_SUBCOMMAND:
        word_file = args.input
        bitmap_file = args.output
        num_checksum = int(args.num)
        bitmap_sz = int(args.size)*1024
        b_filter = BloomFilter(sz=bitmap_sz)
        b_filter.create_bitmap(word_file=word_file,
                               bitmap_file=bitmap_file,
                               num_checksum=num_checksum)

    elif args.cmd == CHECK_SUBCOMMAND:
        bitmap_file = args.input
        word = args.word
        num_checksum = int(args.num)
        b_filter = BloomFilter(filename=bitmap_file)
        good = b_filter.check_word(word=word,
                                   num_checksum=num_checksum)
        result = "Correct" if good else "Wrong"
        print("Spell check using Bloom Filter:")
        print("\tThe spelling of \"{}\" is {}".format(word, result))

    elif args.cmd == ACCURACY_SUBCOMMAND:
        bitmap_file = args.input
        word_file = args.words
        num_words = int(args.num)
        num_checksum = int(args.checksum)
        b_filter = BloomFilter(filename=bitmap_file)
        fal_post = b_filter.check_accuracy(word_file=word_file,
                                           num_words=num_words,
                                           num_checksum=num_checksum)
        #@TODO improve output even more?
        print("Bloom Filter test using {} random words: ".format(num_words))
        print("\tFalse positive rate: {}".format(fal_post))
