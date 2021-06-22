if [[ $# -ne 4 ]] ; then
    echo 'Invalid arguments'
    exit 1
fi

echo

echo "======================== MODEL BASED TESTING ========================"

echo
echo "=== Generator ==="
echo

echo "Generating instances..."

java -jar generator/out/artifacts/generator_jar/generator.jar $1 $2 $3

cd ../alloy_related/alloyToRailML

echo
echo "=== AlloyToRailML ==="
echo

mkdir -p /tmp/generated_models/railml

for x in $(seq 1 $3)
do
  echo "Parsing instance $x to railml..."
  python alloy2railml.py /tmp/generated_models/instance$x.xml > /tmp/generated_models/railml/railml$x.xml
done

echo
echo "=== Validator ==="
echo

cd ../../validator/
python test_validator.py /tmp/generated_models/railml $4

# for x in $(seq 1 $3)
# do
#   echo "Validating instance: $x..."
#   python validator_rml.py /tmp/generated_models/railml$x.xml
#   echo
#   echo
# done
