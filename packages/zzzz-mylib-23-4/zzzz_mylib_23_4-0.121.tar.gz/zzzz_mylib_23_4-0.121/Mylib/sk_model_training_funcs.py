SCORINGS_PREFER_MININUM = ["log_loss", "mse", "mae"]
SCORINGS_PREFER_MAXIMUM = ["accuracy", "roc_auc"]


def get_sign_for_val_scoring_find_best_model(scoring):
    if scoring in SCORINGS_PREFER_MININUM:
        return -1

    if scoring in SCORINGS_PREFER_MAXIMUM:
        return 1

    raise ValueError(f"Chưa định nghĩa cho {scoring}")


def get_reverse_param_in_sorted(scoring):
    if scoring in SCORINGS_PREFER_MAXIMUM:
        return True

    if scoring in SCORINGS_PREFER_MININUM:
        return False

    raise ValueError(f"Chưa định nghĩa cho {scoring}")
