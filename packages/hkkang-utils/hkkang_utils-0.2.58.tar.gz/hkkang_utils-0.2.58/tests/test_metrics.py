import unittest

import src.hkkang_utils.metrics as metrics_utils


class Test_metrics_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_metrics_utils, self).__init__(*args, **kwargs)
    
    def test_compute_f1(self):
        # test_data
        test_data = [{"pred": [1,2,3,4,5,6], "gold": [1,2,3,4,5,6,7,8,9,10], "f1": 0.7499999999999999, "precision": 1, "recall": 0.6},
                     {"pred": [1,2,3,4,5,6,7,8,9,10], "gold": [1,2,3,4,5,6,7,8,9,10], "f1": 1, "precision": 1, "recall": 1},
                     {"pred": [1,2,3,4,5,6,7,8,9,10,11,12], "gold": [1,2,3,4,5,6,7,8,9,10], "f1": 0.9090909090909091, "precision": 10/12, "recall": 1}]
        for datum in test_data:
            f1, precision, recall = metrics_utils.compute_f1(datum["pred"],datum["gold"])
            self.assertEqual(recall, datum["recall"], f"recall pred: {recall}, gold: {datum['recall']}")
            self.assertEqual(precision, datum["precision"], f"precision pred: {precision}, gold: {datum['precision']}")
            self.assertEqual(f1, datum["f1"], f"f1 pred: {f1}, gold: {datum['f1']}")
    
if __name__ == "__main__":
    unittest.main()
    
    