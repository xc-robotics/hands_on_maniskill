sudo docker run -it --rm \
--gpus all \
--shm-size=8g \
-e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics \
-v ${PWD}:/workspace \
--name maniskill \
maniskill:latest \
/bin/bash