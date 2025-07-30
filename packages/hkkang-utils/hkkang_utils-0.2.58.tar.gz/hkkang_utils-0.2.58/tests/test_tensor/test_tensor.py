import unittest

import src.hkkang_utils.tensor as tensor_utils
from tests.test_tensor.utils import (
    Float16ModelWithBias,
    Float32ModelWithBias,
    Float32ModelWithOutBias,
    to_mb,
)


class Test_tensor_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_tensor_utils, self).__init__(*args, **kwargs)

    def test_zero_pad_batching_one_dim(self):
        pass

    def test_zero_pad_batching_two_dim(self):
        pass

    def test_zero_pad_batching(self):
        pass

    def test_calculate_model_size(self):
        model_f32_wo_bias = Float32ModelWithOutBias()
        model_size = tensor_utils.calculate_model_size(model_f32_wo_bias, in_MB=True)
        self.assertEqual(model_size, to_mb(model_f32_wo_bias.model_size))

        model_f32_w_bias = Float32ModelWithBias()
        model_size = tensor_utils.calculate_model_size(model_f32_w_bias, in_MB=True)
        self.assertEqual(model_size, to_mb(model_f32_w_bias.model_size))

        model_f16_w_bias = Float16ModelWithBias()
        model_size = tensor_utils.calculate_model_size(model_f16_w_bias, in_MB=True)
        self.assertEqual(model_size, to_mb(model_f16_w_bias.model_size))


if __name__ == "__main__":
    unittest.main()
