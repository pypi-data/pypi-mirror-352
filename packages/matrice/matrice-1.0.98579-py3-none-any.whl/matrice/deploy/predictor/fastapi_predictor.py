import requests
import uvicorn
from fastapi import Form, FastAPI, File, UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import logging
import threading
import json
from typing import Optional, Dict, Any


class MatriceFastAPIPredictor:
    def __init__(self, load_model, predict, actionTracker):
        """Initialize the predictor with model loading and prediction functions
        
        Args:
            load_model: Function to load the model
            predict: Function to run predictions
            actionTracker: Tracker for monitoring actions
        """
        try:
            logging.info("Initializing MatriceFastAPIPredictor")
            self.actionTracker = actionTracker
            logging.info("Loading model...")
            self.model = load_model(actionTracker)
            logging.info("Model loaded successfully")
            self.predict = self.create_lambda_from_function(predict)
            self.app = FastAPI()
            logging.info("Registering FastAPI endpoints")
            self._register_endpoints()
            logging.info("FastAPI endpoints registered successfully")
        except Exception as e:
            logging.error(f"Failed to initialize predictor: {str(e)}", exc_info=True)
            raise

    def create_lambda_from_function(self, func):
        """Create a wrapper function that handles parameter passing to the prediction function
        
        Args:
            func: The prediction function to wrap
            
        Returns:
            A wrapper function that handles parameter passing
        """
        def wrapper(model, input_data: Dict[str, Any]) -> Any:
            try:
                extra_params_dict = input_data.get("extra_params", {})
                # Extract the parameter names from the function
                param_names = func.__code__.co_varnames[:func.__code__.co_argcount]

                # Filter the dictionary to include only the matching parameters
                filtered_params = {k: v for k, v in extra_params_dict.items() if k in param_names}
                # Call the function with the filtered parameters
                args = [model, input_data.get("input")]
                if input_data.get("input2"):
                    args.append(input_data.get("input2"))
                return func(*args, **filtered_params)
            except Exception as e:
                # Add basic error handling
                error_msg = f"Error calling prediction function: {str(e)}"
                raise RuntimeError(error_msg) from e

        return wrapper

    def _register_endpoints(self):
        """Register the FastAPI endpoints"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy"}

        @self.app.post("/inference")
        async def serve_inference(
            input: Optional[UploadFile] = File(None),
            input2: Optional[UploadFile] = File(None),
            input_url: Optional[str] = Form(None),
            inputUrl: Optional[str] = Form(None),
            extra_params: Optional[str] = Form(None),
        ):
            """
            Run inference on the provided input
            
            Args:
                input: Primary input file
                input2: Secondary input file (optional)
                input_url: URL to fetch input from
                inputUrl: Alternative URL parameter (for backward compatibility)
                extra_params: Additional parameters as JSON string
                
            Returns:
                Prediction results
            """
            try:
                # Use inputUrl as fallback if input_url is not provided
                effective_input_url = input_url if input_url else inputUrl
                
                input_data: Dict[str, Any] = {}
                input_data["input"] = await input.read() if input else None
                input_data["input2"] = await input2.read() if input2 else None
                input_data["input_url"] = effective_input_url
                
                # Parse extra parameters
                if extra_params:
                    try:
                        extra_params_dict = json.loads(extra_params)
                        input_data["extra_params"] = extra_params_dict
                    except json.JSONDecodeError as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid extra_params JSON: {str(e)}",
                        )
                else:
                    input_data["extra_params"] = {}

                # Fetch input from URL if provided
                if effective_input_url:
                    try:
                        logging.info(f"Fetching input from URL: {effective_input_url}")
                        response = requests.get(effective_input_url, timeout=10)
                        response.raise_for_status()
                        input_data["input"] = response.content
                    except requests.exceptions.RequestException as e:
                        logging.error(
                            f"Failed to fetch input from URL: {str(e)}", exc_info=True
                        )
                        raise HTTPException(
                            status_code=400, detail=f"Failed to fetch input: {str(e)}"
                        )
                
                # Validate input
                if not input_data["input"]:
                    raise HTTPException(status_code=400, detail="No input provided")

                # Run inference
                results, ok = self.inference(input_data)
                if ok:
                    logging.info("Inference completed successfully")
                    return JSONResponse(
                        content=jsonable_encoder(
                            {
                                "status": 1,
                                "message": "Request success",
                                "result": results,
                            }
                        )
                    )
                else:
                    logging.error("Model inference failed")
                    raise HTTPException(status_code=500, detail="Inference failed")
            except Exception as e:
                logging.error(f"Error in inference endpoint: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))

    def inference(self, input_data: dict):
        """Run inference on the provided input data"""
        try:
            if input_data is None:
                raise ValueError("Input data cannot be None")

            logging.info("Starting inference")
            results = self.predict(self.model, input_data)
            results = self.actionTracker.update_prediction_results(results)
            logging.info("Inference completed successfully")
            return results, True
        except Exception as e:
            logging.error(f"Inference error: {str(e)}", exc_info=True)
            return None, False

    def setup(self, instance_port):
        """Start the FastAPI server"""
        try:
            if not isinstance(instance_port, int) or instance_port < 0:
                raise ValueError("Invalid port number")

            logging.info(f"Starting FastAPI server on port {instance_port}")
            server = uvicorn.Server(
                uvicorn.Config(
                    app=self.app,
                    host="0.0.0.0",
                    port=80,  # it must be 80 as it is the port mapped to the external instance port
                    log_level="info",
                )
            )
            thread = threading.Thread(target=server.run, daemon=True)
            thread.start()
            logging.info(f"FastAPI server started successfully on port {instance_port}")
            return server
        except Exception as e:
            logging.error(f"Failed to start server: {str(e)}", exc_info=True)
            raise
