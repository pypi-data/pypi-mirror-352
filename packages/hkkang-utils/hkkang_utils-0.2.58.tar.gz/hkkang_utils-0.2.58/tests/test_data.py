import sys

# Import dataclasses according to Python version
sys_version = sys.version_info
if sys_version[0] == 3 and sys_version[1] >= 7:
    import dataclasses
else:
    try:
        import dataclasses
    except:
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "dataclasses"])
    finally:
        import dataclasses

import unittest
from typing import *

import src.hkkang_utils.data as data_utils


@dataclasses.dataclass
class TmpDataclass:
    a: int
    b: str
    c: Optional[int] = dataclasses.field(default=None)
    d: Optional[str] = dataclasses.field(default=None)
    e: List[int] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class TmpNestedDataclass:
    name: str
    nested: TmpDataclass


class Test_data_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_data_utils, self).__init__(*args, **kwargs)
        self.data_class = TmpDataclass(1, "a", None, None, [1, 2, 3])
        self.nested_data_class = TmpNestedDataclass("tmp_name", self.data_class)
        # Gold dicts
        self.data_class_dic_wo_none = {"a": 1, "b": "a", "e": [1, 2, 3]}
        self.data_class_dic_w_none = {
            "a": 1,
            "b": "a",
            "c": None,
            "d": None,
            "e": [1, 2, 3],
        }
        self.nested_data_class_dic_wo_none = {
            "name": "tmp_name",
            "nested": self.data_class_dic_wo_none,
        }
        self.nested_data_class_dic_w_none = {
            "name": "tmp_name",
            "nested": self.data_class_dic_w_none,
        }

    def test_asdict(self):
        generated_nested_data_class_dict_w_none = data_utils.asdict(
            self.nested_data_class, skip_none=False
        )
        generated_nested_data_class_dict_wo_none = data_utils.asdict(
            self.nested_data_class, skip_none=True
        )

        self.assertEqual(
            generated_nested_data_class_dict_w_none,
            self.nested_data_class_dic_w_none,
            f"Generated:{generated_nested_data_class_dict_w_none}\nGold:{self.nested_data_class_dic_w_none}",
        )
        self.assertEqual(
            generated_nested_data_class_dict_wo_none,
            self.nested_data_class_dic_wo_none,
            f"Generated:{generated_nested_data_class_dict_wo_none}\nGold:{self.nested_data_class_dic_wo_none}",
        )

    def test_from_dict(self):
        generated_nested_data_class_from_w_none = data_utils.from_dict(
            TmpNestedDataclass, self.nested_data_class_dic_w_none
        )
        generated_nested_data_class_from_wo_none = data_utils.from_dict(
            TmpNestedDataclass, self.nested_data_class_dic_wo_none
        )
        self.assertEqual(
            generated_nested_data_class_from_w_none,
            self.nested_data_class,
            f"Generated:{generated_nested_data_class_from_w_none}\nGold:{self.nested_data_class}",
        )
        self.assertEqual(
            generated_nested_data_class_from_wo_none,
            self.nested_data_class,
            f"Generated:{generated_nested_data_class_from_wo_none}\nGold:{self.nested_data_class}",
        )


if __name__ == "__main__":
    unittest.main()
