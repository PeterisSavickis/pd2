import unittest
from worker_2_db import sort_ast_by_pass_dist, sort_ast_by_time  # Importing both functions

class TestSortAsteroids(unittest.TestCase):

    def test_sort_ast_by_pass_dist(self):
        ast_data = [
            ['Ast1', 'url1', 0.1, 0.2, 123, '2021-01-01 00:00:00', '2021-01-01 01:00:00', 10000, 500000, '1'],
            ['Ast2', 'url2', 0.3, 0.4, 456, '2021-01-02 00:00:00', '2021-01-02 01:00:00', 20000, 400000, '2']
        ]
        sorted_data = sort_ast_by_pass_dist(ast_data)
        self.assertEqual(sorted_data[0][0], 'Ast2')
        self.assertEqual(sort_ast_by_pass_dist([]), [])

if __name__ == '__main__':
    unittest.main()
