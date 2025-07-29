from .factory import register, create, unregister, get_names
from .fit_param_conversion import get_mu_sigma, get_mu_sigma_std
from .gaussian_fit_1d import fit_gaussian_1d, GaussianProfile1D
from .gaussian_linear_least_squares import (
    GaussianLinearLeastSquares,
    x_to_h as gaussian_lls_trans,
    x_to_h_grad as gaussian_lls_trans_grad,
)
from .plotting_and_output import (
    pretty_print_loc_and_size,
    plot_threshold,
    plot_residuals,
    plot_beam_contours,
)
from .supergaussian import fit_supergaussian, SuperGaussian
from .utils import (
    get_image_and_weight,
    get_config_dict_analysis_method,
    create_analysis_method_from_dict,
    super_gaussian_scaling_factor,
    super_gaussian_scaling_factor_grad,
    SuperGaussianResult,
)
from .sigma_transformations import (
    Cholesky,
    LogCholesky,
    Spherical,
    MatrixLogarithm,
    Givens,
    eigen2d_grad,
    eigen2d,
)
from .rms_integration import RMSIntegration
from .supergaussian_c_drivers import supergaussian, supergaussian_grad
from .debug import AnalysisMethodDebugger

# Register all analysis methods to the factory
for o in [GaussianProfile1D, GaussianLinearLeastSquares, SuperGaussian, RMSIntegration]:
    register("analysis", o.__name__, o)

for o in [
    Cholesky,
    LogCholesky,
    Spherical,
    MatrixLogarithm,
    Givens,
]:  # Register the sigma parameterizations
    register("sig_param", o.__name__, o)


def get_analysis_names():
    return get_names("analysis")


def create_analysis(name, **kwargs):
    return create("analysis", name, **kwargs)


__all__ = [
    # Factory functions
    "register",
    "create",
    "unregister",
    "get_names",
    "get_mu_sigma",
    "get_mu_sigma_std",
    "fit_gaussian_1d",
    "GaussianProfile1D",
    "GaussianLinearLeastSquares",
    "gaussian_lls_trans",
    "gaussian_lls_trans_grad",
    "pretty_print_loc_and_size",
    "plot_threshold",
    "plot_residuals",
    "plot_beam_contours",
    "fit_supergaussian",
    "SuperGaussian",
    "get_image_and_weight",
    "get_config_dict_analysis_method",
    "create_analysis_method_from_dict",
    "super_gaussian_scaling_factor",
    "super_gaussian_scaling_factor_grad",
    "SuperGaussianResult",
    "Cholesky",
    "LogCholesky",
    "Spherical",
    "MatrixLogarithm",
    "Givens",
    "eigen2d_grad",
    "eigen2d",
    "RMSIntegration",
    "supergaussian",
    "supergaussian_grad",
    "AnalysisMethodDebugger",
    "get_analysis_names",
    "create_analysis",
]
