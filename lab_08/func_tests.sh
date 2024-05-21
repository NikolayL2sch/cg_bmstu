jq -c '.[]' "func_tests.json" | while IFS= read -r row; do
    name=$(echo $row | jq -r '.name')
    desc=$(echo $row | jq -r '.desc')
    input_args=$(echo $row | jq -r '.input_args')

    touch ./results/"$name"_desc.txt
    echo -e "$desc" > ./results/"$name"_desc.txt

    eval "coverage run -a main.py "$input_args""
done

eval "coverage report" >> "./report-functesting-latest.txt"