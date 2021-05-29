cd ../alloy_related/alloyToRailML

mkdir generated
for x in {1..50}
do
  python alloy2railml.py ../../model_based_testing/generated_models/instance$x.xml > generated/railml$x.xml
done

mv generated ../../validator/examples

cd ../../validator/
for x in {1..50}
do
  echo "Validating instance: $x"
  python validator_rml.py generated/railml$x.xml
  echo
  echo
  sleep 2
done

rm -rf examples/generated
