import tensorflow as tf
from tensorflow.keras import layers
from Mylib import tf_layers


class DenseBatchNormalizationDropoutList(layers.Layer):
    def __init__(self, dropout_rate, list_units, do_have_last_layer=True, **kwargs):
        super().__init__(**kwargs)
        self.dropout_rate = dropout_rate
        self.list_units = list_units
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "dropout_rate": self.dropout_rate,
                "list_units": self.list_units,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        self.list_DenseBatchNormalizationDropout = [
            tf_layers.DenseBatchNormalizationDropout(
                units=units, dropout_rate=self.dropout_rate
            )
            for units in self.list_units
        ]
        self.DenseBatchNormalization = tf_layers.DenseBatchNormalization(
            units=self.list_units[-1]
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_DenseBatchNormalizationDropout:
            x = layer(x)

        # Xử lí x thông qua layer cuối
        if self.do_have_last_layer:
            x = self.DenseBatchNormalization(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class DenseBatchNormalizationList(layers.Layer):
    def __init__(self, list_units, **kwargs):
        super().__init__(**kwargs)
        self.list_units = list_units

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "list_units": self.list_units,
            }
        )
        return config

    def build(self, input_shape):
        self.list_DenseBatchNormalization = [
            tf_layers.DenseBatchNormalization(
                units=units,
            )
            for units in self.list_units
        ]

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_DenseBatchNormalization:
            x = layer(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class Conv2DBlock_1Conv2D_NoMaxPoolingList(layers.Layer):
    def __init__(self, list_filters, **kwargs):
        super().__init__(**kwargs)
        self.list_filters = list_filters

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "list_filters": self.list_filters,
            }
        )
        return config

    def build(self, input_shape):
        self.list_Conv2DBlock_1Conv2D_NoMaxPooling = [
            tf_layers.Conv2DBlock_1Conv2D_NoMaxPooling(
                filters=filters,
            )
            for filters in self.list_filters
        ]

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_Conv2DBlock_1Conv2D_NoMaxPooling:
            x = layer(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class Conv2DBlock_2Conv2DList(layers.Layer):
    def __init__(self, list_filters, do_have_last_layer=True, **kwargs):
        super().__init__(**kwargs)
        self.list_filters = list_filters
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "list_filters": self.list_filters,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        self.list_Conv2DBlock_2Conv2D = [
            tf_layers.Conv2DBlock_2Conv2D(
                filters=filters,
            )
            for filters in self.list_filters
        ]
        self.Conv2DBlock_1Conv2D_NoMaxPooling = (
            tf_layers.Conv2DBlock_1Conv2D_NoMaxPooling(filters=self.list_filters[-1])
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_Conv2DBlock_2Conv2D:
            x = layer(x)

        # Xử lí x thông qua layer cuối cùng
        if self.do_have_last_layer:
            x = self.Conv2DBlock_1Conv2D_NoMaxPooling(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class Conv2DBlock_1Conv2DList(layers.Layer):
    def __init__(self, list_filters, do_have_last_layer=True, **kwargs):
        super().__init__(**kwargs)
        self.list_filters = list_filters
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "list_filters": self.list_filters,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        self.list_Conv2DBlock_1Conv2D = [
            tf_layers.Conv2DBlock_1Conv2D(
                filters=filters,
            )
            for filters in self.list_filters
        ]
        self.Conv2DBlock_1Conv2D_NoMaxPooling = (
            tf_layers.Conv2DBlock_1Conv2D_NoMaxPooling(filters=self.list_filters[-1])
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_Conv2DBlock_1Conv2D:
            x = layer(x)

        # Xử lí x thông qua layer cuối cùng
        if self.do_have_last_layer:
            x = self.Conv2DBlock_1Conv2D_NoMaxPooling(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class Conv2DBlock_AdvancedList(layers.Layer):
    def __init__(self, list_filters, do_have_last_layer=True, **kwargs):
        super().__init__(**kwargs)
        self.list_filters = list_filters
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "list_filters": self.list_filters,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        self.list_Conv2DBlock_Advanced = [
            tf_layers.Conv2DBlock_Advanced(
                filters=filters,
            )
            for filters in self.list_filters
        ]

        self.Conv2DBlock_1Conv2D_NoMaxPooling = (
            tf_layers.Conv2DBlock_1Conv2D_NoMaxPooling(filters=self.list_filters[-1])
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_Conv2DBlock_Advanced:
            x = layer(x)

        # Xử lí x thông qua layer cuối cùng
        if self.do_have_last_layer:
            x = self.Conv2DBlock_1Conv2D_NoMaxPooling(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class SeparableConv2DBlock_AdvancedList(layers.Layer):
    def __init__(self, list_filters, do_have_last_layer=True, **kwargs):
        super().__init__(**kwargs)
        self.list_filters = list_filters
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "list_filters": self.list_filters,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        self.list_SeparableConv2DBlock_Advanced = [
            tf_layers.SeparableConv2DBlock_Advanced(
                filters=filters,
            )
            for filters in self.list_filters
        ]

        self.Conv2DBlock_1Conv2D_NoMaxPooling = (
            tf_layers.Conv2DBlock_1Conv2D_NoMaxPooling(filters=self.list_filters[-1])
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_SeparableConv2DBlock_Advanced:
            x = layer(x)

        # Xử lí x thông qua layer cuối cùng
        if self.do_have_last_layer:
            x = self.Conv2DBlock_1Conv2D_NoMaxPooling(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class BidirectionalRNNDropoutList(layers.Layer):
    def __init__(
        self,
        layer_name,
        list_units,
        recurrent_dropout,
        merge_mode="concat",
        do_have_last_layer=True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.layer_name = layer_name
        self.list_units = list_units
        self.recurrent_dropout = recurrent_dropout
        self.merge_mode = merge_mode
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "layer_name": self.layer_name,
                "list_units": self.list_units,
                "recurrent_dropout": self.recurrent_dropout,
                "merge_mode": self.merge_mode,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        LayerName = globals()[self.layer_name]

        self.list_BidirectionalRNNDropout = [
            layers.Bidirectional(
                LayerName(
                    units,
                    return_sequences=True,
                    recurrent_dropout=self.recurrent_dropout,
                ),
                merge_mode=self.merge_mode,
            )
            for units in self.list_units
        ]

        self.BidirectionalRNN = layers.Bidirectional(
            LayerName(
                self.list_units[-1],
            ),
            merge_mode=self.merge_mode,
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_BidirectionalRNNDropout:
            x = layer(x)

        # Xử lí x thông qua layer cuối
        if self.do_have_last_layer:
            x = self.BidirectionalRNN(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class BidirectionalRNNList(layers.Layer):
    def __init__(self, layer_name, list_units, merge_mode="concat", **kwargs):
        super().__init__(**kwargs)
        self.layer_name = layer_name
        self.list_units = list_units
        self.merge_mode = merge_mode

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "layer_name": self.layer_name,
                "list_units": self.list_units,
                "merge_mode": self.merge_mode,
            }
        )
        return config

    def build(self, input_shape):
        LayerName = globals()[self.layer_name]

        self.list_BidirectionalRNNDropout = [
            layers.Bidirectional(
                LayerName(
                    units,
                    return_sequences=True,
                ),
                merge_mode=self.merge_mode,
            )
            for units in self.list_units
        ]

        self.BidirectionalRNN = layers.Bidirectional(
            LayerName(
                self.list_units[-1],
            ),
            merge_mode=self.merge_mode,
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_BidirectionalRNNDropout:
            x = layer(x)

        x = self.BidirectionalRNN(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class RNNDropoutList(layers.Layer):
    def __init__(
        self,
        layer_name,
        list_units,
        recurrent_dropout,
        do_have_last_layer=True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.layer_name = layer_name
        self.list_units = list_units
        self.recurrent_dropout = recurrent_dropout
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "layer_name": self.layer_name,
                "list_units": self.list_units,
                "recurrent_dropout": self.recurrent_dropout,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        LayerName = globals()[self.layer_name]

        self.list_RNNDropout = [
            LayerName(
                units,
                return_sequences=True,
                recurrent_dropout=self.recurrent_dropout,
            )
            for units in self.list_units
        ]

        self.RNN = LayerName(
            self.list_units[-1],
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_RNNDropout:
            x = layer(x)

        # Xử lí x thông qua layer cuối cùng
        if self.do_have_last_layer:
            x = self.RNN(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class RNNList(layers.Layer):
    def __init__(self, layer_name, list_units, do_have_last_layer=True, **kwargs):
        super().__init__(**kwargs)
        self.layer_name = layer_name
        self.list_units = list_units
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "layer_name": self.layer_name,
                "list_units": self.list_units,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        LayerName = globals()[self.layer_name]

        self.list_RNNDropout = [
            LayerName(
                units,
                return_sequences=True,
            )
            for units in self.list_units
        ]

        self.RNN = LayerName(
            self.list_units[-1],
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_RNNDropout:
            x = layer(x)

        # Xử lí x thông qua layer cuối cùng
        if self.do_have_last_layer:
            x = self.RNN(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class TransformerEncoderList(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, num_layers, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads
        self.num_layers = num_layers

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "dense_dim": self.dense_dim,
                "num_heads": self.num_heads,
                "num_layers": self.num_layers,
            }
        )
        return config

    def build(self, input_shape):
        self.list_TransformerEncoder = [
            tf_layers.TransformerDecoder(
                embed_dim=self.embed_dim,
                dense_dim=self.dense_dim,
                num_heads=self.num_heads,
            )
            for _ in range(self.num_layers)
        ]

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_TransformerEncoder:
            x = layer(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class TransformerDecoderList(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, num_layers, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads
        self.num_layers = num_layers

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "dense_dim": self.dense_dim,
                "num_heads": self.num_heads,
                "num_layers": self.num_layers,
            }
        )
        return config

    def build(self, input_shape):
        self.list_TransformerDecoder = [
            tf_layers.TransformerDecoder(
                embed_dim=self.embed_dim,
                dense_dim=self.dense_dim,
                num_heads=self.num_heads,
            )
            for _ in range(self.num_layers)
        ]

        super().build(input_shape)

    def call(self, x, encoder_outputs):
        # Xử lí x
        for layer in self.list_TransformerDecoder:
            x = layer(x, encoder_outputs)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)
