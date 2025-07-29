from Mylib import sk_fit_incremental_model, sk_model_training_funcs, myfuncs
import numpy as np
import time
import gc
import os
import pandas as pd
from datetime import datetime


class ModelTrainer:
    def __init__(
        self,
        model_training_path,
        num_models,
        base_model,
        param_dict,
        train_feature,
        train_target,
        val_feature,
        val_target,
        scoring,
        model_saving_val_scoring_limit,
    ):
        self.model_training_path = model_training_path
        self.num_models = num_models
        self.base_model = base_model
        self.param_dict = param_dict
        self.train_feature = train_feature
        self.train_target = train_target
        self.val_feature = val_feature
        self.val_target = val_target
        self.scoring = scoring
        self.model_saving_val_scoring_limit = model_saving_val_scoring_limit

    def save_param_dict(self):
        list_param_path = f"{self.model_training_path}/list_param.pkl"
        if os.path.exits(list_param_path):
            return

        list_param = myfuncs.get_full_list_dict(self.param_dict)
        myfuncs.save_python_object(list_param_path, list_param)

    def train(
        self,
    ):
        log_message = ""

        # Get list_param
        list_param = self.get_list_param()

        # Get tên thư mục để lưu các kết quả
        model_training_folder_path = (
            f"{self.model_training_path}/{self.get_folder_name()}"
        )
        myfuncs.create_directories(model_training_folder_path)

        best_val_scoring = -np.inf
        sign_for_val_scoring_find_best_model = (
            sk_model_training_funcs.get_sign_for_val_scoring_find_best_model(
                self.scoring
            )
        )
        model_saving_val_scoring_limit = (
            model_saving_val_scoring_limit * sign_for_val_scoring_find_best_model
        )

        for i, param in enumerate(list_param):
            try:
                # Tạo model
                model = self.create_model(param)

                # Train model
                print(f"Train model {i} / {self.num_models}")
                start_time = time.time()
                model.fit(self.train_feature, self.train_target)
                training_time = time.time() - start_time

                train_scoring = myfuncs.evaluate_model_on_one_scoring_17(
                    model,
                    self.train_feature,
                    self.train_target,
                    self.scoring,
                )
                val_scoring = myfuncs.evaluate_model_on_one_scoring_17(
                    model,
                    self.val_feature,
                    self.val_target,
                    self.scoring,
                )

                # In kết quả
                training_result_text = f"{param}\n -> Val {self.scoring}: {val_scoring}, Train {self.scoring}: {train_scoring}, Time: {training_time} (s)\n"
                print(training_result_text)

                # Logging
                log_message += training_result_text

                # Cập nhật best model và lưu lại
                val_scoring_find_best_model = (
                    val_scoring * sign_for_val_scoring_find_best_model
                )

                if best_val_scoring < val_scoring_find_best_model:
                    best_val_scoring = val_scoring_find_best_model

                    # Lưu model
                    if best_val_scoring > model_saving_val_scoring_limit:
                        myfuncs.save_python_object(
                            f"{model_training_folder_path}/model.pkl", model
                        )

                    # Lưu kết quả
                    myfuncs.save_python_object(
                        f"{model_training_folder_path}/result.pkl",
                        (param, val_scoring, train_scoring, training_time),
                    )

                # Giải phóng bộ nhớ
                del model
                gc.collect()
            except:
                continue

        # In ra kết quả của model tốt nhất
        best_model_result = myfuncs.load_python_object(
            f"{model_training_folder_path}/result.pkl"
        )
        best_model_result_text = f"Model tốt nhất\n{best_model_result[0]}\n -> Val {self.scoring}: {best_model_result[1]}, Train {self.scoring}: {best_model_result[2]}, Time: {best_model_result[3]} (s)\n"

        print(best_model_result_text)

        # Logging
        log_message += best_model_result_text

        # Lưu list_param
        myfuncs.save_python_object(
            f"{model_training_folder_path}/list_param.pkl", list_param
        )

        return log_message

    def create_model(self, param):
        ClassName = globals()[self.base_model]
        return ClassName(**param)

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


class ModelTrainerOnBatches:
    def __init__(
        self,
        training_batches_folder_path,
        model_training_path,
        num_models,
        base_model,
        param_dict,
        val_feature,
        val_target,
        scoring,
        model_saving_val_scoring_limit,
    ):

        self.training_batches_folder_path = training_batches_folder_path
        self.model_training_path = model_training_path
        self.num_models = num_models
        self.base_model = base_model
        self.param_dict = param_dict
        self.val_feature = val_feature
        self.val_target = val_target
        self.scoring = scoring
        self.model_saving_val_scoring_limit = model_saving_val_scoring_limit

    def train_models(
        self,
    ):
        log_message = ""
        list_param = myfuncs.randomize_dict(self.param_dict, self.num_models)
        best_val_scoring = -np.inf
        sign_for_val_scoring_find_best_model = (
            sk_model_training_funcs.get_sign_for_val_scoring_find_best_model(
                self.scoring
            )
        )
        model_saving_val_scoring_limit = (
            model_saving_val_scoring_limit * sign_for_val_scoring_find_best_model
        )

        # Get số lượng batch cần train
        num_batch = myfuncs.load_python_object(
            f"{self.training_batches_folder_path}/num_batch.pkl"
        )

        for i, param in enumerate(list_param):
            # Tạo model
            model = self.create_model(param)

            # Train model
            print(f"Train model {i} / {self.num_models}")
            start_time = time.time()
            train_scoring = self.train_on_batches(model, num_batch)
            training_time = time.time() - start_time

            val_scoring = myfuncs.evaluate_model_on_one_scoring_17(
                model,
                self.val_feature,
                self.val_target,
                self.scoring,
            )

            # In kết quả
            training_result_text = f"{param}\n -> Val {self.scoring}: {val_scoring}, Train {self.scoring}: {train_scoring}, Time: {training_time} (s)\n"
            print(training_result_text)

            # Logging
            log_message += training_result_text

            # Cập nhật best model và lưu lại
            val_scoring_find_best_model = (
                val_scoring * sign_for_val_scoring_find_best_model
            )

            if best_val_scoring < val_scoring_find_best_model:
                best_val_scoring = val_scoring_find_best_model

                # Lưu model
                if best_val_scoring > model_saving_val_scoring_limit:
                    myfuncs.save_python_object(
                        f"{self.model_training_path}/model.pkl", model
                    )

                # Lưu kết quả
                myfuncs.save_python_object(
                    f"{self.model_training_path}/result.pkl",
                    (param, val_scoring, train_scoring, training_time),
                )

            # Giải phóng bộ nhớ
            del model
            gc.collect()

        # In ra kết quả của model tốt nhất
        best_model_result = myfuncs.load_python_object(
            f"{self.model_training_path}/result.pkl"
        )
        best_model_result_text = f"Model tốt nhất\n{best_model_result[0]}\n -> Val {self.scoring}: {best_model_result[1]}, Train {self.scoring}: {best_model_result[2]}, Time: {best_model_result[3]} (s)\n"

        print(best_model_result_text)

        # Logging
        log_message += best_model_result_text

        return log_message

    def create_model(self, param):
        ClassName = globals()[self.base_model]
        return ClassName(**param)

    def train_on_batches(self, model, num_batch):
        list_train_scoring = (
            []
        )  # Cần biến này vì có thể sau này lấy min, max, ... tùy ý

        # Fit batch đầu tiên
        first_feature_batch = myfuncs.load_python_object(
            f"{self.training_batches_folder_path}/train_features_0.pkl"
        )
        first_target_batch = myfuncs.load_python_object(
            f"{self.training_batches_folder_path}/train_target_0.pkl"
        )

        # Lần đầu nên fit bình thường
        print("Train batch thứ 0")
        model.fit(first_feature_batch, first_target_batch)

        first_train_scoring = myfuncs.evaluate_model_on_one_scoring_17(
            model,
            first_feature_batch,
            first_target_batch,
            self.scoring,
        )

        list_train_scoring.append(first_train_scoring)

        # Fit batch thứ 1 trở đi
        for i in range(1, num_batch - 1 + 1):
            feature_batch = myfuncs.load_python_object(
                f"{self.training_batches_folder_path}/train_features_{i}.pkl"
            )
            target_batch = myfuncs.load_python_object(
                f"{self.training_batches_folder_path}/train_target_{i}.pkl"
            )

            # Lần thứ 1 trở đi thì fit theo kiểu incremental
            print(f"Train batch thứ {i}")
            sk_fit_incremental_model.fit_model_incremental_learning(
                model, feature_batch, target_batch
            )

            train_scoring = myfuncs.evaluate_model_on_one_scoring_17(
                model,
                feature_batch,
                target_batch,
                self.scoring,
            )

            list_train_scoring.append(train_scoring)

        return list_train_scoring[-1]  # Lấy kết quả trên batch cuối cùng


class ModelTrainingResultGatherer:
    MODEL_TRAINING_FOLDER_PATH = "artifacts/model_training"

    def __init__(self, scoring):
        self.scoring = scoring
        pass

    def next(self):
        model_training_paths = [
            f"{self.MODEL_TRAINING_FOLDER_PATH}/{item}"
            for item in os.listdir(self.MODEL_TRAINING_FOLDER_PATH)
        ]

        result = []
        for folder_path in model_training_paths:
            result += self.get_result_from_1folder(folder_path)

        # Sort theo val_scoring (ở vị trí thứ 1)
        result = sorted(
            result,
            key=lambda item: item[1],
            reverse=sk_model_training_funcs.get_reverse_param_in_sorted(self.scoring),
        )
        return result

    def get_result_from_1folder(self, folder_path):
        run_folder_names = pd.Series(os.listdir(folder_path))
        run_folder_names = run_folder_names[
            run_folder_names.str.startswith("run")
        ].tolist()
        run_folder_paths = [f"{folder_path}/{item}" for item in run_folder_names]

        list_result = []
        for folder_path in run_folder_paths:
            result = myfuncs.load_python_object(f"{folder_path}/result.pkl")
            list_result.append(result)

        return list_result


class LoggingDisplayer:
    DATE_FORMAT = "%d-%m-%Y-%H-%M-%S"
    READ_FOLDER_NAME = "artifacts/logs"
    WRITE_FOLDER_NAME = "artifacts/gather_logs"

    # Tạo thư mục
    os.makedirs(WRITE_FOLDER_NAME, exist_ok=True)

    def __init__(self, mode, file_name=None, start_time=None, end_time=None):
        self.mode = mode
        self.file_name = file_name
        self.start_time = start_time
        self.end_time = end_time

        if self.file_name is None:
            self.file_name = f"{datetime.now().strftime(self.DATE_FORMAT)}.log"

    def print_and_save(self):
        file_path = f"{self.WRITE_FOLDER_NAME}/{self.file_name}"

        if self.mode == "all":
            result = self.gather_all_logging_result()
        else:
            result = self.gather_logging_result_from_start_to_end_time()

        print(result)
        print(f"Lưu result tại {file_path}")
        myfuncs.write_content_to_file(result, file_path)

    def gather_all_logging_result(self):
        logs_filenames = self.get_logs_filenames()

        return self.read_from_logs_filenames(logs_filenames)

    def gather_logging_result_from_start_to_end_time(self):
        logs_filenames = pd.Series(self.get_logs_filenames())
        logs_filenames = logs_filenames[
            (logs_filenames > self.start_time) & (logs_filenames < self.end_time)
        ].tolist()

        return self.read_from_logs_filenames(logs_filenames)

    def read_from_logs_filenames(self, logs_filenames):
        result = ""
        for logs_filename in logs_filenames:
            logs_filepath = f"{self.READ_FOLDER_NAME}/{logs_filename}.log"
            content = myfuncs.read_content_from_file_60(logs_filepath)
            result += f"{content}\n\n"

        return result

    def get_logs_filenames(self):
        logs_filenames = os.listdir(self.READ_FOLDER_NAME)
        date_format_in_filename = f"{self.DATE_FORMAT}.log"
        logs_filenames = [
            datetime.strptime(item, date_format_in_filename) for item in logs_filenames
        ]
        logs_filenames = sorted(logs_filenames)  # Sắp xếp theo thời gian tăng dần
        return logs_filenames
