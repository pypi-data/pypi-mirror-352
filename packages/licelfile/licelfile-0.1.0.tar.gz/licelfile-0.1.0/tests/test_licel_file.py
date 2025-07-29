import unittest
from licelfile import LicelFilePack, load_licel_file, load_licelfile_pack

class TestLoadLicelFile(unittest.TestCase):
    """ Loads and save licel files """

    def test_read_licel_file_pack(self):
        f = load_licelfile_pack("tests/licel.zip")
        self.assertIsInstance(f, LicelFilePack)


    def test_load_licel_file(self):
        f = load_licel_file('tests/licel/b2542920.375524')
        self.assertEqual(f.nDatasets, 12)
        self.assertEqual(f.measurementSite, 'Vladivos')
        print(f.profiles[0].data[:10])

    def test_save_licel_file(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()