DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ssh -o StrictHostKeyChecking=no -i $1 root@api-dev.cohorte.tech $(cat $DIR/../docker/demo/start_instance.sh)