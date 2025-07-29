import requests
from io import BytesIO
import numpy as np
import logging
from matrice.utils import dependencies_check
dependencies_check(["pillow"])
from PIL import Image  # noqa: E402

class FastAPIClientUtils():
    def __init__(self):
        dependencies_check(["httpx"])
        import httpx
        self.http_client = httpx.Client(timeout=30, follow_redirects=True)
        self.async_client = httpx.AsyncClient(timeout=30, follow_redirects=True)
        self.clients = []
        logging.info("Initialized FastAPIClientUtils")

    def setup_clients(self, instances_info):
        logging.info(f"Setting up FastAPI clients for {len(instances_info)} instances")
        self.clients = [{
                    "url": f"http://{instance['ip_address']}:{instance['port']}/inference",
                    "instance_id": instance["instance_id"],
                }
                for instance in instances_info
            ]
        logging.info(f"Successfully set up {len(self.clients)} FastAPI clients")
        return self.clients

    def inference(self, client, input_data, extra_params=None):
        try:
            logging.debug(f"Making inference request to {client['url']}")
            resp = self.http_client.post(
                    url=client["url"], files={"input": input_data}, data={"extra_params": extra_params}
                ).json()
            if "result" in resp:
                logging.debug("Successfully got inference result")
                return resp["result"]
            else:
                logging.error(f"Inference failed, response: {resp}")
                raise Exception(f"Inference failed, response: {resp}")
        except Exception as e:
            logging.error(f"FastAPI inference failed: {e}")
            raise Exception(f"FastAPI inference failed: {e}")

    async def async_inference(self, client, input_data, extra_params=None):
        try:
            logging.debug(f"Making async inference request to {client['url']}")
            resp = await self.async_client.post(
                url=client["url"], files={"input": input_data}, data={"extra_params": extra_params}
            )
            resp_json = resp.json()
            if "result" in resp_json:
                logging.debug("Successfully got async inference result") 
                return resp_json["result"]
            else:
                logging.error(f"Async inference failed, response: {resp_json}")
                raise Exception(f"Async inference failed, response: {resp_json}")
        except Exception as e:
            logging.error(f"Async FastAPI inference failed: {e}")
            raise Exception(f"Async FastAPI inference failed: {e}")

class TritonClientUtils():
    def __init__(self, connection_protocol, model_id):
        self.model_id = model_id
        self.clients = []
        self.data_type_mapping = {
            6: "TYPE_INT8",
            7: "TYPE_INT16", 
            8: "TYPE_INT32",
            9: "TYPE_INT64",
            10: "TYPE_FP16",
            11: "TYPE_FP32",
            12: "TYPE_FP64",
        }
        self.numpy_data_type_mapping = {
            "INT8": np.int8,
            "INT16": np.int16,
            "INT32": np.int32,
            "INT64": np.int64,
            "FP16": np.float16,
            "FP32": np.float32,
            "FP64": np.float64,
        }
        self.connection_protocol = connection_protocol.lower()
        self.httpclient = None
        self.grpcclient = None
        logging.info(f"Initializing TritonClientUtils with {connection_protocol} protocol")
        
        if "grpc" in self.connection_protocol:
            try:
                dependencies_check(["tritonclient[grpc]"])
                import tritonclient.grpc as grpcclient
                self.grpcclient = grpcclient
                logging.info("Successfully imported tritonclient.grpc")
            except ImportError:
                logging.info("Failed to import tritonclient.grpc")
        else:
            try:
                dependencies_check(["tritonclient[http]"])
                import tritonclient.http as httpclient
                self.httpclient = httpclient
                logging.info("Successfully imported tritonclient.http")
            except ImportError:
                logging.info("Failed to import tritonclient.http")

    def setup_clients(self, instances_info):
        logging.info(f"Setting up Triton clients for {len(instances_info)} instances")
        self.instances_info = instances_info
        clients = []
        if "rest" in self.connection_protocol:
            if self.httpclient is None:
                logging.info("HTTP client not available - failed to import tritonclient.http")
                return clients
            for instance in self.instances_info:
                try:
                    clients.append(self._setup_rest_client(instance))
                    logging.info(f"Successfully set up REST client for instance {instance['instance_id']}")
                except Exception as e:
                    logging.error(
                        f"Warning: Failed to setup REST client for instance {instance['instance_id']}: {e}"
                    )
        elif "grpc" in self.connection_protocol:
            if self.grpcclient is None:
                logging.info("gRPC client not available - failed to import tritonclient.grpc")
                return clients
            for instance in self.instances_info:
                try:
                    clients.append(self._setup_grpc_client(instance))
                    logging.info(f"Successfully set up gRPC client for instance {instance['instance_id']}")
                except Exception as e:
                    logging.error(
                        f"Warning: Failed to setup gRPC client for instance {instance['instance_id']}: {e}"
                    )
        logging.info(f"Successfully set up {len(clients)} Triton clients")
        return clients

    def _setup_rest_client(self, instance_info):
        logging.debug(f"Setting up REST client for instance {instance_info['instance_id']}")
        client = self.httpclient.InferenceServerClient(
                    url=f"{instance_info['ip_address']}:{instance_info['port']}"
                )
        model_config = client.get_model_config(
            model_name=self.model_id, model_version="1"
        )
        input = self.httpclient.InferInput(
                model_config["input"][0]["name"],
                [1, 3, 244, 244][
                    : 4 - len(model_config["input"][0]["dims"])
                ]
                + model_config["input"][0]["dims"],
                model_config["input"][0]["data_type"].split("_")[-1],
            )
        
        output = self.httpclient.InferRequestedOutput(model_config["output"][0]["name"])
        return {
                "client": client,
                "input": input,
                "output": output,
                "instance_id": instance_info["instance_id"],
            }

    def _setup_grpc_client(self, instance_info):
        logging.debug(f"Setting up gRPC client for instance {instance_info['instance_id']}")
        client = self.grpcclient.InferenceServerClient(
                url=f"{instance_info['ip_address']}:{instance_info['port']}"
            )
        model_config = client.get_model_config(
            model_name=self.model_id, model_version="1"
        )
        input = self.grpcclient.InferInput(
                model_config.config.input[0].name,
                [1, 3, 244, 244][
                    : 4 - len(model_config.config.input[0].dims)
                ]
                + list(model_config.config.input[0].dims),
                self.data_type_mapping[
                    model_config.config.input[0].data_type
                ].split("_")[-1],
            )
        
        output = self.grpcclient.InferRequestedOutput(model_config.config.output[0].name)
        return {
                "client": client,
                "input": input,
                "output": output,
                "instance_id": instance_info["instance_id"],
            }
        
    def inference(self, client, input_data, extra_params=None):
        try:
            logging.debug(f"Making inference request for instance {client['instance_id']}")
            # Convert input bytes to numpy array and reshape to expected format
            input_data = np.expand_dims(
                np.array(
                    Image.open(BytesIO(input_data))
                    .convert("RGB")
                    .resize(client["input"].shape()[2:])
                )
                .astype(self.numpy_data_type_mapping[client["input"].datatype()])
                .transpose(2, 0, 1),
                axis=0,
            )

            client["input"].set_data_from_numpy(input_data)

            resp = client["client"].infer(
                model_name=self.model_id,
                model_version="1",
                inputs=[client["input"]],
                outputs=[client["output"]],
            )

            logging.debug("Successfully got inference result")
            return resp.as_numpy(client["output"].name())

        except Exception as e:
            logging.error(f"Triton inference failed: {e}")
            raise Exception(f"Triton inference failed: {e}")

    async def async_inference(self, client, input_data, extra_params=None): # TODO: test it
        try:
            logging.debug(f"Making async inference request for instance {client['instance_id']}")
            # Convert input bytes to numpy array and reshape to expected format
            input_data = np.expand_dims(
                np.array(
                    Image.open(BytesIO(input_data))
                    .convert("RGB")
                    .resize(client["input"].shape()[2:])
                )
                .astype(self.numpy_data_type_mapping[client["input"].datatype()])
                .transpose(2, 0, 1),
                axis=0,
            )

            client["input"].set_data_from_numpy(input_data)

            if "rest" in self.connection_protocol:
                resp = await client["client"].async_infer(
                    model_name=self.model_id,
                    model_version="1", 
                    inputs=[client["input"]],
                    outputs=[client["output"]]
                )
            else:
                # gRPC async call
                resp = await client["client"].infer_async(
                    model_name=self.model_id,
                    model_version="1",
                    inputs=[client["input"]],
                    outputs=[client["output"]]
                )

            logging.debug("Successfully got async inference result")
            return resp.as_numpy(client["output"].name())

        except Exception as e:
            logging.error(f"Async Triton inference failed: {e}")
            raise Exception(f"Async Triton inference failed: {e}")

def get_input_data(
        input_path: str = None, input_bytes: bytes = None, input_url: str = None
    ):
    try:
        logging.debug("Getting input data")
        if input_path:
            logging.debug(f"Reading input from path: {input_path}")
            with open(input_path, "rb") as img_file:
                input_data = img_file.read()
        elif input_bytes:
            logging.debug("Using provided input bytes")
            input_data = input_bytes
        elif input_url:
            logging.debug(f"Downloading input from URL: {input_url}")
            response = requests.get(input_url, timeout=10)
            response.raise_for_status()
            input_data = response.content
        else:
            logging.error("No input source provided")
            raise ValueError(
                "Must provide one of: input_path, input_bytes, or input_url"
            )
        logging.debug("Successfully got input data")
        return input_data
    except Exception as e:
        logging.error(f"Failed to get input data: {e}")
        raise Exception(f"Failed to get input data: {e}")
