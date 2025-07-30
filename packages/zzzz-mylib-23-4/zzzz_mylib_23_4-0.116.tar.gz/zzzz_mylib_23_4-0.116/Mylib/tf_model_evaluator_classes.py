import numpy as np
from Mylib import tf_myfuncs, myfuncs, tf_myclasses
from sklearn import metrics


class ClassifierEvaluator:
    """Đánh giá classifier trong Deep learning model

    Args:
        model (_type_): _description_
        class_names (_type_): _description_
        train_ds (_type_): _description_
        val_ds (_type_, optional): Nếu không có, tức là chỉ đánh giá trên 1 tập thôi (đánh giá cho tập test). Defaults to None.
    """

    def __init__(self, model, class_names, train_ds, val_ds=None):
        self.model = model
        self.class_names = class_names
        self.train_ds = train_ds
        self.val_ds = val_ds

    def evaluate_train_classifier(self):
        train_target_data, train_pred = (
            tf_myfuncs.get_full_target_and_pred_for_softmax_DLmodel(
                self.model, self.train_ds
            )
        )
        train_pred = [int(item) for item in train_pred]
        train_target_data = [int(item) for item in train_target_data]

        val_target_data, val_pred = (
            tf_myfuncs.get_full_target_and_pred_for_softmax_DLmodel(
                self.model, self.val_ds
            )
        )
        val_pred = [int(item) for item in val_pred]
        val_target_data = [int(item) for item in val_target_data]

        # Accuracy
        train_accuracy = metrics.accuracy_score(train_target_data, train_pred)
        val_accuracy = metrics.accuracy_score(val_target_data, val_pred)

        # Classification report
        class_names = np.asarray(self.class_names)
        named_train_target_data = class_names[train_target_data]
        named_train_pred = class_names[train_pred]
        named_val_target_data = class_names[val_target_data]
        named_val_pred = class_names[val_pred]

        train_classification_report = metrics.classification_report(
            named_train_target_data, named_train_pred
        )
        val_classification_report = metrics.classification_report(
            named_val_target_data, named_val_pred
        )

        # Confusion matrix
        train_confusion_matrix = metrics.confusion_matrix(
            named_train_target_data, named_train_pred, labels=class_names
        )
        np.fill_diagonal(train_confusion_matrix, 0)
        train_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            train_confusion_matrix, class_names
        )

        val_confusion_matrix = metrics.confusion_matrix(
            named_val_target_data, named_val_pred, labels=class_names
        )
        np.fill_diagonal(val_confusion_matrix, 0)
        val_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            val_confusion_matrix, class_names
        )

        model_results_text = f"Train accuracy: {train_accuracy}\n"
        model_results_text += f"Val accuracy: {val_accuracy}\n"
        model_results_text += (
            f"Train classification_report: \n{train_classification_report}\n"
        )
        model_results_text += (
            f"Val classification_report: \n{val_classification_report}"
        )

        return model_results_text, train_confusion_matrix, val_confusion_matrix

    def evaluate_test_classifier(self):
        test_target_data, test_pred = (
            tf_myfuncs.get_full_target_and_pred_for_softmax_DLmodel(
                self.model, self.train_ds
            )
        )
        test_pred = [int(item) for item in test_pred]
        test_target_data = [int(item) for item in test_target_data]

        # Accuracy
        test_accuracy = metrics.accuracy_score(test_target_data, test_pred)

        # Classification report
        class_names = np.asarray(self.class_names)
        named_test_target_data = class_names[test_target_data]
        named_test_pred = class_names[test_pred]

        test_classification_report = metrics.classification_report(
            named_test_target_data, named_test_pred
        )

        # Confusion matrix
        test_confusion_matrix = metrics.confusion_matrix(
            named_test_target_data, named_test_pred, labels=class_names
        )
        np.fill_diagonal(test_confusion_matrix, 0)
        test_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            test_confusion_matrix, class_names
        )

        model_results_text = f"Test accuracy: {test_accuracy}\n"
        model_results_text += (
            f"Test classification_report: \n{test_classification_report}\n"
        )

        return model_results_text, test_confusion_matrix

    def evaluate(self):
        return (
            self.evaluate_train_classifier()
            if self.val_ds is not None
            else self.evaluate_test_classifier()
        )


class RegressorEvaluator:
    def __init__(self, model, train_ds, val_ds=None):
        self.model = model
        self.train_ds = train_ds
        self.val_ds = val_ds

    def evaluate_train_classifier(self):
        train_target_data, train_pred = (
            tf_myfuncs.get_full_target_and_pred_for_regression_DLmodel(
                self.model, self.train_ds
            )
        )
        val_target_data, val_pred = (
            tf_myfuncs.get_full_target_and_pred_for_regression_DLmodel(
                self.model, self.val_ds
            )
        )

        # RMSE
        train_rmse = np.sqrt(metrics.mean_squared_error(train_target_data, train_pred))
        val_rmse = np.sqrt(metrics.mean_squared_error(val_target_data, val_pred))

        # MAE
        train_mae = metrics.mean_absolute_error(train_target_data, train_pred)
        val_mae = metrics.mean_absolute_error(val_target_data, val_pred)

        model_result_text = f"Train RMSE: {train_rmse}\n"
        model_result_text += f"Val RMSE: {val_rmse}\n"
        model_result_text += f"Train MAE: {train_mae}\n"
        model_result_text += f"Val MAE: {val_mae}"

        return model_result_text

    def evaluate_test_classifier(self):
        test_target_data, test_pred = (
            tf_myfuncs.get_full_target_and_pred_for_regression_DLmodel(
                self.model, self.train_ds
            )
        )

        # RMSE
        test_rmse = np.sqrt(metrics.mean_squared_error(test_target_data, test_pred))

        # MAE
        test_mae = metrics.mean_absolute_error(test_target_data, test_pred)

        model_result_text = f"Test RMSE: {test_rmse}\n"
        model_result_text += f"Test MAE: {test_mae}\n"

        return model_result_text


class MachineTranslationEvaluator:
    """Dùng để đánh giá tổng quát bài toán Dịch Máy <br>
    Đánh giá chỉ số BLEU

    Args:
        model (_type_): _description_
        train_ds (_type_): _description_
        val_ds (_type_, optional): Nếu None thì chỉ đánh giá trên 1 tập thôi (tập test). Defaults to None.
    """

    def __init__(self, model, train_ds, val_ds=None):
        self.model = model
        self.train_ds = train_ds
        self.val_ds = val_ds

    def evaluate_train_classifier(self):
        # Get thực tế và dự đoán
        train_target, train_pred = (
            tf_myfuncs.get_full_target_and_pred_for_softmax_DLmodel(
                self.model, self.train_ds
            )
        )
        val_target, val_pred = tf_myfuncs.get_full_target_and_pred_for_softmax_DLmodel(
            self.model, self.val_ds
        )

        # Đánh giá: bleu + ...
        train_bleu = np.mean(
            tf_myclasses.ListBleuGetter(train_target, train_pred).next()
        )
        val_bleu = np.mean(tf_myclasses.ListBleuGetter(val_target, val_pred).next())

        result = f"Train BLEU: {train_bleu}\n"
        result += f"Val BLEU: {val_bleu}\n"

        return result

    def evaluate_test_classifier(self):
        # Get thực tế và dự đoán
        test_target, test_pred = (
            tf_myfuncs.get_full_target_and_pred_for_softmax_DLmodel(
                self.model, self.train_ds
            )
        )

        # Đánh giá: bleu + ...
        test_bleu = np.mean(tf_myclasses.ListBleuGetter(test_target, test_pred).next())

        result = f"Test BLEU: {test_bleu}\n"

        return result

    def evaluate(self):
        return (
            self.evaluate_train_classifier()
            if self.val_ds is not None
            else self.evaluate_test_classifier()
        )
