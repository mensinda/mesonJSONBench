#!/usr/bin/env python3

import json
import os
import re
import sys
import timeit
import functools

DATA_PATH = 'testData'
TEMP_DIR = 'tmp'
NUMBER = 512

class Tester:
    def __init__(self, file):
        self.file = file
        self.file_size = os.path.getsize(self.file)
        self.results = {}

    def split(self):
        with open(self.file) as fp:
            dat = json.load(fp)

        for i, d in dat.items():
            with open(os.path.join(TEMP_DIR, '{}.json'.format(i)), 'w') as fp:
                json.dump(d, fp)

    def run_simple_load(self):
        with open(self.file, 'r') as fp:
            dat = json.load(fp)

        return dat

    def run_load_single(self, curr):
        with open(os.path.join(TEMP_DIR, '{}.json'.format(curr)), 'r') as fp:
            dat = json.load(fp)

        return dat

    def run_load_all(self):
        dat = {}
        for i in ['benchmarks', 'buildoptions', 'buildsystem_files', 'dependencies', 'installed', 'projectinfo', 'targets', 'tests']:
            with open(os.path.join(TEMP_DIR, '{}.json'.format(i)), 'r') as fp:
                dat[i] = json.load(fp)

        return dat

    def run(self):
        self.split()
        self.results = {
            'load_bigFile': timeit.Timer(self.run_simple_load),
            'load_all': timeit.Timer(self.run_load_all),
            'load_targets': timeit.Timer(functools.partial(self.run_load_single, 'targets')),
            'load_tests': timeit.Timer(functools.partial(self.run_load_single, 'tests')),
            'load_buildoptions': timeit.Timer(functools.partial(self.run_load_single, 'buildoptions')),
        }

        for i in self.results:
            tm = self.results[i]
            time = tm.timeit(NUMBER)
            self.results[i] = int(((time / NUMBER) * 1000000))

    def print_results(self):
        name = os.path.basename(self.file)
        print('\nFILE: {:<24} -- SIZE: {} KB'.format(name, self.file_size / 1000))
        print('{:=<52}'.format('='))
        for i, time in self.results.items():
            print('    {:>20} : {:<7}usec'.format(i, time))

def main():
    if not os.path.exists(DATA_PATH) or not os.path.isdir(DATA_PATH):
        print('Data dir {} does not exist'.format(DATA_PATH))
        return 1

    os.makedirs(TEMP_DIR, exist_ok=True)

    files = os.listdir(DATA_PATH)
    reg = re.compile(r'.+\.json$')
    tests = []
    for i in files:
        if not reg.match(i):
            continue

        t = Tester(os.path.abspath('{}/{}'.format(DATA_PATH, i)))
        print('Running tests for {}'.format(i))
        t.run()
        tests += [t]

    for i in tests:
        i.print_results()

    return 0

if __name__ == '__main__':
    sys.exit(main())
