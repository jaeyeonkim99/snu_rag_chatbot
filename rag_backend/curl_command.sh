curl -G http://localhost:8000/rag/ \
    -H "Content-Type: application/json" \
    --data-urlencode 'query=서울대학생 졸업 연한이 어떻게 되나요' \
    | jq .