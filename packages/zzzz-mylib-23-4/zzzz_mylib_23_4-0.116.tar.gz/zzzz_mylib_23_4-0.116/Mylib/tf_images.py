from tensorflow import keras
import tensorflow as tf
import numpy as np
import matplotlib.cm as cm


class ImagesToArrayConverter:
    """Chuyển 1 tập ảnh  thành 1 mảng numpy

    Attributes:
        image_paths (list): Tập các đường dẫn đến các file ảnh
        target_size (int): Kích thước sau khi resize

    Hàm -> convert()

    Returns:
        result (np.ndarray):
    """

    def __init__(self, image_paths, target_size):
        self.image_paths = image_paths
        self.target_size = (target_size, target_size)

    def convert_1image(self, img_path):
        img = keras.utils.load_img(
            img_path, target_size=self.target_size
        )  # load ảnh và resize luôn
        array = keras.utils.img_to_array(img)  # Chuyển img sang array
        array = np.expand_dims(
            array, axis=0
        )  # Thêm chiều để tạo thành mảng có 1 phần tử
        return array

    def convert(self):
        return np.vstack(
            [self.convert_1image(img_path) for img_path in self.image_paths]
        )


class GradCAMForImages:
    """Thực hiện quá trình GradCAM để xác định những phần nảo của ảnh hỗ trợ model phân loại nhiều nhất
    Attributes:
        images (np.ndarray): Tập ảnh đã được chuyển thành **array**
        model (_type_): model
        last_convnet_layer_name ([str, int]): **Tên** hoặc  **index** của layer convent cuối cùng trong model

    Hàm -> **convert()**

    Returns:
        list_superimposed_img (list[PIL.Image.Image]): 1 mảng

    Examples:
        Nhấn mạnh những phần trên ảnh giúp phân loại các lá -> 3 loại: healthy, early_blight, late_blight
        ```python
        # Lấy đường dẫn của các ảnh
        img_paths = [os.path.join(folder, file) for file in file_names]

        # Chuyển các ảnh thành các mảng numpy
        file_names_array = myclasses.ImagesToArrayConverter(image_paths=img_paths, target_size=256).convert()

        # Load model
        model = load_model("artifacts/model_trainer/CONVNET_45/best_model.keras")
        last_convnet_index = int(3) # Specify lớp convnet cuối cùng (thông qua chỉ số), mà cũng nên dùng chỉ số đi :))))

        # Kết quả thu được là 1 mảng các PIL.Image.Image
        result = myclasses.GradCAMForImages(file_names_array, model, last_convnet_index).convert()

        # Show các ảnh lên
        for image in result:
            plt.imshow(image)
        ```
    """

    def __init__(self, images, model, last_convnet_layer_name):
        self.images = images
        self.model = model
        self.last_convnet_layer_name = last_convnet_layer_name

    def create_models(self):
        """Tạo ra 2 model sau:

        **last_conv_layer_model**: model map input image -> convnet block cuối cùng

        **classifier_model**: model map convnet block cuối cùng -> final class predictions.

        Returns:
            tuple: last_conv_layer_model, classifier_model
        """
        last_conv_layer = None
        classifier_layers = None
        if isinstance(self.last_convnet_layer_name, str):
            layer_names = [layer.name for layer in self.model.layers]
            last_conv_layer = self.model.get_layer(self.last_convnet_layer_name)
            classifier_layers = self.model.layers[
                layer_names.index(self.last_convnet_layer_name) + 1 :
            ]
        else:
            last_conv_layer = self.model.layers[self.last_convnet_layer_name]
            classifier_layers = self.model.layers[self.last_convnet_layer_name + 1 :]

        # Model đầu tiên
        last_conv_layer_model = keras.Model(
            inputs=self.model.inputs, outputs=last_conv_layer.output
        )

        classifier_input = keras.Input(shape=last_conv_layer.output.shape[1:])
        x = classifier_input

        for layer in classifier_layers:
            x = layer(x)

        # Model thứ hai
        classifier_model = keras.Model(inputs=classifier_input, outputs=x)

        return last_conv_layer_model, classifier_model

    def do_gradient(self, last_conv_layer_model, classifier_model):
        with tf.GradientTape() as tape:
            last_conv_layer_output = last_conv_layer_model(self.images)
            tape.watch(last_conv_layer_output)
            preds = classifier_model(last_conv_layer_output)
            top_pred_index = tf.argmax(preds[0])
            top_class_channel = preds[:, top_pred_index]

        grads = tape.gradient(top_class_channel, last_conv_layer_output)
        return grads, last_conv_layer_output

    def get_heatmap(self, grads, last_conv_layer_output):
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2)).numpy()
        last_conv_layer_output = last_conv_layer_output.numpy()[0]

        for i in range(pooled_grads.shape[-1]):
            last_conv_layer_output[:, :, i] *= pooled_grads[i]

        heatmap = np.mean(last_conv_layer_output, axis=-1)
        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap)

        return heatmap

    def convert_1image(self, img, heatmap):

        heatmap = np.uint8(255 * heatmap)

        jet = cm.get_cmap("jet")  # Dùng "jet" để tô màu lại heatmap
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]
        jet_heatmap = keras.utils.array_to_img(jet_heatmap)
        jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
        jet_heatmap = keras.utils.img_to_array(jet_heatmap)
        superimposed_img = jet_heatmap * 0.4 + img
        superimposed_img = keras.utils.array_to_img(superimposed_img)

        return superimposed_img

    def convert(self):
        last_conv_layer_model, classifier_model = self.create_models()
        grads, last_conv_layer_output = self.do_gradient(
            last_conv_layer_model, classifier_model
        )
        heatmap = self.get_heatmap(grads, last_conv_layer_output)

        list_superimposed_img = [
            self.convert_1image(img, heatmap) for img in self.images
        ]

        return list_superimposed_img
