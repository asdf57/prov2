import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KaufManager:
    def __init__(self, node_name: str):
        self.node_name = node_name
        logger.info(f"Initialized KaufManager for node: {node_name}")

    def turn_on(self) -> str:
        url = f"http://{self.node_name}.outlet.ryuugu.dev/switch/kauf_plug/turn_on"
        logger.info(f"Attempting to turn on {self.node_name} at {url}")
        
        try:
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully turned on {self.node_name}. Status code: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            return response.text
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while turning on {self.node_name} at {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to turn on {self.node_name}: {e}")
            raise

    def turn_off(self) -> str:
        url = f"http://{self.node_name}.outlet.ryuugu.dev/switch/kauf_plug/turn_off"
        logger.info(f"Attempting to turn off {self.node_name} at {url}")
        
        try:
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully turned off {self.node_name}. Status code: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            return response.text
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while turning off {self.node_name} at {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to turn off {self.node_name}: {e}")
            raise