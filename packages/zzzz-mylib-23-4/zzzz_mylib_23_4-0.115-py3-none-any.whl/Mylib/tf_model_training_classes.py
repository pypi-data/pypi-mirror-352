import os
from Mylib import myfuncs, tf_layers, tf_model_training_funcs, tf_metrics
import tensorflow as tf
from src.utils import classes
import numpy as np
import time
import gc
import itertools
import pandas as pd
from Mylib.tf_layer_lists import (
    DenseBatchNormalizationDropoutList,
    DenseBatchNormalizationList,
    Conv2DBlock_2Conv2DList,
    DenseBatchNormalizationDropoutList,
)
from Mylib.tf_layers import ImageDataPositionAugmentation
from tensorflow.keras.layers import Flatten, GlobalAveragePooling2D, LSTM, GRU
from sklearn.model_selection import ParameterSampler


class LayerCreator:
    """Create layer từ param và text đại diện cho layer đó <br>

    Examples:
    ```
    param = {
        'patience': 10,
        'min_delta': 0.001,
        'learning_rate': 0.01,
        'layer1__start_units': 8,
        'layer1__num_layers': 4,
        'layer1__name': 'DenseBatchNormalizationTuner',
        'layer0__start_units': 16,
        'layer0__num_layers': 5,
        'layer0__name': 'DenseBatchNormalizationDropoutTuner',
        'layer0__dropout_rate': 0.5,
        'epochs': 30
    }
    layer_text = 'layer0'

    ```
    Khi đó tạo layer từ các key có chứa 'layer0' là: start_units, num_layers, name, dropout_rate

    Args:
        param (_type_): dict
        layer_text (_type_): text thể hiện cho layer cần tạo
    """

    def __init__(self, param, layer_text):
        self.param = param
        self.layer_text = layer_text

    def next(self):
        # Kiểm tra có phải PassThroughLayer
        if self.is_PassThroughLayer():
            return tf_layers.PassThroughLayer()

        # Get param ứng với layer_text
        keys = pd.Series(self.param.keys())
        values = pd.Series(self.param.values())
        keys = keys[keys.str.startswith(self.layer_text)]
        values = values[keys.str.startswith(self.layer_text)]

        keys = keys.apply(self.get_param_name)
        layer_param = dict(zip(keys, values))

        # Tạo class
        class_name = layer_param.pop("name")
        ClassName = globals()[class_name]

        # Tạo object
        layer = ClassName(**layer_param)
        return layer

    def get_param_name(self, key):
        parts = key.split("__", 1)
        return parts[1]

    def is_PassThroughLayer(self):
        keys = pd.Series(self.param.keys())
        keys = keys[keys.str.startswith(self.layer_text)]
        return keys.iloc[0] == f"{self.layer_text}__none"


class ListParamCreator:
    def __init__(self, param_dict):
        """Tạo ra danh sách các tham số phục vụ cho model training, cấu trúc của param_dict phải là như sau: <br>
        ```
        param_dict = {
            "patience": [5, 10],
            "min_delta": [0.001],
            "epochs": [30, 50],
            "learning_rate": [0.001, 0.01],
            "layers": [
                {
                    "name": 'DenseBatchNormalizationDropoutTuner',
                    "dropout_rate": 0.5,
                    "start_units": 16,
                    "list_num_layers": [1,2,3,4,5],
                },
                {
                    "name": 'DenseBatchNormalizationTuner',
                    "start_units": 8,
                    "list_num_layers": [1,2,3,4,5],

                }
            ]
        }
        ```
        Khi đó tập trung xử lí key 'layers' để đưa **param_dict** về dạng dict như này: <br>
        ```
        param_dict_transformed = {
            'patience': [5, 10],
            'min_delta': [0.001],
            'epochs': [30, 50],
            'learning_rate': [0.001, 0.01],
            'layer0__name': ['DenseBatchNormalizationDropoutTuner'],
            'layer0__dropout_rate': [0.5],
            'layer0__start_units': [16],
            'layer0__num_layers': [1, 2, 3, 4, 5],
            'layer1__name': ['DenseBatchNormalizationTuner'],
            'layer1__start_units': [8],
            'layer1__num_layers': [1, 2, 3, 4, 5]
        }
        ```

        Args:
            param_dict (_type_): dict
        """
        self.param_dict = param_dict

    def next(self):
        # Loại bỏ key
        list_layers = self.param_dict.pop("layers")

        # Thêm tiền tố layer vào mỗi key trong list_layers
        list_layers = [
            self.add_layer_text_to_key(layer, i) for i, layer in enumerate(list_layers)
        ]

        # Tạo list_layers mới
        list_layers_keys = list(
            itertools.chain(*[list(item.keys()) for item in list_layers])
        )
        list_layers_values = list(
            itertools.chain(*[list(item.values()) for item in list_layers])
        )
        list_layers = dict(zip(list_layers_keys, list_layers_values))

        # Tổng hợp tạo ra param_dict
        param_dict_keys = list(self.param_dict.keys()) + list(list_layers.keys())
        param_dict_values = list(self.param_dict.values()) + list(list_layers.values())
        param_dict_values = [
            item if isinstance(item, list) else [item] for item in param_dict_values
        ]

        param_dict = dict(zip(param_dict_keys, param_dict_values))
        list_param = myfuncs.get_full_list_dict(param_dict)

        return list_param

    def add_layer_text_to_key(self, a, i):
        if not a:
            a[f"layer{i}__none"] = None
            return a

        a_keys = [f"layer{i}__{key}" for key in a.keys()]
        a = dict(zip(a_keys, a.values()))
        return a


class CustomisedModelCheckpoint(tf.keras.callbacks.Callback):
    """Customize từ ModelCheckpoint trong tf.keras.callbacks <br>
    Mục đích: Tìm model tốt nhất theo epoch, cập nhật model tốt nhất và lưu kết quả tương ứng trong quá trình train model <br>

    Attributes:
        model_training_result_path (_type_): kết quả train model tốt nhất theo epoch
        model_path (_type_): đường dẫn đến model tốt nhất trong quá trình train model
        result_path (_type_): kết quả tương ứng với model tốt nhất trong quá trình train model
        sign_for_val_scoring_find_best_model (_type_): dấu (-1 hoặc 1), hỗ trợ tìm model tốt nhất theo epoch và tìm model tốt nhất trong quá trình train model
        Lí do: với các chỉ số ưu tiên nhỏ nhất (mse, mae, ...) thì nhân với -1 để chuyển về logic tìm lớn nhất giống như các chỉ số ưu tiên lớn nhất (accuracy, roc_auc, ...) <br>
        model_saving_val_scoring_limit (_type_): mức tối thiểu của val scoring để lưu model
        best_val_scoring (_type_): chỉ số val scoring tốt nhất hiện tại
        scoring (_type_): chỉ số, vd: mse, mae, ....
        param (_type_): tham số của model
    """

    def __init__(
        self,
        model_training_result_path,
        model_path,
        result_path,
        sign_for_val_scoring_find_best_model,
        model_saving_val_scoring_limit,
        best_val_scoring_path,
        scoring,
        param,
    ):
        super().__init__()
        self.model_training_result_path = model_training_result_path
        self.model_path = model_path
        self.result_path = result_path
        self.sign_for_val_scoring_find_best_model = sign_for_val_scoring_find_best_model
        self.model_saving_val_scoring_limit = model_saving_val_scoring_limit
        self.best_val_scoring_path = best_val_scoring_path
        self.scoring = scoring
        self.param = param

    def on_train_begin(self, logs=None):
        self.start_time = time.time()
        self.train_scorings = []
        self.val_scorings = []
        self.model_weights = []

    def on_epoch_end(self, epoch, logs=None):
        self.train_scorings.append(
            logs.get(self.scoring) * self.sign_for_val_scoring_find_best_model
        )
        self.val_scorings.append(
            logs.get(f"val_{self.scoring}") * self.sign_for_val_scoring_find_best_model
        )
        self.model_weights.append(self.model.get_weights())

    def on_train_end(self, logs=None):
        # Thời gian training model
        training_time = time.time() - self.start_time

        # Tìm model ứng với val scoring tốt nhất
        index_best_model = np.argmax(self.val_scorings)
        best_model_val_scoring = np.abs(self.val_scorings[index_best_model])
        best_model_train_scoring = np.abs(self.train_scorings[index_best_model])
        best_weights = self.model_weights[index_best_model]
        self.model.set_weights(best_weights)
        best_model_num_epochs_before_stopping = len(self.train_scorings)

        # Lưu lại kết quả
        myfuncs.save_python_object(
            self.model_training_result_path,
            (
                best_model_val_scoring,
                best_model_train_scoring,
                training_time,
                best_model_num_epochs_before_stopping,
            ),
        )

        # Lưu model nếu val scoring trong quá trình train model được cải thiện
        best_model_val_scoring_for_saving = (
            best_model_val_scoring * self.sign_for_val_scoring_find_best_model
        )
        best_val_scoring = myfuncs.load_python_object(self.best_val_scoring_path)

        if best_model_val_scoring_for_saving > best_val_scoring:
            best_val_scoring = best_model_val_scoring_for_saving
            myfuncs.save_python_object(self.best_val_scoring_path, best_val_scoring)

            # Lưu kết quả tương ứng
            myfuncs.save_python_object(
                self.result_path,
                (
                    self.param,
                    best_model_val_scoring,
                    best_model_train_scoring,
                    training_time,
                    best_model_num_epochs_before_stopping,
                ),
            )

            # Lưu  model
            if best_model_val_scoring_for_saving > self.model_saving_val_scoring_limit:
                self.model.save(self.model_path)


class ModelTrainer:
    BUILT_IN_METRICS = ["mse", "mae", "accuracy"]

    def __init__(
        self,
        model_training_path,
        param_dict,
        num_models,
        loss,
        train_ds,
        val_ds,
        scoring,
        model_saving_val_scoring_limit,
        create_model_function,
    ):
        self.model_training_path = model_training_path
        self.param_dict = param_dict
        self.num_models = num_models
        self.loss = loss
        self.train_ds = train_ds
        self.val_ds = val_ds
        self.scoring = scoring
        self.model_saving_val_scoring_limit = model_saving_val_scoring_limit
        self.create_model_function = create_model_function

    def save_param_dict(self):
        list_param_path = f"{self.model_training_path}/list_param.pkl"
        if os.path.exists(list_param_path):
            return

        list_param = ListParamCreator(self.param_dict).next()
        myfuncs.save_python_object(list_param_path, list_param)

    def train(self):
        log_message = ""

        # Get list_param
        list_param = self.get_list_param()

        # Get tên thư mục để lưu các kết quả
        model_training_folder_path = (
            f"{self.model_training_path}/{self.get_folder_name()}"
        )
        myfuncs.create_directories(model_training_folder_path)

        # Save best_val_scoring
        best_val_scoring = -np.inf
        best_val_scoring_path = f"{model_training_folder_path}/best_val_scoring.pkl"
        myfuncs.save_python_object(best_val_scoring, best_val_scoring_path)

        sign_for_val_scoring_find_best_model = (
            tf_model_training_funcs.get_sign_for_val_scoring_find_best_model(
                self.scoring
            )
        )
        model_saving_val_scoring_limit = (
            model_saving_val_scoring_limit * sign_for_val_scoring_find_best_model
        )

        for i, param in enumerate(list_param):
            try:
                # Tạo model, callbacks và epochs
                model_training_result_path = (
                    f"{model_training_folder_path}/model_training_result.pkl"
                )
                model_path = f"{model_training_folder_path}/model.keras"
                result_path = f"{model_training_folder_path}/result.pkl"
                model, callbacks, epochs = self.create_model_callbacks_epochs(
                    param,
                    model_training_result_path,
                    model_path,
                    result_path,
                    sign_for_val_scoring_find_best_model,
                    model_saving_val_scoring_limit,
                    best_val_scoring_path,
                )

                # Train model
                print(f"Train model {i} / {self.num_models}")
                history = model.fit(
                    self.train_ds,
                    epochs=epochs,
                    verbose=1,
                    validation_data=self.val_ds,
                    callbacks=callbacks,
                ).history
                (
                    val_scoring,
                    train_scoring,
                    training_time,
                    num_epochs_before_stopping,
                ) = myfuncs.load_python_object(model_training_result_path)

                # In kết quả
                training_result_text = f"{param}\n -> Val {self.scoring}: {val_scoring}, Train {self.scoring}: {train_scoring}, Time: {training_time} (s), Epochs: {num_epochs_before_stopping}\n"
                print(training_result_text)

                # Logging
                log_message += training_result_text

                # Xóa các file không cần thiết nữa
                os.remove(model_training_result_path)

                # Giải phóng bộ nhớ model
                del model
                gc.collect()
            except:
                # Nếu có exception thì bỏ qua vòng lặp đi
                continue

        # Xóa các file không cần thiết nữa
        os.remove(best_val_scoring_path)

        # In ra kết quả của model tốt nhất
        best_model_result = myfuncs.load_python_object(result_path)
        best_model_result_text = f"Model tốt nhất\n{best_model_result[0]}\n -> Val {self.scoring}: {best_model_result[1]}, Train {self.scoring}: {best_model_result[2]}, Time: {best_model_result[3]} (s)\n"

        print(best_model_result_text)

        # Logging
        log_message += best_model_result_text

        # Save list_param
        myfuncs.save_python_object(
            f"{model_training_folder_path}/list_param.pkl", list_param
        )

        return log_message

    def create_model_callbacks_epochs(
        self,
        param,
        model_training_result_path,
        model_path,
        result_path,
        sign_for_val_scoring_find_best_model,
        model_saving_val_scoring_limit,
        best_val_scoring_path,
    ):
        # Get epochs
        epochs = param["epochs"]

        # Get callbacks
        earlyStopping = tf.keras.callbacks.EarlyStopping(
            monitor=f"val_{self.scoring}",
            patience=param["patience"],
            min_delta=param["min_delta"],
            mode=self.get_mode_for_EarlyStopping(),
        )
        modelCheckpoint = CustomisedModelCheckpoint(
            model_training_result_path,
            model_path,
            result_path,
            sign_for_val_scoring_find_best_model,
            model_saving_val_scoring_limit,
            best_val_scoring_path,
            self.scoring,
            param,
        )
        callbacks = [earlyStopping, modelCheckpoint]

        # Create model
        model = self.create_model_function(param)

        # Create optimizer
        optimizer = tf.keras.optimizers.RMSprop(learning_rate=param["learning_rate"])

        # Compile model
        model.compile(optimizer=optimizer, loss=self.loss, metrics=self.get_metrics())

        return model, callbacks, epochs

    def get_mode_for_EarlyStopping(self):
        if self.scoring in tf_model_training_funcs.SCORINGS_PREFER_MAXIMUM:
            return "max"

        if self.scoring in tf_model_training_funcs.SCORINGS_PREFER_MININUM:
            return "min"

        raise ValueError(f"Chưa định nghĩa cho {self.scoring}")

    def get_metrics(self):
        if self.scoring in self.BUILT_IN_METRICS:
            return [self.scoring]

        if self.scoring == "bleu":
            return [tf_metrics.BleuScoreCustomMetric()]

        raise ValueError(f"Chưa định nghĩa cho {self.scoring}")

    def get_list_param(self):
        full_list_param = myfuncs.load_python_object(
            f"{self.model_training_path}/list_param.pkl"
        )

        # Get folder của run
        run_folders = pd.Series(os.listdir(self.model_training_path))
        run_folders = run_folders[run_folders.str.startswith("run")].tolist()

        if len(run_folders) > 0:
            # Get list param còn lại
            for run_folder in run_folders:
                list_param = myfuncs.load_python_object(
                    f"{self.model_training_path}/{run_folder}/list_param.pkl"
                )
                full_list_param = myfuncs.subtract_2list_set(
                    full_list_param, list_param
                )

        # Random list
        return myfuncs.randomize_list(full_list_param, self.num_models)

    def get_folder_name(self):
        # Get folder của run
        run_folders = pd.Series(os.listdir(self.model_training_path))
        run_folders = run_folders[run_folders.str.startswith("run")]

        if len(run_folders) == 0:
            return "run0"

        number_in_run_folders = run_folders.str.extract(r"(\d+)").astype("int")[0]
        folder_name = f"run{number_in_run_folders.max() +1}"
        return folder_name
