import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2
import warnings

def compute_faas(wer_list, speaker_metadata):
    """
    Compute the FAAS (Fairness Adjusted ASR Score) using demographic disparities
    in WER predictions and likelihood ratio tests for fairness adjustment.
    """
    if not wer_list:
        raise ValueError("WER list cannot be empty")

    df = pd.DataFrame(speaker_metadata)
    df["WER"] = wer_list
    df["Reference_words"] = df.get("Reference_words", 10)  # Default if missing
    df["log_Ref_Words"] = np.log(df["Reference_words"] + 1)

    # Ensure grouping column exists and has multiple groups
    if "combined_column" not in df.columns:
        df["combined_column"] = df.index.astype(str)
    if df["combined_column"].nunique() < 2:
        raise ValueError("Grouping column 'combined_column' must have at least 2 unique groups.")

    # Prepare categories present in df and ensure they have >= 2 levels
    candidate_categories = ['gender', 'first_language', 'socioeconomic_bkgd', 'ethnicity']
    categories = []
    for cat in candidate_categories:
        if cat in df.columns:
            df[cat] = df[cat].astype('category')
            if len(df[cat].cat.categories) >= 2:
                categories.append(cat)
            else:
                warnings.warn(f"Category '{cat}' ignored: less than 2 levels.")

    # Base formula and mixed model fitting function with retries
    base_formula = "WER ~ log_Ref_Words"
    for cat in categories:
        base_formula += f" + C({cat})"

    def fit_mixedlm(formula):
        # Try multiple optimizers to avoid convergence issues
        for method in ['lbfgs', 'bfgs', 'cg', 'powell']:
            try:
                model = smf.mixedlm(formula, df, groups=df["combined_column"])
                result = model.fit(method=method, maxiter=1000, reml=False)
                if result.mle_retvals['converged']:
                    return result
            except Exception:
                continue
        raise RuntimeError("MixedLM failed to converge with all optimizers.")

    # Fit full model with all categories
    mixed_model = fit_mixedlm(base_formula)

    params = mixed_model.params
    fixed_log_ref = df["log_Ref_Words"].mean()
    baseline_log = params.get("Intercept", 0) + params.get("log_Ref_Words", 0) * fixed_log_ref
    exposure = np.exp(fixed_log_ref) - 1
    if exposure == 0:
        exposure = 1e-6  # avoid division by zero

    def compute_predicted_error_rate(category, level):
        coef_name = f"C({category})[T.{level}]"
        effect = params.get(coef_name, 0)
        pred_log = baseline_log + effect
        pred_count = np.exp(pred_log)
        return pred_count / exposure

    def compute_category_fairness(category):
        levels = df[category].cat.categories
        predictions = {lvl: compute_predicted_error_rate(category, lvl) for lvl in levels}
        pred_series = pd.Series(predictions)
        min_pred, max_pred = pred_series.min(), pred_series.max()

        if max_pred == min_pred:
            raw_fairness = pd.Series(100.0, index=pred_series.index)
        else:
            raw_fairness = 100 * (1 - (pred_series - min_pred) / (max_pred - min_pred))

        group_proportions = df[category].value_counts(normalize=True)
        group_proportions = group_proportions.reindex(raw_fairness.index, fill_value=0)
        weighted_category_fairness = np.average(raw_fairness, weights=group_proportions)
        return weighted_category_fairness

    # Fit reduced model once for likelihood ratio tests
    reduced_model = fit_mixedlm("WER ~ log_Ref_Words")

    def perform_lrt(attribute):
        # Fit full model with one category + log_Ref_Words
        formula = f"WER ~ log_Ref_Words + C({attribute})"
        full_mod = fit_mixedlm(formula)
        lr_stat = 2 * (full_mod.llf - reduced_model.llf)
        df_diff = full_mod.df_modelwc - reduced_model.df_modelwc
        p_value = chi2.sf(lr_stat, df_diff) if df_diff > 0 else 1.0
        return p_value

    adjusted_category_scores = []
    for cat in categories:
        raw_score = compute_category_fairness(cat)
        p_value = perform_lrt(cat)
        multiplier = (p_value / 0.05) if p_value < 0.05 else 1.0
        adjusted_score = raw_score * multiplier
        adjusted_category_scores.append(adjusted_score)

    overall_fairness_score = np.average(adjusted_category_scores) if adjusted_category_scores else 100.0
    avg_wer = np.mean(wer_list)
    if avg_wer == 0:
        avg_wer = 1e-6  # avoid log(0)

    faas = 10 * np.log10(overall_fairness_score / avg_wer)
    return faas
