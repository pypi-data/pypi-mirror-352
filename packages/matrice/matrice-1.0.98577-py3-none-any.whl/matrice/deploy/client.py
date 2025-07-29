import numpy as np
import time
import threading
import logging
import json
from datetime import datetime, timezone
from queue import Queue
from matrice.deploy.client_utils import get_input_data, FastAPIClientUtils, TritonClientUtils

class MatriceDeployClient:

    def __init__(self, session, deployment_id, auth_key):
        self.session = session
        self.rpc = self.session.rpc
        self.deployment_id = deployment_id
        self.auth_key = auth_key

        self.client = None
        self.client_number = 0
        self.clients = []
        self.instances_info = None
        self.index_to_category = {}

        self.log_prediction_info_queue = Queue()
        self.last_refresh_time = 0
        logging.info(f"Initializing MatriceDeployClient for deployment {deployment_id}")
        self.refresh_deployment_info()
        self.client_utils = FastAPIClientUtils() if self.server_type == "fastapi" else TritonClientUtils(self.connection_protocol, self.model_id)
        self.start_log_prediction_info_thread()

    def refresh_deployment_info(self):
        if (time.time() - self.last_refresh_time < 60) and self.instances_info:
            return
        self.last_refresh_time = time.time()

        logging.info(f"Refreshing deployment info for deployment {self.deployment_id}")
        response = self.rpc.get(f"/v1/deployment/get_deployment_without_auth_key/{self.deployment_id}")
        if response.get("success"):
            self.deployment_info = response["data"]
            self.model_id = self.deployment_info["_idModel"]
            self.model_type = self.deployment_info["modelType"]
            self.runningInstances = self.deployment_info["runningInstances"]
            self.instances_info = [
                {
                    "ip_address": instance["ipAddress"],
                    "port": instance["port"],
                    "instance_id": instance["modelDeployInstanceId"],
                }
                for instance in self.runningInstances
                if instance.get("deployed", False)
            ]
            self.server_type = self.deployment_info.get("serverType", "fastapi")
            self.connection_protocol = (
                "grpc" if "grpc" in self.server_type.lower() else "rest"
            )
            logging.info(f"Successfully refreshed deployment info. Found {len(self.instances_info)} running instances")
            return response
        else:
            error_msg = response.get("message", "Unknown error occurred")
            logging.error(f"Failed to refresh deployment info: {error_msg}")
            raise Exception(error_msg)

    def get_index_to_category(self):
        try:
            logging.info(f"Getting index to category mapping for model {self.model_id}")
            if self.model_type == "trained":
                url = f"/v1/model/model_train/{self.model_id}"
            elif self.model_type == "exported":
                url = f"/v1/model/get_model_train_by_export_id?exportId={self.model_id}"
            else:
                error_msg = f"Unsupported model type: {self.model_type}"
                logging.error(error_msg)
                raise Exception(error_msg)

            response = self.rpc.get(url)
            if not response.get("data"):
                error_msg = "No data returned from model train endpoint"
                logging.error(error_msg)
                raise Exception(error_msg)

            modelTrain_doc = response["data"]
            self.index_to_category = modelTrain_doc.get("indexToCat", {})
            logging.info(f"Successfully retrieved index to category mapping with {len(self.index_to_category)} categories")
            return self.index_to_category
        except Exception as e:
            error_msg = f"Failed to get index to category: {e}"
            logging.error(error_msg)
            raise Exception(error_msg)

    def get_prediction(
        self, input_path: str = None, input_bytes: bytes = None, input_url: str = None, extra_params: dict = None
    ):
        if not any([input_path, input_bytes, input_url]):
            error_msg = "Must provide one of: input_path, input_bytes, or input_url"
            logging.error(error_msg)
            raise ValueError(error_msg)

        logging.info("Getting prediction for input")
        input_data = get_input_data(input_path, input_bytes, input_url)
        if extra_params:
            extra_params = json.dumps(extra_params)
        client = self.get_client()
        start_time = time.time()

        results = self.client_utils.inference(client, input_data)
        latency = time.time() - start_time
        logging.debug(f"Prediction completed in {latency:.3f} seconds")

        self.log_prediction_info_queue.put((results, latency, datetime.now(timezone.utc).isoformat(), input_data, self.client["instance_id"]))

        return results

    async def get_prediction_async(
        self, input_path: str = None, input_bytes: bytes = None, input_url: str = None, extra_params: dict = None
    ):
        if not any([input_path, input_bytes, input_url]):
            error_msg = "Must provide one of: input_path, input_bytes, or input_url"
            logging.error(error_msg)
            raise ValueError(error_msg)

        logging.info("Getting async prediction for input")
        input_data = get_input_data(input_path, input_bytes, input_url)
        if extra_params:
            extra_params = json.dumps(extra_params)
        client = self.get_client()
        start_time = time.time()

        results = await self.client_utils.async_inference(client, input_data)
        latency = time.time() - start_time
        logging.debug(f"Async prediction completed in {latency:.3f} seconds")

        self.log_prediction_info_queue.put((results, latency, datetime.now(timezone.utc).isoformat(), input_data, self.client["instance_id"]))

        return results

    def setup_clients(self):
        if not self.instances_info:
            self.refresh_deployment_info()
        if not self.instances_info:
            error_msg = "No instances found"
            logging.error(error_msg)
            raise Exception(error_msg)

        logging.info("Setting up clients")
        self.clients = self.client_utils.setup_clients(self.instances_info)

        if not self.clients:
            error_msg = "Failed to setup any clients"
            logging.error(error_msg)
            raise Exception(error_msg)
        logging.info(f"Successfully set up {len(self.clients)} clients")

    def update_client(self):
        if not self.clients:
            self.setup_clients()

        if not self.clients:
            error_msg = "No clients available after setup"
            logging.error(error_msg)
            raise Exception(error_msg)

        if self.client_number >= len(self.clients):
            self.client_number = 0

        self.client = self.clients[self.client_number]
        self.client_number += 1
        logging.debug(f"Updated to client {self.client_number} of {len(self.clients)}")

    def get_client(self):
        self.update_client()
        return self.client

    def log_prediction_info(self, prediction, latency, request_time, input_data, instance_id): # TODO: add the triton structure handling and upload input
        try:
            logging.info("Logging prediction info")
            self.refresh_deployment_info()
            payload = {
                "prediction": (
                    prediction.tolist()
                    if isinstance(prediction, np.ndarray)
                    else prediction
                ),
                "latency": latency,
                "reqTime": request_time,
                "_idDeploymentInstance": instance_id,
                "isMLAssisted": False,
            }

            response = self.rpc.post(
                path=f"/v1/model_prediction/log_prediction_info/{self.deployment_id}",
                payload=payload,
            )
            logging.info("Successfully logged prediction info")
            return response
        except Exception as e:
            logging.warning(f"Failed to log prediction info: {e}")
            return None

    def log_prediction_info_thread(self):
        logging.info("Starting prediction info logging thread")
        while True:
            try:
                prediction, latency, request_time, input_data, instance_id = self.log_prediction_info_queue.get()
                self.log_prediction_info(prediction, latency, request_time, input_data, instance_id)
            except Exception as e:
                logging.error(f"Error in prediction info logging thread: {e}")

    def start_log_prediction_info_thread(self):
        logging.info("Starting prediction info logging background thread")
        threading.Thread(target=self.log_prediction_info_thread, daemon=True).start()
