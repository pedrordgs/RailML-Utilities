import sys
import os
import shutil
import re

if len(sys.argv) < 4:
    print("Insuficient arguments")
    exit(1)

alloyp = sys.argv[1]
run = sys.argv[2]
n = sys.argv[3]

tmp = "/tmp/generated_models"
tmprail = "/tmp/generated_models/railml"

expected_fail = set(sys.argv[4:])

if os.path.isdir(tmp):
    shutil.rmtree(tmp)


print()
print("\033[1m======================== MODEL BASED TESTING ========================\033[0m")

print()
print("=== Generator ===")
print()

print("Generating instances...")

javacmd = "java -jar generator/out/artifacts/generator_jar/generator.jar " + alloyp + " " + run + " " + n
os.system(javacmd)


print()
print("=== AlloyToRailML ===")
print()

os.system("mkdir -p " + tmprail)

for f in os.listdir(tmp):
    ff = os.path.join(tmp,f)
    if os.path.isfile(ff):
        i = re.findall(r'\d+', f)[0]
        os.system("./helpers/run_translator.sh " + ff + " " + os.path.join(tmprail, "railml" + i + ".xml"))

print()
print("=== Validator ===")
print()

os.system("./helpers/run_tester.sh " + tmprail + " " + (' ').join(expected_fail))






