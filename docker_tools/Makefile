CUR_DATE=`date +'%H:%M:%S_%m_%d_%y'`

# Move this and Dockerfile.any_pipeline to the  pipeline root directory

# all: build_docker_image login_to_dockerhub push_to_dockerhub

build_docker_image:
	docker build --no-cache -t knowengtest/pipeline:$(CUR_DATE) .

login_to_dockerhub:
	docker login --username=$(username) --password=$(password)

help:
	# Move this and Dockerfile.any_pipeline to the pipeline root directory then use: make build_docker_image
	# Really!

