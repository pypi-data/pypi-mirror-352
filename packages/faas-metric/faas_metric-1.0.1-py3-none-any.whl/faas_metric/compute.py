import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2

def compute_faas(wer_list, speaker_metadata):
    """
    Compute the FAAS (Fairness Adjusted ASR Score) using demographic disparities
    in WER predictions and likelihood ratio tests for fairness adjustment.
    """
    if not wer_list:
        raise ValueError("WER list cannot be empty")
    
    # Prepare the DataFrame
    df = pd.DataFrame(speaker_metadata)
    df["WER"] = wer_list
    df["Reference_words"] = df.get("Reference_words", 10)  # Default value if not present
    df["log_Ref_Words"] = np.log(df["Reference_words"] + 1)
    
    # Combine speaker/group identifier if not already present
    if "combined_column" not in df.columns:
        df["combined_column"] = df.index.astype(str)  # Dummy group ID for now

    # Ensure categorical data
    categories = ['gender', 'first_language', 'socioeconomic_bkgd', 'ethnicity']
    categories = [cat for cat in categories if cat in df.columns]
    for cat in categories:
        df[cat] = df[cat].astype('category')

    # Fit the mixed effects model
    formula = "WER ~ log_Ref_Words"
    for cat in categories:
        formula += f" + C({cat})"
    mixed_model = smf.mixedlm(formula, df, groups=df["combined_column"]).fit()

    # Compute baseline info
    params = mixed_model.params
    fixed_log_ref = df["log_Ref_Words"].mean()
    baseline_log = params["Intercept"] + params["log_Ref_Words"] * fixed_log_ref
    exposure = np.exp(fixed_log_ref) - 1

    def compute_predicted_error_rate(category, level):
        coef_name = f"C({category})[T.{level}]"
        effect = params.get(coef_name, 0)
        pred_log = baseline_log + effect
        pred_count = np.exp(pred_log)
        return pred_count / exposure

    def compute_category_fairness(category):
        levels = df[category].cat.categories
        predictions = {
            lvl: compute_predicted_error_rate(category, lvl)
            for lvl in levels
        }
        pred_series = pd.Series(predictions)
        min_pred, max_pred = pred_series.min(), pred_series.max()

        if max_pred == min_pred:
            raw_fairness = pred_series.apply(lambda x: 100.0)
        else:
            raw_fairness = pred_series.apply(lambda x: 100 * (1 - (x - min_pred) / (max_pred - min_pred)))

        group_proportions = df[category].value_counts(normalize=True)
        group_proportions = group_proportions.reindex(raw_fairness.index, fill_value=0)
        weighted_category_fairness = np.average(raw_fairness, weights=group_proportions)
        return weighted_category_fairness

    def perform_lrt(attribute):
        full_model = smf.mixedlm(f"WER ~ C({attribute}) + log_Ref_Words", df, groups=df["combined_column"]).fit()
        reduced_model = smf.mixedlm("WER ~ log_Ref_Words", df, groups=df["combined_column"]).fit()
        lr_stat = 2 * (full_model.llf - reduced_model.llf)
        df_diff = full_model.df_modelwc - reduced_model.df_modelwc
        p_value = chi2.sf(lr_stat, df_diff)
        return p_value

    adjusted_category_scores = []
    for cat in categories:
        raw_score = compute_category_fairness(cat)
        p_value = perform_lrt(cat)
        multiplier = (p_value / 0.05) if p_value < 0.05 else 1.0
        adjusted_score = raw_score * multiplier
        adjusted_category_scores.append(adjusted_score)

    overall_fairness_score = np.average(adjusted_category_scores)
    avg_wer = np.mean(wer_list)

    # Final FAAS metric
    faas = 10 * np.log10(overall_fairness_score / avg_wer)
    return faas

