from .Solution import Solution

class Solution_135(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 135, 'Hard')

    main = None

    def candy(self, ratings):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/candy/?envType=daily-question&envId=2025-06-02

        :type ratings: List[int]
        :rtype: int
        '''

        n = len(ratings)
        candy = [1] * n

        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                if candy[i] <= candy[i - 1]:
                    candy[i] = candy[i - 1] + 1 # in cases like 1, 2, 3 where they are in a row

        for i in reversed(range(n - 1)):
            if ratings[i] > ratings[i + 1]:
                if candy[i] <= candy[i + 1]:
                    candy[i] = max(candy[i], candy[i + 1]) + 1 # if this one is equal to the other or the other is greater than this

        return sum(candy)

    main = candy

class Solution_1857(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 1857, 'Hard')

    def largestPathValue(self, colors, edges):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/largest-color-value-in-a-directed-graph/?envType=daily-question&envId=2025-05-26

        :type colors: str
        :type edges: List[List[int]]
        :rtype: int
        '''

        n = len(colors)

        # Build graph as adjacency list and indegree array
        graph = [[] for _ in range(n)]
        indegree = [0] * n
        for u, v in edges:
            graph[u].append(v)
            indegree[v] += 1

        # Initialize DP table: dp[node][color] = max count of color at node
        dp = [[0] * 26 for _ in range(n)]
        for i in range(n):
            dp[i][ord(colors[i]) - ord('a')] = 1

        # Initialize queue with nodes having indegree zero
        queue = []
        for i in range(n):
            if indegree[i] == 0:
                queue.append(i)

        visited = 0
        max_value = 0

        # BFS traversal (topological sort)
        while queue:
            node = queue.pop(0)  # pop front (acts as deque.popleft())
            visited += 1
            for neighbor in graph[node]:
                for c in range(26):
                    add = 1 if c == ord(colors[neighbor]) - ord('a') else 0
                    if dp[neighbor][c] < dp[node][c] + add:
                        dp[neighbor][c] = dp[node][c] + add
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
            max_value = max(max_value, max(dp[node]))

        return max_value if visited == n else -1

    main = largestPathValue

class Solution_3373(Solution):

    '''
    Explanation for the solution:

    First, a graph is built from the edges provided for both trees.
    The graph is represented as an adjacency list (similar to 28th).
    Then, we make the parities of each tree. It determines if it is on the odd or even level.
    We use the current parity and then send the opposite parity to the next level in the DFS.
    Finally, we calculate the maximum number of target nodes based on the parity of each node.
    The amount of 'even' parity nodes is the same as the amount of nodes in Tree 1 with the same parity.
    Then, it is added to the best possible solution from Tree 2, since we can determine the node connection.
    '''

    def __init__(self):
        super().__init__('Kevin Zhu', 3373, 'Hard')

    def maxTargetNodes(self, edges1, edges2):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-ii/?envType=daily-question&envId=2025-05-29

        :type edges1: List[List[int]]
        :type edges2: List[List[int]]
        :rtype: List[int]
        '''

        def build_graph(edges, n):
            graph = [[] for _ in range(n)]
            for u, v in edges:
                graph[u].append(v)
                graph[v].append(u)

            return graph

        def dfs(graph, node, parent, parity, is_even):
            count = 1 if is_even else 0
            parity[node] = is_even

            for neighbor in graph[node]:
                if neighbor != parent:
                    count += dfs(graph, neighbor, node, parity, not is_even)

            return count

        n1 = len(edges1) + 1
        n2 = len(edges2) + 1

        graph1 = build_graph(edges1, n1)
        graph2 = build_graph(edges2, n2)

        parity1 = [False] * n1
        parity2 = [False] * n2

        even_count1 = dfs(graph1, 0, -1, parity1, True)
        even_count2 = dfs(graph2, 0, -1, parity2, True)

        odd_count1 = n1 - even_count1
        odd_count2 = n2 - even_count2

        result = []
        best = max(even_count2, odd_count2)

        for i in range(n1):
            if parity1[i]:
                result.append(even_count1 + best)

            else:
                result.append(odd_count1 + best)

        return result

    main = maxTargetNodes
