import numpy as np
from typing import Any, Dict, List


def model_fn(model_dir: str) -> Dict[str, Any]:
    """
    Load the model for inference
    """
    return {}


def predict_fn(input_data: List, model: Dict):
    """
    Apply model to the incoming request
    """
    return np.array([[1, 2, 3], [2, 3, 4]])


def input_fn(request_body: str, request_content_type: str) -> List[str]:
    """
    Deserialize and prepare the prediction input
    """
    return request_body

def output_fn(prediction, accept):  # pylint: disable=no-self-use
    return prediction.tolist()

def explain_fn(data, model, enable_explanations):
    return {"explanations": {"kernel_shap": [0.2, 0.3]}}