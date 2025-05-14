import json
import logging
import os
from train import train
from inference import start_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log that the script is being executed
logger.info("Executing main.py: Starting entry point script")

if __name__ == '__main__':
    sm_channels = json.loads(os.environ.get('SM_CHANNELS', '[]'))
    logger.info(f"SM_CHANNELS: {sm_channels}")

    if 'train' in sm_channels:
        logger.info("Training mode detected, executing training")
        train_dir = '/opt/ml/input/data/train'
        model_dir = '/opt/ml/model'
        train(train_dir, model_dir)
    else:
        logger.info("Inference mode detected, starting inference server")
        start_server()