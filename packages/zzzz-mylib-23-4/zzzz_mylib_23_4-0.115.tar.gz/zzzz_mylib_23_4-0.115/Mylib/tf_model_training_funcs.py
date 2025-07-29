import tensorflow as tf


SCORINGS_PREFER_MININUM = ["log_loss", "mse", "mae"]
SCORINGS_PREFER_MAXIMUM = ["accuracy", "bleu"]


def get_sign_for_val_scoring_find_best_model(scoring):
    if scoring in SCORINGS_PREFER_MININUM:
        return -1

    if scoring in SCORINGS_PREFER_MAXIMUM:
        return 1

    raise ValueError(f"Chưa định nghĩa cho {scoring}")


def get_output_layer_for_classification(num_classes=None):
    if len(num_classes) == 2:
        return tf.keras.layers.Dense(1, activation="sigmoid")

    # Phân loại nhiều class
    return tf.keras.layers.Dense(num_classes, activation="softmax")
