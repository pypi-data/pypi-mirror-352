import abc
import unittest

import hkkang_utils.pattern as pattern_utils


class Test_pattern_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_pattern_utils, self).__init__(*args, **kwargs)

    def test_singleton_design(self):
        class SingletonClass(metaclass=pattern_utils.SingletonMeta):
            def __init__(self):
                self.a = 1

        a = SingletonClass()
        b = SingletonClass()
        self.assertEqual(a, b)

    def test_singleton_decorator(self):
        @pattern_utils.singleton
        class SingletonClass:
            def __init__(self):
                self.a = 1

        a = SingletonClass()
        b = SingletonClass()
        self.assertEqual(a, b)

    def test_signleton_with_args(self):
        class CustomClassWithArgs(metaclass=pattern_utils.SingletonMetaWithArgs):
            def __init__(self, a):
                self.a = a

        a = CustomClassWithArgs(1)
        b = CustomClassWithArgs(1)
        self.assertEqual(a, b)

        c = CustomClassWithArgs(2)
        self.assertNotEqual(a, c)

    def test_singleton_abc(self):
        class CustomAbstractClass(metaclass=pattern_utils.SingletonABCMeta):
            def __init__(self):
                self.a = 1

            @abc.abstractmethod
            def run(self):
                pass

        class CustomClass(CustomAbstractClass):
            def __init__(self):
                super().__init__()
                self.b = 2

            def run(self):
                pass

        a = CustomClass()
        b = CustomClass()
        self.assertEqual(a, b)

    def test_singleton_abc_with_args(self):
        class CustomAbstractClassWithArgs(
            metaclass=pattern_utils.SingletonABCMetaWithArgs
        ):
            def __init__(self, a):
                self.a = a

            @abc.abstractmethod
            def run(self):
                pass

        class CustomClassWithArgs(CustomAbstractClassWithArgs):
            def __init__(self, a, b):
                super().__init__(a)
                self.b = b

            def run(self):
                pass

        a = CustomClassWithArgs(1, 2)
        b = CustomClassWithArgs(1, 2)
        self.assertEqual(a, b, "a and b are not equal")

        c = CustomClassWithArgs(2, 3)
        self.assertNotEqual(a, c, "a and c are equal")


if __name__ == "__main__":
    unittest.main()
