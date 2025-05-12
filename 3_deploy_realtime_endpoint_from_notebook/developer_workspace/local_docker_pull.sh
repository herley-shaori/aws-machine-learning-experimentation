export ECR_IMAGE_ID='public.ecr.aws/sagemaker/sagemaker-distribution:latest-cpu'
docker run -it \
    -p 8888:8888 \
    -v `pwd`/sample-notebooks:/home/sagemaker-user/sample-notebooks \
    $ECR_IMAGE_ID jupyter-lab --no-browser --ip=0.0.0.0