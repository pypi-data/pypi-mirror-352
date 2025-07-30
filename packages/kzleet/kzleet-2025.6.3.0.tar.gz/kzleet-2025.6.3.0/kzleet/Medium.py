from .Solution import Solution

class Solution_909(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 909, 'Medium')

    def snakesAndLadders(self, board):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/snakes-and-ladders/description/?envType=daily-question&envId=2025-05-31

        :type board: List[List[int]]
        :rtype: int
        '''

        flat = []
        n = len(board)
        for i in range(n - 1, -1, -1): # provided in reverse
            row = board[i]
            if (n - 1 - i) % 2 == 0:
                flat.extend(row)
            else:
                flat.extend(reversed(row))

        queue = [(0, 0)]  # (position, rolls)
        visited = set([0])
        front = 0

        n = len(flat)
        while front < len(queue):
            pos, rolls = queue[front]
            front += 1

            if pos == n - 1:
                return rolls

            for k in range(1, 7):
                next_pos = pos + k
                if next_pos >= n:
                    continue

                if flat[next_pos] != -1:
                    next_pos = flat[next_pos] - 1 # 0 index

                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, rolls + 1))

        return -1

    main = snakesAndLadders

class Solution_2131(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2131, 'Medium')

    def longestPalindrome(self, words):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/?envType=daily-question&envId=2025-05-25

        :type colors: str
        :type edges: List[List[int]]
        :rtype: int
        '''

        count = {}
        for word in words:
            if word in count:
                count[word] += 1
            else:
                count[word] = 1

        length = 0
        center = False

        for word in list(count.keys()):
            rev = word[::-1]
            if word != rev:
                if rev in count:
                    pairs = min(count[word], count[rev])
                    length += pairs * 4
                    count[word] -= pairs
                    count[rev] -= pairs

            else:
                pairs = count[word] // 2
                length += pairs * 4
                count[word] -= pairs * 2

                if count[word] > 0: # should be odd
                    center = True

        if center:
            length += 2

        return length

    main = longestPalindrome

class Solution_2359(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2359, 'Medium')

    def closestMeetingNode(self, edges, node1, node2):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-closest-node-to-given-two-nodes/?envType=daily-question&envId=2025-05-30

        :type edges: List[int]
        :type node1: int
        :type node2: int
        :rtype: int
        '''

        def distances(node):
            distance = 0
            v = set()
            r = [len(edges) * 10] * len(edges)

            while True:
                if node in v: break
                v.add(node)
                r[node] = distance
                distance += 1
                node = edges[node]
                if node == -1: break

            return r

        d1 = distances(node1)
        d2 = distances(node2)

        argmin = 0
        impossible = True

        for i in range(len(edges)):
            if d1[i] < len(edges) * 10 and d2[i] < len(edges) * 10:
                impossible = False

            if max(d1[i], d2[i]) < max(d1[argmin], d2[argmin]):
                argmin = i

        if impossible: return -1
        return argmin

    main = closestMeetingNode

class Solution_3372(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3372, 'Medium')

    def maxTargetNodes(self, edges1, edges2, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-i/?envType=daily-question&envId=2025-05-28

        :type edges1: List[List[int]]
        :type edges2: List[List[int]]
        :type k: int
        :rtype: List[int]
        '''

        def build_adj(edges):
            nodes = {}
            for i, j in edges:
                if i in nodes.keys():
                    nodes[i].append(j)

                else:
                    nodes[i] = [j]

                if j in nodes.keys():
                    nodes[j].append(i)

                else:
                    nodes[j] = [i]

            return nodes

        nodes1 = build_adj(edges1)
        nodes2 = build_adj(edges2)

        def target(node, max_depth, graph):
            result = set()

            def dfs(current, depth):
                if depth > max_depth:
                    return

                if current in result:
                    return

                result.add(current)

                for neighbor in graph.get(current, []):
                    dfs(neighbor, depth + 1)

            dfs(node, 0)
            return result

        max_targets2 = 0
        for node in nodes2:
            reachable = target(node, k - 1, nodes2)
            max_targets2 = max(max_targets2, len(reachable))

        result = []
        for node in nodes1:
            reachable1 = target(node, k, nodes1)
            result.append(len(reachable1) + max_targets2)

        return result

    main = maxTargetNodes

class Solution_2929(Solution):

    '''
    This solution just usees the stars and bars problem.
    It also includes exclutions for the usage of limit.
    However, since we multiply by 3, cases like (3, 3, 1) where 3 is over the limit need to be added back in.
    This is because we subtract for child 1, but child 2 has the same case which we subtract 3 times again.
    Then, for cases like (3, 3, 3), we need to subtract again since we added it back in.
    '''

    def __init__(self):
        super().__init__('Kevin Zhu', 2929, 'Medium')

    def distributeCandies(self, n, limit):
            '''
            Author: Kevin Zhu
            Link: https://leetcode.com/problems/distribute-candies-among-children-ii/?envType=daily-question&envId=2025-06-01

            :type n: int
            :type limit: int
            :rtype: int
            '''

            def choose(n, k):
                if k < 0 or k > n:
                    return 0
                if k == 0 or k == n:
                    return 1
                if k == 1:
                    return n
                if k == 2:
                    return n * (n - 1) // 2
                return 0

            # Total ways without restrictions
            total = choose(n + 2, 2)

            # Subtract cases where 1 child exceeds limit
            over1 = 3 * choose(n - (limit + 1) + 2, 2) if n >= limit + 1 else 0

            # Add back cases where 2 children exceed limit
            over2 = 3 * choose(n - 2 * (limit + 1) + 2, 2) if n >= 2 * (limit + 1) else 0

            # Subtract cases where all 3 children exceed limit
            over3 = choose(n - 3 * (limit + 1) + 2, 2) if n >= 3 * (limit + 1) else 0

            return total - over1 + over2 - over3

    main = distributeCandies