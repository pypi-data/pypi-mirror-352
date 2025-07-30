Benchmarks & Performance Evaluation
===================================

This document summarizes the empirical evaluation of the **Adaptive Momentum Gradient Descent (AMGD)** algorithm, comparing it with established optimization methods including **Adam**, **AdaGrad**, and **GLMNet**. The comparisons are based on experiments conducted on a large-scale ecological health dataset containing 61,345 observations and 17 features.

All benchmarks were evaluated using standard regression metrics:
    - Mean Absolute Error (MAE)
    - Root Mean Squared Error (RMSE)
    - Mean Poisson Deviance (MPD)
    - Sparsity (percentage of coefficients set to zero)

The results demonstrate that AMGD achieves superior performance across all metrics while maintaining meaningful sparsity through effective feature selection.

---

Key Benchmark Highlights
------------------------

- **56.6% reduction in MAE** compared to AdaGrad
- **2.7% improvement in MAE** over Adam
- Achieves **35.29% sparsity**, selecting only 11 out of 17 features
- Demonstrates **faster convergence**, reaching near-optimal loss values within 10% of maximum iterations
- Statistically significant improvements (**p < 0.0001**) with large effect sizes (**Cohen’s d up to 713**)

---

Benchmark Setup
---------------

**Algorithms Compared**
    - AMGD (this work)
    - Adam
    - AdaGrad
    - GLMNet

**Metrics Tracked**
    - Convergence speed
    - Prediction accuracy (MAE, RMSE, MPD)
    - Sparsity of solution
    - Feature selection stability

**Hardware & Dataset**
    - Dataset: Ecological health data (61,345 samples, 17 features)
    - Hardware: Intel i7 CPU, 32GB RAM
    - No GPU acceleration used

---

Convergence Behavior
--------------------

As shown in Figure 1 of the paper, AMGD exhibits rapid initial improvement and stable convergence:

.. code-block:: text

    | Optimizer | Iterations to Near-Optimal Loss | Final Loss Value |
    |-----------|-------------------------------|------------------|
    | AMGD      | ~10% of max iterations          | ~135,140         |
    | Adam      | ~25% of max iterations          | ~136,167         |
    | AdaGrad   | Very slow                       | ~300,000+        |
    | GLMNet    | Numerically unstable            | N/A              |

AMGD converges significantly faster than Adam and AdaGrad, and reaches better final loss values. GLMNet shows signs of numerical instability, especially with extreme predictor values.

---

Feature Selection Performance
-----------------------------

AMGD demonstrates superior feature selection capabilities by identifying relevant predictors and eliminating redundant ones effectively.

### Coefficient Stability Across Methods

The most important features selected by AMGD include:
- Pollution levels (low and moderate)
- Ecological health labels (ecologically degraded, healthy, and stable)

These features consistently showed high coefficient values (> 0.5) across bootstrap resamples, indicating robustness and interpretability.

#### Top Selected Features by AMGD

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Rank
     - Feature
   * - 1
     - Pollution_Level_Low
   * - 2
     - Pollution_Level_Moderate
   * - 3
     - Ecological_Health_Label_Ecologically Degraded
   * - 4
     - Ecological_Health_Label_Ecologically Healthy
   * - 5
     - Ecological_Health_Label_Ecologically Stable

AMGD selects these features with 100% consistency across resamples, confirming their importance.

---

Test Set Performance
--------------------

The following table summarizes test set performance across all algorithms:

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1

   * - Algorithm
     - MAE
     - RMSE
     - MPD
     - Sparsity (%)
   * - AMGD
     - 3.03
     - 3.91
     - 2.23
     - 35.29%
   * - Adam
     - 3.12
     - 4.03
     - 2.29
     - 11.76%
   * - AdaGrad
     - 6.74
     - 7.47
     - 10.50
     - 0.00%
   * - GLMNet
     - 9.00
     - 9.54
     - 29.39
     - 0.00%

AMGD outperforms all other methods in terms of prediction accuracy and achieves meaningful sparsity without sacrificing model quality.

---

Statistical Validation
----------------------

To validate the robustness of our findings, we conducted a **bootstrap analysis with 1000 resamples** and computed 95% confidence intervals and p-values.

### Bootstrap Results (95% CI)

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Metric
     - AMGD Confidence Interval
   * - MAE
     - [3.0131, 3.0183]
   * - RMSE
     - [3.8820, 3.8877]
   * - MPD
     - [2.1848, 2.1854]
   * - Sparsity
     - [0.3333]

Narrow confidence intervals confirm AMGD's consistent performance across resamples.

### Statistical Significance

All pairwise comparisons between AMGD and other algorithms yielded **p < 0.0001** with large effect sizes:

.. code-block:: text

    Cohen’s d:
    - vs Adam: -10.08 (MAE), -12.63 (RMSE), -9.46 (MPD)
    - vs AdaGrad: -16.94 (MAE), -18.19 (RMSE), -8.96 (MPD)
    - vs GLMNet: -713.03 (MAE), -688.00 (RMSE), -227.02 (MPD)

This confirms AMGD's statistically significant superiority across all metrics.

---

Conclusion
----------

AMGD demonstrates robust and consistent advantages over existing optimization methods for regularized Poisson regression:

- Achieves **superior prediction accuracy** (lowest MAE, RMSE, MPD)
- Maintains **meaningful sparsity** (35.29%) for improved interpretability
- Exhibits **faster convergence** and greater stability
- Selects features with **high consistency** across bootstrap resamples
- Shows **statistically significant improvements** with extremely large effect sizes

These results validate AMGD as a powerful tool for high-dimensional sparse modeling tasks, particularly where interpretability and feature selection are critical.
