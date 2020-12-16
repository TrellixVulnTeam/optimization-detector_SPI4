import csv
import os
import shutil
import tempfile
from unittest import TestCase

from src.extractor import extract_dot_text, extract_dot_text_to_file, \
    extract_function_to_file, get_opcode

PREFIX = "BCCFLT_"


class TestExtractor(TestCase):
    tmpdir: str = None
    file: str = "./resources/tempfile"
    expected = [243, 15, 30, 250, 65, 87, 73, 137, 247, 65, 86, 76, 141, 53,
                127, 15, 0, 0, 65, 85, 69, 49, 237, 65, 84, 85, 137, 253, 83,
                72, 141, 29, 0, 16, 0, 0, 72, 129, 236, 104, 1, 0, 0, 100, 72,
                139, 4, 37, 40, 0, 0, 0, 72, 137, 132, 36, 88, 1, 0, 0, 49,
                192, 72, 141, 5, 81, 15, 0, 0, 76, 141, 100, 36, 80, 199, 68,
                36, 44, 128, 1, 0, 0, 72, 137, 68, 36, 80, 72, 141, 5, 63, 15,
                0, 0, 72, 137, 68, 36, 112, 72, 141, 5, 58, 15, 0, 0, 72, 137,
                132, 36, 144, 0, 0, 0, 72, 141, 5, 53, 15, 0, 0, 72, 137, 132,
                36, 176, 0, 0, 0, 72, 141, 5, 43, 15, 0, 0, 72, 137, 132, 36,
                208, 0, 0, 0, 72, 141, 5, 33, 15, 0, 0, 72, 137, 132, 36, 240,
                0, 0, 0, 72, 141, 5, 23, 15, 0, 0, 199, 68, 36, 88, 1, 0, 0, 0,
                72, 199, 68, 36, 96, 0, 0, 0, 0, 199, 68, 36, 104, 112, 0, 0,
                0, 199, 68, 36, 120, 1, 0, 0, 0, 72, 199, 132, 36, 128, 0, 0,
                0, 0, 0, 0, 0, 199, 132, 36, 136, 0, 0, 0, 115, 0, 0, 0, 199,
                132, 36, 152, 0, 0, 0, 1, 0, 0, 0, 72, 199, 132, 36, 160, 0, 0,
                0, 0, 0, 0, 0, 199, 132, 36, 168, 0, 0, 0, 100, 0, 0, 0, 199,
                132, 36, 184, 0, 0, 0, 1, 0, 0, 0, 72, 199, 132, 36, 192, 0, 0,
                0, 0, 0, 0, 0, 199, 132, 36, 200, 0, 0, 0, 109, 0, 0, 0, 199,
                132, 36, 216, 0, 0, 0, 1, 0, 0, 0, 72, 199, 132, 36, 224, 0, 0,
                0, 0, 0, 0, 0, 199, 132, 36, 232, 0, 0, 0, 110, 0, 0, 0, 199,
                132, 36, 248, 0, 0, 0, 0, 0, 0, 0, 72, 199, 132, 36, 0, 1, 0,
                0, 0, 0, 0, 0, 72, 137, 132, 36, 16, 1, 0, 0, 72, 139, 6, 199,
                132, 36, 8, 1, 0, 0, 104, 0, 0, 0, 199, 132, 36, 24, 1, 0, 0,
                0, 0, 0, 0, 72, 199, 132, 36, 32, 1, 0, 0, 0, 0, 0, 0, 199,
                132, 36, 40, 1, 0, 0, 118, 0, 0, 0, 72, 199, 132, 36, 48, 1, 0,
                0, 0, 0, 0, 0, 199, 132, 36, 56, 1, 0, 0, 0, 0, 0, 0, 72, 199,
                132, 36, 64, 1, 0, 0, 0, 0, 0, 0, 199, 132, 36, 72, 1, 0, 0, 0,
                0, 0, 0, 72, 137, 5, 8, 44, 0, 0, 72, 199, 68, 36, 8, 0, 0, 0,
                0, 72, 199, 68, 36, 16, 0, 0, 0, 0, 69, 49, 192, 76, 137, 225,
                72, 141, 21, 244, 13, 0, 0, 76, 137, 254, 137, 239, 232, 95,
                253, 255, 255, 131, 248, 255, 15, 132, 202, 0, 0, 0, 133, 192,
                116, 220, 131, 232, 100, 131, 248, 18, 15, 135, 176, 0, 0, 0,
                72, 99, 4, 131, 72, 1, 216, 62, 255, 224, 72, 141, 61, 177, 13,
                0, 0, 232, 16, 253, 255, 255, 49, 255, 232, 169, 253, 255, 255,
                72, 139, 5, 114, 43, 0, 0, 72, 137, 68, 36, 8, 235, 165, 76,
                139, 53, 100, 43, 0, 0, 235, 156, 72, 139, 61, 91, 43, 0, 0,
                232, 166, 253, 255, 255, 73, 137, 197, 72, 133, 192, 117, 136,
                72, 141, 61, 108, 13, 0, 0, 232, 210, 3, 0, 0, 72, 139, 61, 59,
                43, 0, 0, 72, 141, 116, 36, 44, 232, 225, 3, 0, 0, 133, 192,
                15, 132, 99, 255, 255, 255, 72, 139, 61, 66, 43, 0, 0, 72, 139,
                13, 27, 43, 0, 0, 72, 141, 21, 220, 12, 0, 0, 49, 192, 190, 1,
                0, 0, 0, 232, 72, 253, 255, 255, 191, 1, 0, 0, 0, 232, 62, 3,
                0, 0, 49, 255, 232, 55, 3, 0, 0, 72, 139, 5, 240, 42, 0, 0, 72,
                137, 68, 36, 16, 233, 32, 255, 255, 255, 191, 1, 0, 0, 0, 232,
                28, 3, 0, 0, 77, 133, 237, 116, 54, 139, 84, 36, 44, 76, 137,
                239, 190, 194, 0, 0, 0, 49, 192, 232, 212, 252, 255, 255, 137,
                199, 133, 192, 15, 136, 90, 1, 0, 0, 232, 117, 252, 255, 255,
                133, 192, 15, 132, 54, 1, 0, 0, 72, 141, 61, 20, 13, 0, 0, 232,
                49, 3, 0, 0, 72, 141, 61, 229, 12, 0, 0, 49, 219, 72, 141, 108,
                36, 48, 232, 222, 251, 255, 255, 76, 141, 37, 193, 12, 0, 0,
                72, 137, 68, 36, 48, 72, 139, 68, 36, 16, 72, 137, 68, 36, 56,
                72, 141, 5, 195, 12, 0, 0, 72, 137, 68, 36, 64, 72, 137, 68,
                36, 72, 76, 139, 76, 221, 0, 77, 133, 201, 15, 132, 13, 1, 0,
                0, 72, 131, 206, 255, 49, 192, 76, 137, 207, 72, 137, 241, 242,
                174, 72, 247, 209, 72, 141, 81, 255, 77, 133, 246, 15, 132, 6,
                1, 0, 0, 72, 137, 241, 76, 137, 247, 242, 174, 72, 137, 200,
                72, 247, 208, 72, 131, 232, 1, 72, 139, 124, 36, 8, 76, 137,
                76, 36, 16, 76, 141, 124, 2, 8, 72, 133, 255, 15, 132, 227, 0,
                0, 0, 49, 192, 72, 131, 201, 255, 242, 174, 72, 137, 200, 72,
                247, 208, 77, 141, 124, 7, 255, 76, 137, 255, 232, 214, 251,
                255, 255, 76, 139, 76, 36, 16, 72, 133, 192, 73, 137, 197, 15,
                132, 41, 1, 0, 0, 77, 133, 246, 15, 132, 242, 0, 0, 0, 255,
                116, 36, 8, 65, 86, 72, 131, 201, 255, 76, 137, 254, 76, 137,
                239, 186, 1, 0, 0, 0, 76, 141, 5, 52, 12, 0, 0, 49, 192, 232,
                25, 251, 255, 255, 89, 94, 49, 192, 72, 139, 124, 36, 8, 72,
                131, 201, 255, 242, 174, 72, 137, 200, 72, 247, 208, 141, 112,
                255, 76, 137, 239, 232, 217, 250, 255, 255, 137, 68, 36, 28,
                133, 192, 15, 137, 180, 0, 0, 0, 232, 8, 251, 255, 255, 131,
                56, 17, 116, 47, 72, 141, 61, 218, 11, 0, 0, 232, 7, 2, 0, 0,
                76, 137, 239, 232, 255, 250, 255, 255, 76, 137, 239, 232, 215,
                250, 255, 255, 49, 255, 232, 144, 251, 255, 255, 72, 141, 61,
                159, 11, 0, 0, 232, 228, 1, 0, 0, 76, 137, 239, 232, 188, 250,
                255, 255, 72, 131, 195, 1, 72, 131, 251, 4, 15, 133, 215, 254,
                255, 255, 139, 124, 36, 28, 233, 123, 254, 255, 255, 49, 192,
                233, 5, 255, 255, 255, 76, 137, 255, 232, 6, 251, 255, 255, 76,
                139, 76, 36, 16, 72, 133, 192, 73, 137, 197, 116, 93, 77, 133,
                246, 116, 53, 65, 84, 65, 86, 186, 1, 0, 0, 0, 76, 137, 254,
                72, 131, 201, 255, 76, 137, 239, 76, 141, 5, 110, 11, 0, 0, 49,
                192, 232, 83, 250, 255, 255, 88, 49, 246, 90, 233, 73, 255,
                255, 255, 255, 116, 36, 8, 65, 84, 233, 9, 255, 255, 255, 65,
                84, 65, 84, 235, 201, 139, 116, 36, 44, 139, 124, 36, 28, 232,
                204, 250, 255, 255, 133, 192, 121, 138, 72, 141, 61, 40, 11, 0,
                0, 232, 76, 1, 0, 0, 72, 141, 61, 12, 11, 0, 0, 232, 64, 1, 0,
                0, 243, 15, 30, 250, 49, 237, 73, 137, 209, 94, 72, 137, 226,
                72, 131, 228, 240, 80, 84, 76, 141, 5, 38, 2, 0, 0, 72, 141,
                13, 175, 1, 0, 0, 72, 141, 61, 232, 250, 255, 255, 255, 21, 66,
                40, 0, 0, 244, 144, 72, 141, 61, 105, 40, 0, 0, 72, 141, 5, 98,
                40, 0, 0, 72, 57, 248, 116, 21, 72, 139, 5, 30, 40, 0, 0, 72,
                133, 192, 116, 9, 255, 224, 15, 31, 128, 0, 0, 0, 0, 195, 15,
                31, 128, 0, 0, 0, 0, 72, 141, 61, 57, 40, 0, 0, 72, 141, 53,
                50, 40, 0, 0, 72, 41, 254, 72, 137, 240, 72, 193, 238, 63, 72,
                193, 248, 3, 72, 1, 198, 72, 209, 254, 116, 20, 72, 139, 5,
                245, 39, 0, 0, 72, 133, 192, 116, 8, 255, 224, 102, 15, 31, 68,
                0, 0, 195, 15, 31, 128, 0, 0, 0, 0, 243, 15, 30, 250, 128, 61,
                45, 40, 0, 0, 0, 117, 43, 85, 72, 131, 61, 210, 39, 0, 0, 0,
                72, 137, 229, 116, 12, 72, 139, 61, 214, 39, 0, 0, 232, 25,
                249, 255, 255, 232, 100, 255, 255, 255, 198, 5, 5, 40, 0, 0, 1,
                93, 195, 15, 31, 0, 195, 15, 31, 128, 0, 0, 0, 0, 243, 15, 30,
                250, 233, 119, 255, 255, 255, 15, 31, 128, 0, 0, 0, 0, 243, 15,
                30, 250, 85, 72, 139, 21, 228, 39, 0, 0, 137, 253, 133, 255,
                116, 36, 72, 139, 61, 199, 39, 0, 0, 72, 137, 209, 190, 1, 0,
                0, 0, 49, 192, 72, 141, 21, 126, 7, 0, 0, 232, 209, 249, 255,
                255, 137, 239, 232, 186, 249, 255, 255, 72, 141, 53, 147, 7, 0,
                0, 191, 1, 0, 0, 0, 49, 192, 232, 103, 249, 255, 255, 235, 228,
                15, 31, 68, 0, 0, 243, 15, 30, 250, 80, 88, 72, 131, 236, 8,
                232, 129, 249, 255, 255, 191, 1, 0, 0, 0, 232, 135, 249, 255,
                255, 15, 31, 128, 0, 0, 0, 0, 243, 15, 30, 250, 83, 186, 8, 0,
                0, 0, 72, 137, 243, 72, 131, 236, 16, 100, 72, 139, 4, 37, 40,
                0, 0, 0, 72, 137, 68, 36, 8, 49, 192, 72, 137, 230, 232, 247,
                248, 255, 255, 72, 139, 20, 36, 65, 184, 1, 0, 0, 0, 128, 58,
                0, 117, 13, 72, 61, 255, 15, 0, 0, 119, 5, 137, 3, 69, 49, 192,
                72, 139, 68, 36, 8, 100, 72, 51, 4, 37, 40, 0, 0, 0, 117, 9,
                72, 131, 196, 16, 68, 137, 192, 91, 195, 232, 141, 248, 255,
                255, 102, 46, 15, 31, 132, 0, 0, 0, 0, 0, 15, 31, 0, 243, 15,
                30, 250, 65, 87, 76, 141, 61, 227, 35, 0, 0, 65, 86, 73, 137,
                214, 65, 85, 73, 137, 245, 65, 84, 65, 137, 252, 85, 72, 141,
                45, 212, 35, 0, 0, 83, 76, 41, 253, 72, 131, 236, 8, 232, 143,
                246, 255, 255, 72, 193, 253, 3, 116, 31, 49, 219, 15, 31, 128,
                0, 0, 0, 0, 76, 137, 242, 76, 137, 238, 68, 137, 231, 65, 255,
                20, 223, 72, 131, 195, 1, 72, 57, 221, 117, 234, 72, 131, 196,
                8, 91, 93, 65, 92, 65, 93, 65, 94, 65, 95, 195, 102, 102, 46,
                15, 31, 132, 0, 0, 0, 0, 0, 243, 15, 30, 250, 195]

    @classmethod
    def setUpClass(self):
        systmpdir = tempfile.gettempdir()
        self.tmpdir = tempfile.mkdtemp(prefix=PREFIX, dir=systmpdir)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tmpdir)

    # write empty file and asserts no exception is thrown
    def test_extract(self):
        self.assertTrue(os.path.exists(self.file))
        data = extract_dot_text(self.file)
        self.assertEqual(data, self.expected)

    def test_extract_file(self):
        self.assertTrue(os.path.exists(self.file))
        extracted = os.path.join(self.tmpdir, "extracted.bin")
        extract_dot_text_to_file(self.file, extracted)
        with open(extracted, "rb") as fp:
            extracted_data = list(fp.read())
        self.assertEqual(extracted_data, self.expected)

    def test_get_opcode_x8664(self):
        inputs = ["f30f1efa", "e953ffff", "0f97C1", "490faf", "f2ff", "f20fc7"]
        expected = [bytearray(b"\x0f\x1e"),
                    bytearray(b"\xe9"),
                    bytearray(b"\x0f\x97"),
                    bytearray(b"\x0f\xaf"),
                    bytearray(b"\xf2"),
                    bytearray(b"\x0f\xc7")]
        for i in range(0, len(inputs)):
            opcode = get_opcode(bytearray.fromhex(inputs[i]))
            self.assertEqual(opcode, expected[i])

    def test_extract_function_to_file(self):
        self.assertTrue(os.path.exists(self.file))
        extracted = os.path.join(self.tmpdir, "extracted.csv")
        extract_function_to_file(self.file, extracted)
        # can't check the content, so just hope for the best and check method
        # completition
        with open(extracted, "r") as fp:
            read = csv.reader(fp, delimiter=",")
            self.assertEqual(sum(1 for _ in read), 28)
