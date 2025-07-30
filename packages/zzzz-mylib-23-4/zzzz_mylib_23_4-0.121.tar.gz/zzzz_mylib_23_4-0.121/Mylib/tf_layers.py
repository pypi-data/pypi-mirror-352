from tensorflow.keras import layers
from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.layers import LSTM, GRU


class SeparableConv2DBlock_Advanced(layers.Layer):
    """Gồm các layers sau:
    - SeparableConv2D
    - SeparableConv2D
    - MaxPooling2D

    Đi kèm là sự kết hợp giữa residual connections, batch normalization và  depthwise separable convolutions (lớp SeparableConv2D)

    Attributes:
        filters (_type_): số lượng filters trong lớp SeparableConv2D
    """

    def __init__(self, filters, name=None, **kwargs):
        # super(ConvNetBlock_XceptionVersion, self).__init__()
        super().__init__(name=name, **kwargs)
        self.filters = filters

    def build(self, input_shape):
        self.BatchNormalization = layers.BatchNormalization()
        self.Activation = layers.Activation("relu")
        self.SeparableConv2D = layers.SeparableConv2D(
            self.filters, 3, padding="same", use_bias=False
        )

        self.BatchNormalization_1 = layers.BatchNormalization()
        self.Activation_1 = layers.Activation("relu")
        self.SeparableConv2D_1 = layers.SeparableConv2D(
            self.filters, 3, padding="same", use_bias=False
        )
        self.MaxPooling2D = layers.MaxPooling2D(3, strides=2, padding="same")

        self.Conv2D = layers.Conv2D(
            self.filters, 1, strides=2, padding="same", use_bias=False
        )

        super().build(input_shape)

    def call(self, x):
        residual = x

        # First part of the block
        x = self.BatchNormalization(x)
        x = self.Activation(x)
        x = self.SeparableConv2D(x)

        # Second part of the block
        x = self.BatchNormalization_1(x)
        x = self.Activation_1(x)
        x = self.SeparableConv2D_1(x)
        x = self.MaxPooling2D(x)

        # Apply residual connection
        residual = self.Conv2D(residual)
        x = layers.add([x, residual])

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update({"filters": self.filters})
        return config

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        name = config.pop("name", None)
        return cls(**config)


class Conv2DBlock_Advanced(layers.Layer):
    """Gồm các layers sau:
    - Conv2D
    - Conv2D
    - MaxPooling2D

    Đi kèm là sự kết hợp giữa residual connections, batch normalization

    Attributes:
        filters (_type_): số lượng filters trong lớp Conv2D
    """

    def __init__(self, filters, **kwargs):
        super().__init__(**kwargs)
        self.filters = filters

    def build(self, input_shape):
        self.BatchNormalization = layers.BatchNormalization()
        self.Activation = layers.Activation("relu")
        self.Conv2D = layers.Conv2D(self.filters, 3, padding="same")

        self.BatchNormalization_1 = layers.BatchNormalization()
        self.Activation_1 = layers.Activation("relu")
        self.Conv2D_1 = layers.Conv2D(self.filters, 3, padding="same")
        self.MaxPooling2D = layers.MaxPooling2D(2, padding="same")

        self.Conv2D_2 = layers.Conv2D(self.filters, 1, strides=2)

        super().build(input_shape)

    def call(self, x):
        residual = x

        # First part of the block
        x = self.BatchNormalization(x)
        x = self.Activation(x)
        x = self.Conv2D(x)

        # Second part of the block
        x = self.BatchNormalization_1(x)
        x = self.Activation_1(x)
        x = self.Conv2D_1(x)
        x = self.MaxPooling2D(x)

        # Xử lí residual
        residual = self.Conv2D_2(residual)

        # Apply residual connection
        x = layers.add([x, residual])

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "filters": self.filters,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class Conv2DBlock_1Conv2D(layers.Layer):
    """Kết hợp các layers sau:
    - Conv2D
    - MaxPooling

    Đi kèm là BatchNormalization

    Attributes:
        filters (_type_): số lượng filters trong lớp Conv2D
    """

    def __init__(self, filters, name=None, **kwargs):
        """ """
        # super(ConvNetBlock, self).__init__()
        super().__init__(name=name, **kwargs)
        self.filters = filters

    def build(self, input_shape):
        self.BatchNormalization = layers.BatchNormalization()
        self.Activation = layers.Activation("relu")
        self.Conv2D = layers.Conv2D(self.filters, 3)
        self.MaxPooling2D = layers.MaxPooling2D(pool_size=2)

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        x = self.BatchNormalization(x)
        x = self.Activation(x)
        x = self.Conv2D(x)
        x = self.MaxPooling2D(x)

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "filters": self.filters,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


class Conv2DBlock_2Conv2D(layers.Layer):
    """Kết hợp các layers sau:
    - Conv2D
    - Conv2D
    - MaxPooling

    Đi kèm là BatchNormalization

    Attributes:
        filters (_type_): số lượng filters trong lớp Conv2D
    """

    def __init__(self, filters, name=None, **kwargs):
        """ """
        # super(ConvNetBlock, self).__init__()
        super().__init__(name=name, **kwargs)
        self.filters = filters

    def build(self, input_shape):
        self.BatchNormalization = layers.BatchNormalization()
        self.Activation = layers.Activation("relu")
        self.Conv2D = layers.Conv2D(self.filters, 3)

        self.BatchNormalization_1 = layers.BatchNormalization()
        self.Activation_1 = layers.Activation("relu")
        self.Conv2D_1 = layers.Conv2D(self.filters, 3)

        self.MaxPooling2D = layers.MaxPooling2D(pool_size=2)

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        x = self.BatchNormalization(x)
        x = self.Activation(x)
        x = self.Conv2D(x)

        x = self.BatchNormalization_1(x)
        x = self.Activation_1(x)
        x = self.Conv2D_1(x)
        x = self.MaxPooling2D(x)

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "filters": self.filters,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


class Conv2DBlock_1Conv2D_NoMaxPooling(layers.Layer):
    """Kết hợp các layers sau:
    - Conv2D

    Đi kèm là BatchNormalization

    Attributes:
        filters (_type_): số lượng filters trong lớp Conv2D
    """

    def __init__(self, filters, name=None, **kwargs):
        # super(ConvNetBlock, self).__init__()
        super().__init__(name=name, **kwargs)
        self.filters = filters

    def build(self, input_shape):
        self.BatchNormalization = layers.BatchNormalization()
        self.Activation = layers.Activation("relu")
        self.Conv2D = layers.Conv2D(self.filters, 3)

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        x = self.BatchNormalization(x)
        x = self.Activation(x)
        x = self.Conv2D(x)

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "filters": self.filters,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


class ImageDataPositionAugmentation(layers.Layer):
    """Tăng cường dữ liệu hình ảnh ở khía cạnh vị trí, bao gồm các lớp sau (**trong tf.keras.layers**)
    - RandomFlip
    - RandomRotation
    - RandomZoom

    Attributes:
        rotation_factor (float): Tham số cho lớp RandomRotation. Default to 0.2
        zoom_factor (float): Tham số cho lớp RandomZoom. Default to 0.2
    """

    def __init__(self, rotation_factor=0.2, zoom_factor=0.2, **kwargs):
        # super(ImageDataPositionAugmentation, self).__init__()
        super().__init__(**kwargs)
        self.rotation_factor = rotation_factor
        self.zoom_factor = zoom_factor

    def build(self, input_shape):
        self.RandomFlip = layers.RandomFlip(mode="horizontal_and_vertical")
        self.RandomRotation = layers.RandomRotation(factor=self.rotation_factor)
        self.RandomZoom = layers.RandomZoom(height_factor=self.zoom_factor)

        super().build(input_shape)

    def call(self, x):
        x = self.RandomFlip(x)
        x = self.RandomRotation(x)
        x = self.RandomZoom(x)

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "rotation_factor": self.rotation_factor,
                "zoom_factor": self.zoom_factor,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class PretrainedModel(layers.Layer):
    """Sử dụng các pretrained models ở trong **keras.applications**
    Attributes:
        model_name (str): Tên pretrained model, vd: vgg16, vgg19, ....
        num_trainable (int, optional): Số lượng các lớp đầu tiên cho trainable = True. Defaults to 0.
    """

    def __init__(self, model_name, num_trainable=0, **kwargs):
        if num_trainable < 0:
            raise ValueError(
                "=========ERROR: Tham số <num_trainable> trong class PretrainedModel phải >= 0   ============="
            )

        # super(ConvNetBlock, self).__init__()
        super().__init__(**kwargs)
        self.model_name = model_name
        self.num_trainable = num_trainable

    def build(self, input_shape):
        if self.model_name == "vgg16":
            self.model = keras.applications.vgg16.VGG16(
                weights="imagenet", include_top=False
            )
            self.preprocess_input = keras.applications.vgg16.preprocess_input
        elif self.model_name == "vgg19":
            self.model = keras.applications.vgg19.VGG19(
                weights="imagenet", include_top=False
            )
            self.preprocess_input = keras.applications.vgg19.preprocess_input
        else:
            raise ValueError(
                "=========ERROR: Pretrained model name is not valid============="
            )

        # Cập nhật trạng thái trainable cho các lớp đầu
        if self.num_trainable == 0:
            self.model.trainable = False
        else:
            self.model.trainable = True
            for layer in self.model.layers[: -self.num_trainable]:
                layer.trainable = False

        super().build(input_shape)

    def call(self, x):
        x = self.preprocess_input(x)
        x = self.model(x)

        return x


class PositionalEmbedding(layers.Layer):
    def __init__(self, sequence_length, input_dim, output_dim, **kwargs):
        # TODO: d
        print("Update  PositionalEmbedding lần 1")
        # d

        super().__init__(**kwargs)
        # Các layers
        self.token_embeddings = layers.Embedding(
            input_dim=input_dim, output_dim=output_dim
        )  # Embedding layers cho token indices
        self.position_embeddings = layers.Embedding(
            input_dim=sequence_length, output_dim=output_dim
        )  # Layer này cho token positions

        # Các siêu tham số
        self.sequence_length = sequence_length
        self.input_dim = input_dim
        self.output_dim = output_dim

    def call(self, inputs):

        length = tf.shape(inputs)[-1]
        positions = tf.range(start=0, limit=length, delta=1)
        embedded_tokens = self.token_embeddings(inputs)
        embedded_positions = self.position_embeddings(positions)
        embedded = embedded_tokens + embedded_positions  # Cộng 2 embedding vectors lại

        # Save mask using Keras's _keras_mask mechanism
        embedded._keras_mask = tf.not_equal(inputs, 0)
        return embedded

    def build(self, input_shape):
        super().build(input_shape)

    def compute_mask(
        self, inputs, mask=None
    ):  # Giống với Embedding layer,  layer này nên tạo ra mask để ignore paddings 0 trong inputs
        return None

    def get_config(self):  # Để lưu được model
        config = super().get_config()
        config.update(
            {
                "output_dim": self.output_dim,
                "sequence_length": self.sequence_length,
                "input_dim": self.input_dim,
            }
        )
        return config


class TransformerEncoder(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, **kwargs):
        super().__init__(**kwargs)
        # Các siêu tham số
        self.supports_masking = True  # Có hỗ trợ masking
        self.embed_dim = embed_dim  # size của input token vectors
        self.dense_dim = dense_dim  # Size của Denser layer
        self.num_heads = num_heads  # Số lượng attention heads

        # Các layers
        self.attention = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.dense_proj = keras.Sequential(
            [
                layers.Dense(dense_dim, activation="relu"),
                layers.Dense(embed_dim),
            ]
        )
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()

    def call(self, inputs, mask=None):  # Tính toán là ở trong hàm call()
        if mask is not None:
            mask = mask[
                :, tf.newaxis, :
            ]  # mask được tạo ra bởi Embedding layer là 2D, nhưng attention layer thì yêu cầu 3D hoặc 4D -> thêm chiều
        attention_output = self.attention(inputs, inputs, attention_mask=mask)
        proj_input = self.layernorm_1(inputs + attention_output)
        proj_output = self.dense_proj(proj_input)
        return self.layernorm_2(proj_input + proj_output)

    def build(self, input_shape):
        super().build(input_shape)

    def get_config(self):  # Cần thiết để lưu model
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "num_heads": self.num_heads,
                "dense_dim": self.dense_dim,
            }
        )
        return config


class TransformerDecoder(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads
        self.attention_1 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.attention_2 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.dense_proj = keras.Sequential(
            [
                layers.Dense(dense_dim, activation="relu"),
                layers.Dense(embed_dim),
            ]
        )
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()
        self.layernorm_3 = layers.LayerNormalization()
        self.supports_masking = True

    def call(self, inputs, encoder_outputs, mask=None):
        causal_mask = self.get_causal_attention_mask(inputs)  # Get causal_mask
        padding_mask = None  # Define để né lỗi UnboundLocalError
        if mask is not None:  # Chuẩn bị input mask
            padding_mask = tf.cast(mask[:, tf.newaxis, :], dtype="int32")
            padding_mask = tf.minimum(
                padding_mask, causal_mask
            )  # merge 2 masks với nhau
        attention_output_1 = self.attention_1(
            query=inputs,
            value=inputs,
            key=inputs,
            attention_mask=causal_mask,  # pass causal_mask vào layer attention đâu tiên,
            # cái thực hiện  self-attention cho target sequence
        )
        attention_output_1 = self.layernorm_1(inputs + attention_output_1)
        attention_output_2 = self.attention_2(
            query=attention_output_1,
            value=encoder_outputs,
            key=encoder_outputs,
            attention_mask=padding_mask,  # pass combined mask cho layer attention thứ 2,
            # cái mà relates the source sequence to the target sequence.
        )
        attention_output_2 = self.layernorm_2(attention_output_1 + attention_output_2)
        proj_output = self.dense_proj(attention_output_2)
        return self.layernorm_3(attention_output_2 + proj_output)

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "num_heads": self.num_heads,
                "dense_dim": self.dense_dim,
            }
        )
        return config

    def get_causal_attention_mask(self, inputs):
        input_shape = tf.shape(inputs)
        batch_size, sequence_length = input_shape[0], input_shape[1]
        i = tf.range(sequence_length)[:, tf.newaxis]
        j = tf.range(sequence_length)
        mask = tf.cast(i >= j, dtype="int32")
        mask = tf.reshape(mask, (1, input_shape[1], input_shape[1]))
        mult = tf.concat(
            [tf.expand_dims(batch_size, -1), tf.constant([1, 1], dtype=tf.int32)],
            axis=0,
        )
        return tf.tile(mask, mult)

    def build(self, input_shape):
        # No custom weights to create, so just mark as built
        super().build(input_shape)


class DenseBatchNormalizationDropout(layers.Layer):
    def __init__(self, units, dropout_rate, **kwargs):
        super().__init__(**kwargs)
        self.units = units
        self.dropout_rate = dropout_rate

    def build(self, input_shape):
        self.BatchNormalization = layers.BatchNormalization()
        self.Dense = layers.Dense(self.units, activation="relu")
        self.Dropout = layers.Dropout(self.dropout_rate)

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        x = self.BatchNormalization(x)
        x = self.Dense(x)
        x = self.Dropout(x)

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "units": self.units,
                "dropout_rate": self.dropout_rate,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class DenseBatchNormalization(layers.Layer):
    def __init__(self, units, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.BatchNormalization = layers.BatchNormalization()
        self.Dense = layers.Dense(self.units, activation="relu")

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        x = self.BatchNormalization(x)
        x = self.Dense(x)

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "units": self.units,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class PassThroughLayer(layers.Layer):
    """Đơn giản là placeholdout layer, không biến đổi gì cả"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):

        super().build(input_shape)

    def call(self, x):

        return x

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class BidirectionalRNN(layers.Layer):
    def __init__(
        self,
        layer_name,
        units,
        merge_mode="cat",
        return_sequences=False,
        recurrent_dropout=0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.layer_name = layer_name
        self.units = units
        self.merge_mode = merge_mode
        self.return_sequences = return_sequences
        self.recurrent_dropout = recurrent_dropout

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "layer_name": self.layer_name,
                "units": self.units,
                "merge_mode": self.merge_mode,
                "return_sequences": self.return_sequences,
                "recurrent_dropout": self.recurrent_dropout,
            }
        )
        return config

    def build(self, input_shape):
        ClassName = globals()[self.layer_name]
        self.BidirectionalRNN = layers.Bidirectional(
            ClassName(
                units=self.units,
                recurrent_dropout=self.recurrent_dropout,
                return_sequences=self.return_sequences,
            ),
            merge_mode=self.merge_mode,
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        x = self.BidirectionalRNN(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)
