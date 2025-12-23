xhost +

sudo docker run -it --rm \
--gpus all \
--shm-size=8g \
--network=host \
--privileged \
--device=/dev/dri:/dev/dri \
-e NVIDIA_DRIVER_CAPABILITIES=all \
-e DISPLAY=$DISPLAY \
-e QT_X11_NO_MITSHM=1 \
-e VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json \
-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
-v $HOME/.Xauthority:/root/.Xauthority:rw \
-v ${PWD}:/workspace \
--name maniskill \
maniskill:latest \
/bin/bash