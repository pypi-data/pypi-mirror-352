from matrice.utils import dependencies_check
dependencies_check(["torch", "fastapi", "uvicorn"])

from matrice.deploy.predictor.triton_predictor import MatriceTritonPredictor  # noqa: E402
from matrice.deploy.predictor.fastapi_predictor import MatriceFastAPIPredictor  # noqa: E402

__all__ = ["MatriceTritonPredictor", "MatriceFastAPIPredictor"]
