DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker run -v $DIR/collections:/etc/newman -t postman/newman_ubuntu1404:3.8.1 --collection="CohortePlatform_Demo.postman_collection.json"