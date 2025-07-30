from .Solution import Solution

class Solution_2894(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2894, 'Easy')

    def differenceOfSums(self, n, m):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/divisible-and-non-divisible-sums-difference/?envType=daily-question&envId=2025-05-27

        :type n: int
        :type m: int
        :rtype: int
        '''
        num = 0
        for i in range(n + 1):
            num += i if i % m != 0 else -i

        return num

    main = differenceOfSums

class Solution_2942(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2942, 'Easy')

    def findWordsContaining(self, words, x):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-words-containing-character/?envType=daily-question&envId=2025-05-24

        :type words: List[str]
        :type x: str
        :rtype: List[int]
        '''

        indices = []
        for i in range(len(words)):
            if x in words[i]: indices.append(i)

        return indices

    main = findWordsContaining
