#!/usr/bin/env python3
"""Grind 75, wave 3: the first real medium block.

Positions 26-37. The two design problems in the range are skipped -- Clone
Graph at 32 and Implement Trie at 35 -- which leaves ten.

This is where the matrix contract stops being a curiosity and starts doing
work: five of the ten take a matrix or return one, and two more take a tree
and return a matrix of rows, which is the first time a tree question has to
answer in something other than a tree.

Two questions needed a decision rather than a transcription.

Binary Tree Level Order Traversal returns a list of lists, so its answer is a
matrix. A matrix is a list of equal-length rows in this project, and a level's
rows are equal-length by construction -- that is what a level *is* -- so the
contract fits exactly rather than approximately.

Evaluate Reverse Polish Notation takes its tokens as a list of strings, and
the difference between that and a list of numbers is not cosmetic: a token is
either an operator or a number, and deciding which is the first line of the
solution. It is declared `stri` rather than left as `array`, which is the
distinction the harness needs in order to write `vector<string>` instead of
guessing.
"""

from __future__ import annotations

from grind75_common import (ALGO, ARR, BOOL, DP, INT, LC, LIST, MATRIX, MATRIX_NOTE, SEARCH, SM,
                            STRETCH, STR, STRI, TREE, TREE_NOTE, c, q, S)

QUESTIONS = [
    q("g-insert-interval", "Insert Interval", STRETCH, [ALGO, "matrix"], "InsertInterval",
      "Have the function InsertInterval(intervals, newInterval) take a list of "
      "intervals sorted from smallest to largest and never overlapping, plus a "
      "second matrix holding just the one new interval, and return the first "
      "matrix with that interval added, still sorted and still with no two "
      "entries overlapping.\n\n" + MATRIX_NOTE +
      "\n\nThe new interval arrives as a matrix of one row rather than as a bare "
      "pair, because a pair is not one of the contract types: its start and end "
      "are the two numbers in that row."
      "\n\nAn interval that only touches another one -- [1, 2] and [2, 3] -- counts "
      "as overlapping, because they share the point 2.\n\nThe input is already "
      "sorted, so this is a single pass with three phases: everything before the "
      "new interval goes out untouched, everything that overlaps it is folded "
      "into it to widen it, and everything after goes out untouched. Sorting a "
      "second time would also work and would be the wrong lesson.",
      (["intervals", "newInterval"], [MATRIX, MATRIX]),
      [c([[[1, 3], [6, 9]], [[2, 5]]], [[1, 5], [6, 9]], MATRIX),
       c([[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [[4, 8]]],
         [[1, 2], [3, 10], [12, 16]], MATRIX),
       c([[[1, 2], [2, 3], [3, 4], [5, 6]], [[2, 4]]], [[1, 4], [5, 6]], MATRIX),
       c([[], [[5, 7]]], [[5, 7]], MATRIX),
       c([[[1, 5]], [[6, 8]]], [[1, 5], [6, 8]], MATRIX),
       c([[[1, 5]], [[0, 0]]], [[0, 0], [1, 5]], MATRIX)],
      S('''def InsertInterval(intervals, newInterval):
    out = []
    i = 0
    start, end = newInterval[0][0], newInterval[0][1]
    n = len(intervals)
    while i < n and intervals[i][1] < start:
        out.append(list(intervals[i]))
        i += 1
    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    out.append([start, end])
    while i < n:
        out.append(list(intervals[i]))
        i += 1
    return out
''',
        """
vector<vector<int>> InsertInterval(const vector<vector<int>>& intervals,
                                   const vector<vector<int>>& newInterval) {
  vector<vector<int>> out;
  size_t i = 0, n = intervals.size();
  int start = newInterval[0][0], end = newInterval[0][1];
  while (i < n && intervals[i][1] < start) out.push_back(intervals[i++]);
  while (i < n && intervals[i][0] <= end) {
    start = min(start, intervals[i][0]);
    end = max(end, intervals[i][1]);
    ++i;
  }
  out.push_back({start, end});
  while (i < n) out.push_back(intervals[i++]);
  return out;
}
""",
        """
public class Solution
{
    public static int[][] InsertInterval(int[][] intervals, int[][] newInterval)
    {
        var outp = new System.Collections.Generic.List<int[]>();
        int i = 0, n = intervals.Length;
        int start = newInterval[0][0], end = newInterval[0][1];
        while (i < n && intervals[i][1] < start)
        {
            outp.Add(new[] { intervals[i][0], intervals[i][1] });
            i++;
        }
        while (i < n && intervals[i][0] <= end)
        {
            start = Math.Min(start, intervals[i][0]);
            end = Math.Max(end, intervals[i][1]);
            i++;
        }
        outp.Add(new[] { start, end });
        while (i < n)
        {
            outp.Add(new[] { intervals[i][0], intervals[i][1] });
            i++;
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[][] insertInterval(int[][] intervals, int[][] newInterval) {
        java.util.List<int[]> out = new java.util.ArrayList<>();
        int i = 0, n = intervals.length;
        int start = newInterval[0][0], end = newInterval[0][1];
        while (i < n && intervals[i][1] < start) {
            out.add(new int[] { intervals[i][0], intervals[i][1] });
            i++;
        }
        while (i < n && intervals[i][0] <= end) {
            start = Math.min(start, intervals[i][0]);
            end = Math.max(end, intervals[i][1]);
            i++;
        }
        out.add(new int[] { start, end });
        while (i < n) {
            out.add(new int[] { intervals[i][0], intervals[i][1] });
            i++;
        }
        return out.toArray(new int[0][]);
    }
}
"""),
      position=26, source=LC, sourceId=57,
      sourceNote="LeetCode 57 (Medium). Three phases in one pass, and the overlap test is <= rather than <."),

    q("g-zero-one-matrix", "01 Matrix", STRETCH, [ALGO, "matrix", SEARCH], "ZeroOneMatrix",
      "Have the function ZeroOneMatrix(matrix) take a grid of 0s and 1s and return a "
      "grid of the same shape holding, for each cell, the distance to the nearest 0 "
      "measured in four-directional steps. The grid always contains at least one "
      "0, so every cell has an answer.\n\n" + MATRIX_NOTE +
      "\n\nSearching outwards separately from each 0 would repeat the same work over "
      "and over. Starting one search from every 0 at the same time visits each cell "
      "once, and the first time a cell is reached it has been reached the short way.",
      (["matrix"], [MATRIX]),
      [c([[[0, 0, 0], [0, 1, 0], [1, 1, 1]]], [[0, 0, 0], [0, 1, 0], [1, 2, 1]], MATRIX),
       c([[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[0, 0, 0], [0, 1, 0], [0, 0, 0]], MATRIX),
       c([[[0, 0, 0], [1, 1, 1], [1, 1, 1]]], [[0, 0, 0], [1, 1, 1], [2, 2, 2]], MATRIX),
       c([[[0]]], [[0]], MATRIX),
       c([[[0, 1], [1, 1]]], [[0, 1], [1, 2]], MATRIX),
       c([[[0, 1, 0, 1], [1, 0, 1, 0]]], [[0, 1, 0, 1], [1, 0, 1, 0]], MATRIX)],
      S('''def ZeroOneMatrix(matrix):
    if not matrix or not matrix[0]:
        return matrix
    rows, columns = len(matrix), len(matrix[0])
    distance = [[-1] * columns for _ in range(rows)]
    queue = []
    for row in range(rows):
        for column in range(columns):
            if matrix[row][column] == 0:
                distance[row][column] = 0
                queue.append((row, column))
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
    while queue:
        row, column = queue.pop(0)
        for row_step, column_step in steps:
            next_row, next_column = row + row_step, column + column_step
            if not (0 <= next_row < rows and 0 <= next_column < columns):
                continue
            if distance[next_row][next_column] != -1:
                continue
            distance[next_row][next_column] = distance[row][column] + 1
            queue.append((next_row, next_column))
    return distance
''',
        """
vector<vector<int>> ZeroOneMatrix(const vector<vector<int>>& matrix) {
  if (matrix.empty() || matrix[0].empty()) return matrix;
  int rows = (int)matrix.size(), columns = (int)matrix[0].size();
  vector<vector<int>> distance(rows, vector<int>(columns, -1));
  queue<pair<int, int>> pending;
  for (int row = 0; row < rows; ++row)
    for (int column = 0; column < columns; ++column)
      if (matrix[row][column] == 0) {
        distance[row][column] = 0;
        pending.push({row, column});
      }
  const int steps[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
  while (!pending.empty()) {
    pair<int, int> here = pending.front();
    pending.pop();
    for (int k = 0; k < 4; ++k) {
      int next_row = here.first + steps[k][0], next_column = here.second + steps[k][1];
      if (next_row < 0 || next_row >= rows || next_column < 0 || next_column >= columns)
        continue;
      if (distance[next_row][next_column] != -1) continue;
      distance[next_row][next_column] = distance[here.first][here.second] + 1;
      pending.push({next_row, next_column});
    }
  }
  return distance;
}
""",
        """
public class Solution
{
    public static int[][] ZeroOneMatrix(int[][] matrix)
    {
        if (matrix.Length == 0 || matrix[0].Length == 0) return matrix;
        int rows = matrix.Length, columns = matrix[0].Length;
        var distance = new int[rows][];
        for (int row = 0; row < rows; row++)
        {
            distance[row] = new int[columns];
            for (int column = 0; column < columns; column++) distance[row][column] = -1;
        }
        var pending = new System.Collections.Generic.Queue<int[]>();
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++)
                if (matrix[row][column] == 0)
                {
                    distance[row][column] = 0;
                    pending.Enqueue(new[] { row, column });
                }
        int[][] steps = { new[] { 1, 0 }, new[] { -1, 0 }, new[] { 0, 1 }, new[] { 0, -1 } };
        while (pending.Count > 0)
        {
            int[] here = pending.Dequeue();
            foreach (int[] step in steps)
            {
                int nextRow = here[0] + step[0], nextColumn = here[1] + step[1];
                if (nextRow < 0 || nextRow >= rows || nextColumn < 0 || nextColumn >= columns)
                    continue;
                if (distance[nextRow][nextColumn] != -1) continue;
                distance[nextRow][nextColumn] = distance[here[0]][here[1]] + 1;
                pending.Enqueue(new[] { nextRow, nextColumn });
            }
        }
        return distance;
    }
}
""",
        """
public class Solution {
    public static int[][] zeroOneMatrix(int[][] matrix) {
        if (matrix.length == 0 || matrix[0].length == 0) return matrix;
        int rows = matrix.length, columns = matrix[0].length;
        int[][] distance = new int[rows][];
        for (int row = 0; row < rows; row++) {
            distance[row] = new int[columns];
            java.util.Arrays.fill(distance[row], -1);
        }
        java.util.ArrayDeque<int[]> pending = new java.util.ArrayDeque<>();
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++)
                if (matrix[row][column] == 0) {
                    distance[row][column] = 0;
                    pending.add(new int[] { row, column });
                }
        int[][] steps = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } };
        while (!pending.isEmpty()) {
            int[] here = pending.poll();
            for (int[] step : steps) {
                int nextRow = here[0] + step[0], nextColumn = here[1] + step[1];
                if (nextRow < 0 || nextRow >= rows || nextColumn < 0 || nextColumn >= columns)
                    continue;
                if (distance[nextRow][nextColumn] != -1) continue;
                distance[nextRow][nextColumn] = distance[here[0]][here[1]] + 1;
                pending.add(new int[] { nextRow, nextColumn });
            }
        }
        return distance;
    }
}
"""),
      position=27, source=LC, sourceId=542,
      sourceNote="LeetCode 542 (Medium). Multi-source BFS: seed the queue with every 0 and never look for them again."),

    q("g-k-closest-points", "K Closest Points to Origin", STRETCH, [ALGO, "matrix", SEARCH],
      "KClosestPointsToOrigin",
      "Have the function KClosestPointsToOrigin(points, k) take a list of points, each "
      "a pair of integers, and return the k of them closest to the origin, ordered "
      "from nearest to furthest.\n\n" + MATRIX_NOTE +
      "\n\nThe distance itself is never needed. Comparing the squares gives the same "
      "order and never takes a root, which also means a squared distance can be "
      "enormous without overflowing where a real distance would have run out of "
      "precision.",
      (["points", "k"], [MATRIX, INT]),
      [c([[[1, 3], [-2, 2]], 1], [[-2, 2]], MATRIX),
       c([[[3, 3], [5, -1], [-2, 4]], 2], [[3, 3], [-2, 4]], MATRIX),
       c([[[1, 1]], 1], [[1, 1]], MATRIX),
       c([[[0, 1], [1, 0]], 2], [[0, 1], [1, 0]], MATRIX),
       c([[[1, 0], [0, 1], [-1, 0], [0, -1], [2, 2]], 3],
         [[-1, 0], [0, -1], [0, 1]], MATRIX)],
      S('''def KClosestPointsToOrigin(points, k):
    ordered = sorted(points, key=lambda point: (point[0] * point[0] + point[1] * point[1],
                                                 point[0], point[1]))
    return [list(point) for point in ordered[:k]]
''',
        """
vector<vector<int>> KClosestPointsToOrigin(const vector<vector<int>>& points, int k) {
  vector<vector<int>> ordered = points;
  sort(ordered.begin(), ordered.end(), [](const vector<int>& a, const vector<int>& b) {
    long long da = (long long)a[0] * a[0] + (long long)a[1] * a[1];
    long long db = (long long)b[0] * b[0] + (long long)b[1] * b[1];
    if (da != db) return da < db;
    if (a[0] != b[0]) return a[0] < b[0];
    return a[1] < b[1];
  });
  if (k > (int)ordered.size()) k = (int)ordered.size();
  ordered.resize(k);
  return ordered;
}
""",
        """
public class Solution
{
    public static int[][] KClosestPointsToOrigin(int[][] points, int k)
    {
        var ordered = (int[][])points.Clone();
        System.Array.Sort(ordered, (a, b) =>
        {
            long da = (long)a[0] * a[0] + (long)a[1] * a[1];
            long db = (long)b[0] * b[0] + (long)b[1] * b[1];
            if (da != db) return da.CompareTo(db);
            if (a[0] != b[0]) return a[0].CompareTo(b[0]);
            return a[1].CompareTo(b[1]);
        });
        if (k > ordered.Length) k = ordered.Length;
        var result = new int[k][];
        System.Array.Copy(ordered, result, k);
        return result;
    }
}
""",
        """
public class Solution {
    public static int[][] kClosestPointsToOrigin(int[][] points, int k) {
        int[][] ordered = points.clone();
        java.util.Arrays.sort(ordered, (a, b) -> {
            long da = (long) a[0] * a[0] + (long) a[1] * a[1];
            long db = (long) b[0] * b[0] + (long) b[1] * b[1];
            if (da != db) return Long.compare(da, db);
            if (a[0] != b[0]) return Integer.compare(a[0], b[0]);
            return Integer.compare(a[1], b[1]);
        });
        if (k > ordered.length) k = ordered.length;
        int[][] result = new int[k][];
        System.arraycopy(ordered, 0, result, 0, k);
        return result;
    }
}
"""),
      position=28, source=LC, sourceId=973,
      sourceNote="LeetCode 973 (Medium). Sort by squared distance; the tie-break on x then y is there so the answer is a single one rather than a set of valid ones."),

    q("g-longest-unique-substring", "Longest Substring Without Repeating Characters", STRETCH,
      [ALGO, SM, "sliding window"], "LengthOfLongestSubstring",
      "Have the function LengthOfLongestSubstring(s) take a string and return the "
      "length of its longest run of consecutive characters in which no character "
      "appears twice.\n\nA sliding window does it in one pass. The window is the "
      "current run of distinct characters; when a repeat turns up, the left edge "
      "jumps just past the previous sighting of that character rather than back to "
      "the start, which is what keeps the whole thing linear rather than quadratic.",
      (["s"], [STR]),
      [c(["abcabcbb"], 3, INT), c(["bbbbb"], 1, INT), c(["pwwkew"], 3, INT),
       c([""], 0, INT), c(["dvdf"], 3, INT), c(["abba"], 2, INT),
       c(["tmmzuxt"], 5, INT)],
      S('''def LengthOfLongestSubstring(s):
    last_seen = {}
    start = 0
    best = 0
    for index, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            start = last_seen[ch] + 1
        last_seen[ch] = index
        if index - start + 1 > best:
            best = index - start + 1
    return best
''',
        """
int LengthOfLongestSubstring(const string& s) {
  map<char, int> last_seen;
  int start = 0, best = 0;
  for (int index = 0; index < (int)s.size(); ++index) {
    char ch = s[index];
    auto found = last_seen.find(ch);
    if (found != last_seen.end() && found->second >= start) start = found->second + 1;
    last_seen[ch] = index;
    if (index - start + 1 > best) best = index - start + 1;
  }
  return best;
}
""",
        """
public class Solution
{
    public static int LengthOfLongestSubstring(string s)
    {
        var lastSeen = new System.Collections.Generic.Dictionary<char, int>();
        int start = 0, best = 0;
        for (int index = 0; index < s.Length; index++)
        {
            char ch = s[index];
            int seen;
            if (lastSeen.TryGetValue(ch, out seen) && seen >= start) start = seen + 1;
            lastSeen[ch] = index;
            if (index - start + 1 > best) best = index - start + 1;
        }
        return best;
    }
}
""",
        """
public class Solution {
    public static int lengthOfLongestSubstring(String s) {
        java.util.Map<Character, Integer> lastSeen = new java.util.HashMap<>();
        int start = 0, best = 0;
        for (int index = 0; index < s.length(); index++) {
            char ch = s.charAt(index);
            Integer seen = lastSeen.get(ch);
            if (seen != null && seen >= start) start = seen + 1;
            lastSeen.put(ch, index);
            if (index - start + 1 > best) best = index - start + 1;
        }
        return best;
    }
}
"""),
      position=29, source=LC, sourceId=3,
      sourceNote="LeetCode 3 (Medium). The left edge only ever moves right, which is what makes the window linear."),

    q("g-three-sum", "3Sum", STRETCH, [ALGO, "matrix", SEARCH], "ThreeSum",
      "Have the function ThreeSum(nums) take a list of integers and return every "
      "group of three of them, taken from three different positions, that adds up to "
      "zero. Each group comes back as a list of three, and the groups come back "
      "sorted, and within a group the numbers come back from smallest to largest. The "
      "same group must not appear twice, however many ways the list contains it.\n\n"
      + MATRIX_NOTE +
      "\n\nSorting the list once is what makes this tractable. After that, for each "
      "number put one pointer just past it and another at the far end: a sum that is "
      "too small means the left pointer has to move up, a sum that is too large means "
      "the right pointer has to move down, and a sum of zero means both have to move "
      "past the duplicates just found.\n\nSkipping those duplicates is not an "
      "optimisation. Without it the list [0, 0, 0, 0] produces the answer sixteen "
      "times over.",
      (["nums"], [ARR]),
      [c([[-1, 0, 1, 2, -1, -4]], [[-1, -1, 2], [-1, 0, 1]], MATRIX),
       c([[0, 1, 1]], [], MATRIX),
       c([[0, 0, 0]], [[0, 0, 0]], MATRIX),
       c([[0, 0, 0, 0]], [[0, 0, 0]], MATRIX),
       c([[1, 2, -2, -1]], [], MATRIX),
       c([[-2, 0, 1, 1, 2]], [[-2, 0, 2], [-2, 1, 1]], MATRIX),
       c([[-4, -2, -2, -2, 0, 1, 2, 2, 2, 3, 3, 4, 4, 6, 6]],
         [[-4, -2, 6], [-4, 0, 4], [-4, 1, 3], [-4, 2, 2], [-2, -2, 4], [-2, 0, 2]], MATRIX),
       c([[]], [], MATRIX)],
      S('''def ThreeSum(nums):
    ordered = sorted(nums)
    size = len(ordered)
    out = []
    for first in range(size):
        if first > 0 and ordered[first] == ordered[first - 1]:
            continue
        left, right = first + 1, size - 1
        while left < right:
            total = ordered[first] + ordered[left] + ordered[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                out.append([ordered[first], ordered[left], ordered[right]])
                left += 1
                right -= 1
                while left <= right and ordered[left] == ordered[left - 1]:
                    left += 1
                while left <= right and ordered[right] == ordered[right + 1]:
                    right -= 1
    return out
''',
        """
vector<vector<int>> ThreeSum(const vector<int>& nums) {
  vector<int> ordered = nums;
  sort(ordered.begin(), ordered.end());
  int size = (int)ordered.size();
  vector<vector<int>> out;
  for (int first = 0; first < size; ++first) {
    if (first > 0 && ordered[first] == ordered[first - 1]) continue;
    int left = first + 1, right = size - 1;
    while (left < right) {
      int total = ordered[first] + ordered[left] + ordered[right];
      if (total < 0) { ++left; continue; }
      if (total > 0) { --right; continue; }
      out.push_back({ordered[first], ordered[left], ordered[right]});
      ++left;
      --right;
      while (left <= right && ordered[left] == ordered[left - 1]) ++left;
      while (left <= right && ordered[right] == ordered[right + 1]) --right;
    }
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[][] ThreeSum(int[] nums)
    {
        var ordered = new int[nums.Length];
        System.Array.Copy(nums, ordered, nums.Length);
        System.Array.Sort(ordered);
        int size = ordered.Length;
        var outp = new System.Collections.Generic.List<int[]>();
        for (int first = 0; first < size; first++)
        {
            if (first > 0 && ordered[first] == ordered[first - 1]) continue;
            int left = first + 1, right = size - 1;
            while (left < right)
            {
                int total = ordered[first] + ordered[left] + ordered[right];
                if (total < 0) { left++; continue; }
                if (total > 0) { right--; continue; }
                outp.Add(new[] { ordered[first], ordered[left], ordered[right] });
                left++;
                right--;
                while (left <= right && ordered[left] == ordered[left - 1]) left++;
                while (left <= right && ordered[right] == ordered[right + 1]) right--;
            }
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[][] threeSum(int[] nums) {
        int[] ordered = nums.clone();
        java.util.Arrays.sort(ordered);
        int size = ordered.length;
        java.util.List<int[]> out = new java.util.ArrayList<>();
        for (int first = 0; first < size; first++) {
            if (first > 0 && ordered[first] == ordered[first - 1]) continue;
            int left = first + 1, right = size - 1;
            while (left < right) {
                int total = ordered[first] + ordered[left] + ordered[right];
                if (total < 0) { left++; continue; }
                if (total > 0) { right--; continue; }
                out.add(new int[] { ordered[first], ordered[left], ordered[right] });
                left++;
                right--;
                while (left <= right && ordered[left] == ordered[left - 1]) left++;
                while (left <= right && ordered[right] == ordered[right + 1]) right--;
            }
        }
        return out.toArray(new int[0][]);
    }
}
"""),
      position=30, source=LC, sourceId=15,
      sourceNote="LeetCode 15 (Medium). The first question on the list whose answer is a matrix while its argument is not, and the duplicate-skipping is the part people leave out."),

    q("g-level-order-traversal", "Binary Tree Level Order Traversal", STRETCH, [ALGO, "tree"],
      "BinaryTreeLevelOrderTraversal",
      "Have the function BinaryTreeLevelOrderTraversal(root) take a binary tree and "
      "return its values one level at a time, from the root down, with each level "
      "read left to right.\n\n" + TREE_NOTE +
      "\n\nThe answer is a list of lists, and that is not a formality: a node with "
      "three children is impossible, but a node with one child belongs to a level of "
      "two, and the level is still a row in the answer with a null-shaped gap in it. "
      "What each row means is fixed -- every row is exactly the nodes at one depth, "
      "in order.\n\nNothing here needs the tree's own shape to be preserved, only its "
      "values, which makes this the first question where reading the heap-indexed "
      "form level by level is easier than recursing.",
      (["root"], [TREE]),
      [c([[3, 9, 20, None, None, 15, 7]], [[3], [9, 20], [15, 7]], MATRIX),
       c([[1]], [[1]], MATRIX),
       c([[]], [], MATRIX),
       c([[1, None, 2, None, None, None, 3]], [[1], [2], [3]], MATRIX),
       c([[1, 2, 3, 4, 5]], [[1], [2, 3], [4, 5]], MATRIX),
       c([[5, 4, 7, 3, None, 6, None, None, None, None, None, None, 2]],
         [[5], [4, 7], [3, 6], [2]], MATRIX)],
      S('''def BinaryTreeLevelOrderTraversal(root):
    out = []
    if not root:
        return out
    level = [0]
    while level:
        values = []
        next_level = []
        for node in level:
            if node < len(root) and root[node] is not None:
                values.append(root[node])
                next_level.append(2 * node + 1)
                next_level.append(2 * node + 2)
        if not values:
            break
        out.append(values)
        level = next_level
    return out
''',
        """
vector<vector<int>> BinaryTreeLevelOrderTraversal(const vector<optional<int>>& root) {
  vector<vector<int>> out;
  if (root.empty()) return out;
  vector<size_t> level{0};
  while (!level.empty()) {
    vector<int> values;
    vector<size_t> next_level;
    for (size_t node : level) {
      if (node >= root.size() || !root[node].has_value()) continue;
      values.push_back(*root[node]);
      next_level.push_back(2 * node + 1);
      next_level.push_back(2 * node + 2);
    }
    if (values.empty()) break;
    out.push_back(values);
    level = next_level;
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[][] BinaryTreeLevelOrderTraversal(int?[] root)
    {
        var outp = new System.Collections.Generic.List<int[]>();
        if (root.Length == 0) return outp.ToArray();
        var level = new System.Collections.Generic.List<int> { 0 };
        while (level.Count > 0)
        {
            var values = new System.Collections.Generic.List<int>();
            var nextLevel = new System.Collections.Generic.List<int>();
            foreach (int node in level)
            {
                if (node >= root.Length || !root[node].HasValue) continue;
                values.Add(root[node].Value);
                nextLevel.Add(2 * node + 1);
                nextLevel.Add(2 * node + 2);
            }
            if (values.Count == 0) break;
            outp.Add(values.ToArray());
            level = nextLevel;
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[][] binaryTreeLevelOrderTraversal(Integer[] root) {
        java.util.List<int[]> out = new java.util.ArrayList<>();
        if (root.length == 0) return out.toArray(new int[0][]);
        java.util.List<Integer> level = new java.util.ArrayList<>();
        level.add(0);
        while (!level.isEmpty()) {
            java.util.List<Integer> values = new java.util.ArrayList<>();
            java.util.List<Integer> nextLevel = new java.util.ArrayList<>();
            for (int node : level) {
                if (node >= root.length || root[node] == null) continue;
                values.add(root[node]);
                nextLevel.add(2 * node + 1);
                nextLevel.add(2 * node + 2);
            }
            if (values.isEmpty()) break;
            int[] row = new int[values.size()];
            for (int i = 0; i < row.length; i++) row[i] = values.get(i);
            out.add(row);
            level = nextLevel;
        }
        return out.toArray(new int[0][]);
    }
}
"""),
      position=31, source=LC, sourceId=102,
      sourceNote="LeetCode 102 (Medium). A queue, and a tree question whose answer is a matrix rather than a tree."),

    q("g-evaluate-rpn", "Evaluate Reverse Polish Notation", STRETCH, [ALGO, "stack", SM],
      "EvaluateReversePolishNotation",
      "Have the function EvaluateReversePolishNotation(tokens) take the tokens of an "
      "expression written in reverse Polish notation and return its value as a whole "
      "number. The operators are + - * and /, and / discards any remainder rather "
      "than rounding to the nearest whole number, so -7 / 2 is -3 rather than -4.\n\n"
      "Each token is either a number or an operator, and which one it is has to be "
      "decided before anything else happens: a token is an operator only if it is "
      "not a number.\n\nA stack is the whole answer. A number is pushed; an operator "
      "pops two values, applies itself to them, and pushes the result back. Note "
      "which of the two popped values comes off first -- for - and / the order "
      "matters.",
      (["tokens"], [STRI]),
      [c([["2", "1", "+", "3", "*"]], 9, INT),
       c([["4", "13", "5", "/", "+"]], 6, INT),
       c([["10", "6", "9", "3", "+", "-11", "*", "/", "*", "2", "*"]], 0, INT),
       c([["3", "-4", "/"]], 0, INT),
       c([["5"]], 5, INT),
       c([["7", "2", "/"]], 3, INT),
       c([["-7", "2", "/"]], -3, INT),
       c([["1", "2", "3", "*", "+"]], 7, INT)],
      S('''def EvaluateReversePolishNotation(tokens):
    stack = []
    for token in tokens:
        if token not in ("+", "-", "*", "/"):
            stack.append(int(token))
            continue
        right = stack.pop()
        left = stack.pop()
        if token == "+":
            stack.append(left + right)
        elif token == "-":
            stack.append(left - right)
        elif token == "*":
            stack.append(left * right)
        else:
            # Division truncates towards zero, which is not what // does in
            # Python, so the sign is carried by hand.
            magnitude = abs(left) // abs(right)
            stack.append(-magnitude if (left < 0) != (right < 0) else magnitude)
    return stack[0]
''',
        """
int EvaluateReversePolishNotation(const vector<string>& tokens) {
  vector<int> stack;
  for (const string& token : tokens) {
    if (token != "+" && token != "-" && token != "*" && token != "/") {
      stack.push_back(stoi(token));
      continue;
    }
    int right = stack.back();
    stack.pop_back();
    int left = stack.back();
    stack.pop_back();
    if (token == "+") stack.push_back(left + right);
    else if (token == "-") stack.push_back(left - right);
    else if (token == "*") stack.push_back(left * right);
    else stack.push_back(left / right);
  }
  return stack[0];
}
""",
        """
public class Solution
{
    public static int EvaluateReversePolishNotation(string[] tokens)
    {
        var stack = new System.Collections.Generic.Stack<int>();
        foreach (string token in tokens)
        {
            if (token != "+" && token != "-" && token != "*" && token != "/")
            {
                stack.Push(int.Parse(token));
                continue;
            }
            int right = stack.Pop();
            int left = stack.Pop();
            if (token == "+") stack.Push(left + right);
            else if (token == "-") stack.Push(left - right);
            else if (token == "*") stack.Push(left * right);
            else stack.Push(left / right);
        }
        return stack.Peek();
    }
}
""",
        """
public class Solution {
    public static int evaluateReversePolishNotation(String[] tokens) {
        java.util.ArrayDeque<Integer> stack = new java.util.ArrayDeque<>();
        for (String token : tokens) {
            if (!token.equals("+") && !token.equals("-") && !token.equals("*") && !token.equals("/")) {
                stack.push(Integer.parseInt(token));
                continue;
            }
            int right = stack.pop();
            int left = stack.pop();
            if (token.equals("+")) stack.push(left + right);
            else if (token.equals("-")) stack.push(left - right);
            else if (token.equals("*")) stack.push(left * right);
            else stack.push(left / right);
        }
        return stack.peek();
    }
}
"""),
      position=33, source=LC, sourceId=150,
      sourceNote="LeetCode 150 (Medium). The order of the two pops is the only thing easy to get backwards, and the truncation rule is the only thing easy to get language-specific."),

    q("g-course-schedule", "Course Schedule", STRETCH, [ALGO, "graph", SEARCH], "CourseSchedule",
      "Have the function CourseSchedule(courseCount, prerequisites) take the number of "
      "courses and a list of pairs where each pair is a course and one of its "
      "prerequisites, and return the boolean true if all the courses can be taken, "
      "otherwise return false.\n\n" + MATRIX_NOTE +
      "\n\nA pair [a, b] means b must be taken before a, so the dependency runs from "
      "b to a. Courses can be taken if and only if that graph has no cycle, and "
      "there is a cycle exactly when a search started anywhere runs into a course it "
      "is already inside.",
      (["courseCount", "prerequisites"], [INT, MATRIX]),
      [c([2, [[1, 0]]], True, BOOL),
       c([2, [[1, 0], [0, 1]]], False, BOOL),
       c([1, []], True, BOOL),
       c([0, []], True, BOOL),
       c([4, [[1, 0], [2, 1], [3, 2]]], True, BOOL),
       c([3, [[0, 1], [1, 2], [2, 0]]], False, BOOL),
       c([5, [[1, 4], [2, 4], [3, 1], [3, 2]]], True, BOOL)],
      S('''def CourseSchedule(courseCount, prerequisites):
    outgoing = [[] for _ in range(courseCount)]
    for course, needed in prerequisites:
        outgoing[needed].append(course)
    # 0 = not looked at, 1 = on the current path, 2 = finished.
    state = [0] * courseCount
    for start in range(courseCount):
        if state[start] != 0:
            continue
        path = [(start, 0)]
        state[start] = 1
        while path:
            course, edge = path[-1]
            if edge == len(outgoing[course]):
                state[course] = 2
                path.pop()
                continue
            path[-1] = (course, edge + 1)
            nxt = outgoing[course][edge]
            if state[nxt] == 1:
                return False
            if state[nxt] == 0:
                state[nxt] = 1
                path.append((nxt, 0))
    return True
''',
        """
bool CourseSchedule(int courseCount, const vector<vector<int>>& prerequisites) {
  vector<vector<int>> outgoing(courseCount);
  for (const auto& pair : prerequisites) outgoing[pair[1]].push_back(pair[0]);
  // 0 = not looked at, 1 = on the current path, 2 = finished.
  vector<int> state(courseCount, 0);
  for (int start = 0; start < courseCount; ++start) {
    if (state[start] != 0) continue;
    vector<pair<int, int>> path{{start, 0}};
    state[start] = 1;
    while (!path.empty()) {
      int course = path.back().first, edge = path.back().second;
      if (edge == (int)outgoing[course].size()) {
        state[course] = 2;
        path.pop_back();
        continue;
      }
      path.back().second = edge + 1;
      int nxt = outgoing[course][edge];
      if (state[nxt] == 1) return false;
      if (state[nxt] == 0) {
        state[nxt] = 1;
        path.push_back({nxt, 0});
      }
    }
  }
  return true;
}
""",
        """
public class Solution
{
    public static bool CourseSchedule(int courseCount, int[][] prerequisites)
    {
        var outgoing = new System.Collections.Generic.List<int>[courseCount];
        for (int i = 0; i < courseCount; i++) outgoing[i] = new System.Collections.Generic.List<int>();
        foreach (int[] pair in prerequisites) outgoing[pair[1]].Add(pair[0]);
        // 0 = not looked at, 1 = on the current path, 2 = finished.
        var state = new int[courseCount];
        var path = new System.Collections.Generic.List<int[]>();
        for (int start = 0; start < courseCount; start++)
        {
            if (state[start] != 0) continue;
            path.Clear();
            path.Add(new[] { start, 0 });
            state[start] = 1;
            while (path.Count > 0)
            {
                int course = path[path.Count - 1][0], edge = path[path.Count - 1][1];
                if (edge == outgoing[course].Count)
                {
                    state[course] = 2;
                    path.RemoveAt(path.Count - 1);
                    continue;
                }
                path[path.Count - 1][1] = edge + 1;
                int nxt = outgoing[course][edge];
                if (state[nxt] == 1) return false;
                if (state[nxt] == 0)
                {
                    state[nxt] = 1;
                    path.Add(new[] { nxt, 0 });
                }
            }
        }
        return true;
    }
}
""",
        """
public class Solution {
    public static boolean courseSchedule(int courseCount, int[][] prerequisites) {
        java.util.List<java.util.List<Integer>> outgoing = new java.util.ArrayList<>();
        for (int i = 0; i < courseCount; i++) outgoing.add(new java.util.ArrayList<Integer>());
        for (int[] pair : prerequisites) outgoing.get(pair[1]).add(pair[0]);
        // 0 = not looked at, 1 = on the current path, 2 = finished.
        int[] state = new int[courseCount];
        java.util.List<int[]> path = new java.util.ArrayList<>();
        for (int start = 0; start < courseCount; start++) {
            if (state[start] != 0) continue;
            path.clear();
            path.add(new int[] { start, 0 });
            state[start] = 1;
            while (!path.isEmpty()) {
                int course = path.get(path.size() - 1)[0];
                int edge = path.get(path.size() - 1)[1];
                if (edge == outgoing.get(course).size()) {
                    state[course] = 2;
                    path.remove(path.size() - 1);
                    continue;
                }
                path.get(path.size() - 1)[1] = edge + 1;
                int nxt = outgoing.get(course).get(edge);
                if (state[nxt] == 1) return false;
                if (state[nxt] == 0) {
                    state[nxt] = 1;
                    path.add(new int[] { nxt, 0 });
                }
            }
        }
        return true;
    }
}
"""),
      position=34, source=LC, sourceId=207,
      sourceNote="LeetCode 207 (Medium). Three states, not two: without the 'on the current path' state a node reached twice from different branches looks like a cycle when it is not."),

    q("g-coin-change", "Coin Change", STRETCH, [ALGO, DP], "CoinChange",
      "Have the function CoinChange(coins, amount) take a list of coin values and a "
      "target amount, and return the fewest coins that add up to exactly that amount, "
      "or -1 if no combination does.\n\nAsking for the fewest rather than any way to "
      "make it is what makes this a table rather than a search: once the best answer "
      "for every amount up to the target is known, the answer for the target is the "
      "best of one coin plus the answer for what is left over.\n\nThe order of the "
      "table matters. Every entry it reads has to be one already filled in, so the "
      "amounts go in increasing order.",
      (["coins", "amount"], [ARR, INT]),
      [c([[1, 2, 5], 11], 3, INT), c([[2], 3], -1, INT), c([[1], 0], 0, INT),
       c([[], 0], 0, INT), c([[], 7], -1, INT), c([[1], 2], 2, INT),
       c([[2, 5, 10, 1], 27], 4, INT), c([[1, 5, 10, 25], 30], 2, INT),
       c([[186, 419, 83, 408], 6249], 20, INT)],
      S('''def CoinChange(coins, amount):
    unreachable = amount + 1
    best = [0] + [unreachable] * amount
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and best[value - coin] + 1 < best[value]:
                best[value] = best[value - coin] + 1
    return -1 if best[amount] > amount else best[amount]
''',
        """
int CoinChange(const vector<int>& coins, int amount) {
  int unreachable = amount + 1;
  vector<int> best(amount + 1, unreachable);
  best[0] = 0;
  for (int value = 1; value <= amount; ++value)
    for (int coin : coins)
      if (coin <= value && best[value - coin] + 1 < best[value])
        best[value] = best[value - coin] + 1;
  return best[amount] > amount ? -1 : best[amount];
}
""",
        """
public class Solution
{
    public static int CoinChange(int[] coins, int amount)
    {
        int unreachable = amount + 1;
        var best = new int[amount + 1];
        for (int i = 0; i <= amount; i++) best[i] = unreachable;
        best[0] = 0;
        for (int value = 1; value <= amount; value++)
            foreach (int coin in coins)
                if (coin <= value && best[value - coin] + 1 < best[value])
                    best[value] = best[value - coin] + 1;
        return best[amount] > amount ? -1 : best[amount];
    }
}
""",
        """
public class Solution {
    public static int coinChange(int[] coins, int amount) {
        int unreachable = amount + 1;
        int[] best = new int[amount + 1];
        java.util.Arrays.fill(best, unreachable);
        best[0] = 0;
        for (int value = 1; value <= amount; value++)
            for (int coin : coins)
                if (coin <= value && best[value - coin] + 1 < best[value])
                    best[value] = best[value - coin] + 1;
        return best[amount] > amount ? -1 : best[amount];
    }
}
"""),
      position=36, source=LC, sourceId=322,
      sourceNote="LeetCode 322 (Medium). The first table-driven question on the list, and the reason the amounts go in increasing order rather than the coins."),

    q("g-product-except-self", "Product of Array Except Self", STRETCH, [ALGO, "array"],
      "ProductOfArrayExceptSelf",
      "Have the function ProductOfArrayExceptSelf(nums) take a list of integers and "
      "return a list of the same length where entry i holds the product of every "
      "value in nums except the one at index i. Neither division nor a prefix and a "
      "suffix array are allowed, because the question is what to do when a value is "
      "0 and division by it is not an option.\n\nEverything at index i is the "
      "product of what is before it times the product of what is after it, and both "
      "halves can be swept in turn, carrying the running product along.",
      (["nums"], [ARR]),
      [c([[1, 2, 3, 4]], [24, 12, 8, 6], ARR),
       c([[-1, 1, 0, -3, 3]], [0, 0, 9, 0, 0], ARR),
       c([[0, 0]], [0, 0], ARR),
       c([[1, 1]], [1, 1], ARR),
       c([[1, 2, 0, 4]], [0, 0, 8, 0], ARR),
       c([[3, 5, 2, 4]], [40, 24, 60, 30], ARR),
       c([[1]], [1], ARR),
       c([[2, 3]], [3, 2], ARR)],
      S('''def ProductOfArrayExceptSelf(nums):
    size = len(nums)
    out = [1] * size
    running = 1
    for index in range(size):
        out[index] = running
        running *= nums[index]
    running = 1
    for index in range(size - 1, -1, -1):
        out[index] *= running
        running *= nums[index]
    return out
''',
        """
vector<int> ProductOfArrayExceptSelf(const vector<int>& nums) {
  int size = (int)nums.size();
  vector<int> out(size, 1);
  long long running = 1;
  for (int index = 0; index < size; ++index) {
    out[index] = (int)running;
    running *= nums[index];
  }
  running = 1;
  for (int index = size - 1; index >= 0; --index) {
    out[index] = (int)(out[index] * running);
    running *= nums[index];
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[] ProductOfArrayExceptSelf(int[] nums)
    {
        int size = nums.Length;
        var outp = new int[size];
        long running = 1;
        for (int index = 0; index < size; index++)
        {
            outp[index] = (int)running;
            running *= nums[index];
        }
        running = 1;
        for (int index = size - 1; index >= 0; index--)
        {
            outp[index] = (int)(outp[index] * running);
            running *= nums[index];
        }
        return outp;
    }
}
""",
        """
public class Solution {
    public static int[] productOfArrayExceptSelf(int[] nums) {
        int size = nums.length;
        int[] out = new int[size];
        long running = 1;
        for (int index = 0; index < size; index++) {
            out[index] = (int) running;
            running *= nums[index];
        }
        running = 1;
        for (int index = size - 1; index >= 0; index--) {
            out[index] = (int) (out[index] * running);
            running *= nums[index];
        }
        return out;
    }
}
"""),
      position=37, source=LC, sourceId=238,
      sourceNote="LeetCode 238 (Medium). A zero in the list is the reason the question forbids division: a prefix and suffix sweep produces the right answer anyway."),
]
