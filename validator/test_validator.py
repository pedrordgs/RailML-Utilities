from unittest.runner import TextTestRunner
from colorama import Fore, Back, Style
from validator_rml import verify
import sys
import os


def test_file(fp, expected_fail):
    f = open(os.devnull, 'w')
    out = sys.stdout
    sys.stdout = f

    failed_properties = verify(fp)

    sys.stdout = out

    print("\033[1mTesting file \033[0m" + fp)
    print(Fore.YELLOW + "\tExpected rules to fail: " + Style.RESET_ALL + str(expected_fail))

    print(Fore.YELLOW + "\tRules that failed: " + Style.RESET_ALL + str(failed_properties))

    if failed_properties == expected_fail:
        print(Fore.GREEN + "\tTest passed" + Style.RESET_ALL)
        return True
    else:
        print(Fore.RED + "\tTest Failed" + Style.RESET_ALL)
        return False



def test_dir(fp, expected_fail):
    passed = 0
    failed = 0
    tests_failed = []

    print("\033[1mTesting every files from directory \033[0m" + fp)
    print()
    print()

    for f in os.listdir(fp):
        ff = os.path.join(fp,f)
        if os.path.isfile(ff):
            if test_file(ff, expected_fail):
                passed = passed + 1
            else:
                failed = failed + 1
                tests_failed.append(f)
        print()

    print()
    print()
    if failed == 0:
        print(Fore.GREEN + "OK " + Fore.LIGHTBLUE_EX + str(passed) + Fore.GREEN + " tests passed" + Style.RESET_ALL)
    else:
        print(Fore.RED + "NOK " + Fore.LIGHTBLUE_EX + str(failed) + Fore.RED + " tests failed"  + Style.RESET_ALL)
        for failed in tests_failed:
            print("\t" + failed)



fp = sys.argv[1]
expected_fail = set(map(int,sys.argv[2:]))

if os.path.isdir(fp):
    test_dir(fp,expected_fail)
elif os.path.isfile(fp):
    test_file(fp,expected_fail)
else:
    print("Bad argument")
