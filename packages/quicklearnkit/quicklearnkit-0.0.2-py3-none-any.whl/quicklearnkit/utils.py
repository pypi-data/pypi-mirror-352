import numpy as np

def create_random(mean, std, size, random_state=None):
    """
    Generate random data with a specified mean and standard deviation.

    Parameters:
        mean (float): Desired mean of the data.
        std (float): Desired standard deviation of the data.
        size (int): Length of the data to generate.
        random_state (int, optional): Seed for reproducibility. Defaults to None.

    Returns:
        dict: A dictionary containing:
            - "data": Random data with the specified mean and standard deviation.
            - "mean": Actual mean of the generated data.
            - "std": Actual standard deviation of the generated data.

    Raises:
        ValueError: If std is negative or size is not a positive integer.
    """
    if std < 0:
        raise ValueError("Standard deviation must be non-negative.")
    if size <= 0:
        raise ValueError("Size must be a positive integer.")

    # Create a random number generator instance
    rng = np.random.default_rng(random_state)
    
    # Generate random normal data
    x = rng.normal(size=size)
    x1 = (x - np.mean(x)) / np.std(x)
    x2 = (x1 * std) + mean

    return {
        "data": x2,
        "mean": np.mean(x2),
        "std": np.std(x2)
    }
