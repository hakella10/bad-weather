clear
export MONGODB_URL='<mongodb-cluster-connection-string>'
export MONGODB_DBNAME='logs_database'

export GITREPO_TOKEN='<your-git-token>'
export GITREPO_OWNER='hakella10'
export GITREPO_NAME='bad-weather'
export GITREPO_BRANCH='main'

export LOGS_DIR='/home/ubuntu/ai/logai/store/logs'
export SPRINGBOOT_GUIDE_PDF='/home/ubuntu/ai/logai/store/docs/spring-boot-reference.pdf'

python3 data-pipeline.py

