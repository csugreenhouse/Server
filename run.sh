set -e 
echo "Running tests "
if ! pytest; then
    echo "Tests failed"
    exit 1
fi   
    
echo "All tests passed"