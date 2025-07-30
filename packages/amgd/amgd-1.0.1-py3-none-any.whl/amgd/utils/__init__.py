"""Utility functions for AMGD package."""

from amgd.utils.validation import (
    check_array, 
    check_consistent_length,
    check_is_fitted,
    validate_penalty_params
)
from amgd.utils.preprocessing import StandardScaler, add_intercept
from amgd.utils.metrics import (
    poisson_deviance,
    mean_absolute_error,
    mean_squared_error,
    evaluate_model
)

__all__ = [
    "check_array",
    "check_consistent_length",
    "check_is_fitted",
    "validate_penalty_params",
    "StandardScaler",
    "add_intercept",
    "poisson_deviance",
    "mean_absolute_error", 
    "mean_squared_error",
    "evaluate_model",
]