import unittest

import src.hkkang_utils.string as string_utils


class Test_string_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_string_utils, self).__init__(*args, **kwargs)
    
    def test_multi_space_to_single_space(self):
        pass
    
    def test_is_int(self):
        input_str1 = "123"
        input_str2 = "123.0"
        input_str3 = "123.1"
        input_str4  = "abc1"
        input_str5  = "1abc"
        input_str6  = "1abc1"
        self.assertTrue(string_utils.is_int(input_str1))
        self.assertFalse(string_utils.is_int(input_str2))
        self.assertFalse(string_utils.is_int(input_str3))
        self.assertFalse(string_utils.is_int(input_str4))
        self.assertFalse(string_utils.is_int(input_str5))
        self.assertFalse(string_utils.is_int(input_str6))
        
    
    def test_is_number(self):
        input_str1 = "123"
        input_str2 = "123.0"
        input_str3 = "123.1"
        input_str4  = "abc1"
        input_str5  = "1abc"
        input_str6  = "1abc1"
        self.assertTrue(string_utils.is_number(input_str1), f"{input_str1} is int")
        self.assertTrue(string_utils.is_number(input_str2), f"{input_str2} is int")
        self.assertTrue(string_utils.is_number(input_str3), f"{input_str3} is int")
        self.assertFalse(string_utils.is_number(input_str4), f"{input_str4} is not int")
        self.assertFalse(string_utils.is_number(input_str5), f"{input_str5} is not int")
        self.assertFalse(string_utils.is_number(input_str6), f"{input_str6} is not int")

    def test_remove_substring(self):
        input_str = "abcdefg"
        self.assertTrue(string_utils.remove_substring(input_str, "ac") == "abcdefg")
        self.assertTrue(string_utils.remove_substring(input_str, "de") == "abcfg")

    def test_remove_punctuation(self):
        input_str = "a,b.c;d:e?fg"
        self.assertTrue(string_utils.remove_punctuation(input_str) == "abcdefg")

if __name__ == "__main__":
    unittest.main()
