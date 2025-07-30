import numpy as np
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("numpy")

tensor_store = {}


# Tensor creation and deletion
@mcp.tool()
def create_matrix(shape: list[int], values: list[float], name: str) -> np.ndarray:
    """
    Creates a NumPy array (matrix) with a specified shape and values.

    Args:
        shape (list[int]): The shape of the resulting array as a tuple(e.g., (2, 3)).
        values (list[float]): A flat list of values to populate the array.
        name (str): The name of the tensor to be stored.

    Returns:
        np.ndarray: A NumPy array with the specified shape.

    Raises:
        ValueError: If the number of values does not match the product of the shape.
    """
    if len(values) != np.prod(shape):
        raise ValueError("Shape does not match number of values.")
    a = np.array(values).reshape(shape)

    tensor_store[name] = a
    return a


@mcp.tool()
def view_tensor(name: str) -> dict:
    """
    Returns an immutable view of a previously stored NumPy tensor from the in-memory tensor store.

    Args:
        name (str): The name of the tensor as stored in the in-store dictionary
    Returns:
        dict: The in-store dictionary for tensors

    """
    return tensor_store[name]


@mcp.tool()
def get_tensors() -> dict:
    """
    Returns the current state of the in-memory tensor store.

    Returns:
        dict: A dictionary containing all stored tensors with their names as keys and NumPy arrays as values.
    """
    return tensor_store


@mcp.tool()
def delete_tensor(name: str):
    """
    Deletes a tensor from the in-memory tensor store.

    Args:
        name (str): The name of the tensor to delete.

    Raises:
        ValueError: If the tensor name is not found in the store or if an error occurs during deletion.
    """

    if name not in tensor_store:
        raise ValueError("One or both tensor names not found in the store.")

    try:
        tensor_store.pop(name)
    except ValueError as e:
        raise ValueError(f"Error removing tensor:{e}")


# Matrix/tensor operations
@mcp.tool()
def add_tensors(name_a: str, name_b: str) -> np.ndarray:
    """
    Adds two stored tensors element-wise.

    Args:
        name_a (str): The name of the first tensor.
        name_b (str): The name of the second tensor.

    Returns:
        np.ndarray: The result of element-wise addition.

    Raises:
        ValueError: If the tensor names are not found or shapes are incompatible.
    """
    if name_a not in tensor_store or name_b not in tensor_store:
        raise ValueError("One or both tensor names not found in the store.")

    try:
        result = np.add(tensor_store[name_a], tensor_store[name_b])
    except ValueError as e:
        raise ValueError(f"Error adding tensors: {e}")

    return result


@mcp.tool()
def subtract_tensors(name_a: str, name_b: str) -> np.ndarray:
    """
    Adds two stored tensors element-wise.

    Args:
        name_a (str): The name of the first tensor.
        name_b (str): The name of the second tensor.

    Returns:
        np.ndarray: The result of element-wise subtraction.

    Raises:
        ValueError: If the tensor names are not found or shapes are incompatible.
    """
    if name_a not in tensor_store or name_b not in tensor_store:
        raise ValueError("One or both tensor names not found in the store.")

    try:
        result = np.subtract(tensor_store[name_a], tensor_store[name_b])
    except ValueError as e:
        raise ValueError(f"Error subtracting tensors: {e}")

    return result


@mcp.tool()
def scale_tensor(name: str, scale_factor: float, in_place: bool = True) -> np.ndarray:
    """
    Scales a stored tensor by a scalar factor.

    Args:
        name (str): The name of the tensor to scale.
        scale_factor (float): The scalar value to multiply the tensor by.
        in_place (bool): If True, updates the stored tensor; otherwise, returns a new scaled tensor.

    Returns:
        np.ndarray: The scaled tensor.

    Raises:
        ValueError: If the tensor name is not found in the store.
    """
    if name not in tensor_store:
        raise ValueError("The tensor name is not found in the store.")

    result = tensor_store[name] * scale_factor

    if in_place:
        tensor_store[name] = result

    return result


@mcp.tool()
def matrix_inverse(name: str) -> np.ndarray:
    """
    Computes the inverse of a stored square matrix.

    Args:
        name (str): The name of the tensor to invert.

    Returns:
        np.ndarray: The inverse of the matrix.

    Raises:
        ValueError: If the matrix is not found, is not square, or is singular (non-invertible).
    """
    if name not in tensor_store:
        raise ValueError("The tensor name is not found in the store.")

    try:
        result = np.linalg.inv(tensor_store[name])
    except ValueError as e:
        raise ValueError(f"Error computing matrix inverse: {e}")

    return result


@mcp.tool()
def transpose(name: str) -> np.ndarray:
    """
    Computes the transpose of a stored tensor.

    Args:
        name (str): The name of the tensor to transpose.

    Returns:
        np.ndarray: The transposed tensor.

    Raises:
        ValueError: If the tensor name is not found in the store.
    """
    if name not in tensor_store:
        raise ValueError("The tensor name is not found in the store.")

    return tensor_store[name].T


@mcp.tool()
def determinant(name: str) -> float:
    """
    Computes the determinant of a stored square matrix.

    Args:
        name (str): The name of the matrix.

    Returns:
        float: The determinant of the matrix.

    Raises:
        ValueError: If the matrix is not found or is not square.
    """
    if name not in tensor_store:
        raise ValueError("The tensor name is not found in the store.")

    try:
        result = np.linalg.det(tensor_store[name])
    except ValueError as e:
        raise ValueError(f"Error computing determinant: {e}")

    return result


@mcp.tool()
def rank(name: str) -> int | list[int]:
    """
    Computes the rank of a stored tensor.

    Args:
        name (str): The name of the tensor.

    Returns:
        int | list[int]: The rank of the matrix.

    Raises:
        ValueError: If the tensor name is not found in the store.
    """
    if name not in tensor_store:
        raise ValueError("The tensor name is not found in the store.")

    result = np.linalg.matrix_rank(tensor_store[name])
    return result

# @mcp.tool()
# def matrix_multiplication(name_1: str, name_2: str) -> np.ndarray:


@mcp.tool()
def eigen(name: str) -> dict:
    if name not in tensor_store:
        raise ValueError("The tensor name is not found in the store.")

    try:
        eigenvalues, eigenvectors = np.linalg.eig(tensor_store[name])
    except ValueError as e:
        raise ValueError(f"Error computing eigenvalues and eigenvectors: {e}")

    return {"eigenvalues": eigenvalues, "eigenvectors": eigenvectors}


if __name__ == '__main__':
    mcp.run(transport="sse")
