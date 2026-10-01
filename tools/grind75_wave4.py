#!/usr/bin/env python3
"""Grind 75, wave 4: positions 38-49.

The two design problems in the range are skipped -- Min Stack at 38 and Time
Based Key-Value Store at 47 -- which leaves ten.

Every expectation in this file came out of `tools/_ref_wave4.py` rather than
from memory. Wave 3 was written from recall and seven of the twenty or so
answers were wrong, which cost more time than computing them would have. The
reference file also caught a real error before it reached a language: the
Lowest Common Ancestor question is the general binary tree, not the BST, and
the walk that solves LeetCode 235 gives the wrong answer here.

Two questions in this wave earn a contract type each.

Accounts Merge is the reason `strmatrix` exists. Its answer is a list of lists
of names, which is neither a matrix (the cells are strings) nor a charmatrix
(the cells are words, not single characters), so the type was added rather than
the question rewritten to fit something that already existed.

Number of Islands takes a grid of single characters, which is a charmatrix --
the first practice question to take one. It returns an int, so it does not need
the string-rows emitter on the way out; Accounts Merge does.

Lowest Common Ancestor of a Binary Tree deliberately sits right after the
Binary Search Tree question from wave 1, because the difference between the
two is the lesson. A BST node tells you which way to walk. A general tree node
tells you nothing, so both branches have to be searched, and the answer is the
first node whose two subtrees each contain one of the two values.
"""

from __future__ import annotations

from grind75_common import (ALGO, ARR, BOOL, CHARMATRIX, DP, INT, LC, LIST, MATRIX,
                            MATRIX_NOTE, SEARCH, SM, STRETCH, STR, STRMATRIX, TREE,
                            TREE_NOTE, c, q, S)

QUESTIONS = [
    q("g-validate-bst", "Validate Binary Search Tree", STRETCH, [ALGO, "tree"],
      "IsValidBst",
      "Have the function IsValidBst(root) take a binary tree and return the boolean "
      "true if it is a valid binary search tree, otherwise return false. A binary "
      "search tree is one where, for every node, every value in its left subtree is "
      "strictly smaller than the node's own value and every value in its right "
      "subtree is strictly larger.\n\n" + TREE_NOTE +
      "\n\nThe rule is about whole subtrees, not about a node and its immediate "
      "children. A node whose left child is smaller and whose right child is larger "
      "is still invalid if something smaller than the node is hiding further down "
      "the right side. So what travels down the tree is a range, and each node "
      "narrows it.\n\nThe empty tree is valid.",
      (["root"], [TREE]),
      [c([[2, 1, 3]], True, BOOL),
       c([[5, 1, 4, None, None, 3, 6]], False, BOOL),
       c([[10, 5, 15, None, None, 6, 20]], False, BOOL),
       c([[2, 2, 2]], False, BOOL),
       c([[3, 1, 5, None, None, 2, 4]], False, BOOL),
       c([[1]], True, BOOL),
       c([[]], True, BOOL)],
      S('''def IsValidBst(root):
    def walk(node, low, high):
        if node >= len(root) or root[node] is None:
            return True
        value = root[node]
        if not low < value < high:
            return False
        return (walk(2 * node + 1, low, value)
                and walk(2 * node + 2, value, high))
    return walk(0, float("-inf"), float("inf"))
''',
        """
bool IsValidBst(const vector<optional<int>>& root) {
  function<bool(size_t, long long, long long)> walk =
      [&](size_t node, long long low, long long high) -> bool {
    if (node >= root.size() || !root[node].has_value()) return true;
    long long value = *root[node];
    if (value <= low || value >= high) return false;
    return walk(2 * node + 1, low, value) && walk(2 * node + 2, value, high);
  };
  return walk(0, LLONG_MIN, LLONG_MAX);
}
""",
        """
public class Solution
{
    public static bool IsValidBst(int?[] root)
    {
        bool Walk(int node, long low, long high)
        {
            if (node >= root.Length || !root[node].HasValue) return true;
            long value = root[node].Value;
            if (value <= low || value >= high) return false;
            return Walk(2 * node + 1, low, value) && Walk(2 * node + 2, value, high);
        }
        return Walk(0, long.MinValue, long.MaxValue);
    }
}
""",
        """
public class Solution {
    public static boolean isValidBst(Integer[] root) {
        return walk(root, 0, Long.MIN_VALUE, Long.MAX_VALUE);
    }

    static boolean walk(Integer[] root, int node, long low, long high) {
        if (node >= root.length || root[node] == null) return true;
        long value = root[node];
        if (value <= low || value >= high) return false;
        return walk(root, 2 * node + 1, low, value)
            && walk(root, 2 * node + 2, value, high);
    }
}
"""),
      position=39, source=LC, sourceId=98,
      sourceNote="LeetCode 98 (Medium). A range travels down with the search, and each node narrows it. Checking only a node against its own children passes the first case and fails the third."),

    q("g-number-of-islands", "Number of Islands", STRETCH, [ALGO, "matrix", SEARCH],
      "NumberOfIslands",
      "Have the function NumberOfIslands(grid) take a grid in which each cell "
      "is the character 1 or the character 0, and return the number of separate "
      "groups of 1 cells, where two cells are in the same group if they can be "
      "reached from one another by moving up, down, left or right through 1 "
      "cells.\n\n" + MATRIX_NOTE +
      "\n\nDiagonals do not count, which is the detail that catches people.\n\n"
      "Sweep the grid. Each time you meet a 1 that is still standing, that is the "
      "start of a new island, so count it and then sink the whole thing so the "
      "sweep cannot count it again. Sinking by marking as you go is what keeps it "
      "linear; a set of already-visited cells also works and is easier to get "
      "right.",
      (["grid"], [CHARMATRIX]),
      [c([[["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"],
          ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]]], 3, INT),
       c([[["1", "1", "0"], ["0", "1", "0"], ["0", "0", "1"]]], 2, INT),
       c([[["0", "0"], ["0", "0"]]], 0, INT),
       c([[["1"]]], 1, INT),
       # Every 1 here touches another 1 only at a corner, so each is its own
       # island. Reading the diagonals as connected gives 2 and is the mistake
       # this question exists to catch.
       c([[["1", "0", "1", "0", "1"],
           ["0", "1", "0", "1", "0"],
           ["1", "0", "1", "0", "1"]]], 8, INT),
       c([[["0", "1", "0"], ["1", "0", "1"], ["0", "1", "0"]]], 4, INT)],
      S('''def NumberOfIslands(grid):
    if not grid or not grid[0]:
        return 0
    rows, columns = len(grid), len(grid[0])

    def sink(row, column):
        if not (0 <= row < rows and 0 <= column < columns):
            return
        if grid[row][column] != "1":
            return
        grid[row][column] = "0"
        sink(row + 1, column)
        sink(row - 1, column)
        sink(row, column + 1)
        sink(row, column - 1)

    islands = 0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] == "1":
                islands += 1
                sink(row, column)
    return islands
''',
        """
int NumberOfIslands(vector<vector<string>> grid) {
  if (grid.empty() || grid[0].empty()) return 0;
  int rows = (int)grid.size(), columns = (int)grid[0].size();
  function<void(int, int)> sink = [&](int row, int column) {
    if (row < 0 || row >= rows || column < 0 || column >= columns) return;
    if (grid[row][column] != "1") return;
    grid[row][column] = "0";
    sink(row + 1, column);
    sink(row - 1, column);
    sink(row, column + 1);
    sink(row, column - 1);
  };
  int islands = 0;
  for (int row = 0; row < rows; ++row)
    for (int column = 0; column < columns; ++column)
      if (grid[row][column] == "1") { ++islands; sink(row, column); }
  return islands;
}
""",
        """
public class Solution
{
    public static int NumberOfIslands(string[][] grid)
    {
        if (grid.Length == 0 || grid[0].Length == 0) return 0;
        int rows = grid.Length, columns = grid[0].Length;
        System.Action<int, int> sink = null;
        sink = (row, column) =>
        {
            if (row < 0 || row >= rows || column < 0 || column >= columns) return;
            if (grid[row][column] != "1") return;
            grid[row][column] = "0";
            sink(row + 1, column);
            sink(row - 1, column);
            sink(row, column + 1);
            sink(row, column - 1);
        };
        int islands = 0;
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++)
                if (grid[row][column] == "1") { islands++; sink(row, column); }
        return islands;
    }
}
""",
        """
public class Solution {
    public static int numberOfIslands(String[][] grid) {
        if (grid.length == 0 || grid[0].length == 0) return 0;
        int rows = grid.length, columns = grid[0].length;
        int islands = 0;
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++) {
                if (grid[row][column].equals("1")) {
                    islands++;
                    sink(grid, row, column, rows, columns);
                }
            }
        return islands;
    }

    static void sink(String[][] grid, int row, int column, int rows, int columns) {
        if (row < 0 || row >= rows || column < 0 || column >= columns) return;
        if (!grid[row][column].equals("1")) return;
        grid[row][column] = "0";
        sink(grid, row + 1, column, rows, columns);
        sink(grid, row - 1, column, rows, columns);
        sink(grid, row, column + 1, rows, columns);
        sink(grid, row, column - 1, rows, columns);
    }
}
"""),
      position=40, source=LC, sourceId=200,
      sourceNote="LeetCode 200 (Medium). The first practice question to take a grid of characters, and the diagonal is the trap: four neighbours, not eight."),

    q("g-rotting-oranges", "Rotting Oranges", STRETCH, [ALGO, "matrix"], "RottingOranges",
      "Have the function RottingOranges(grid) take a grid in which each cell is 0 "
      "(an empty cell), 1 (a fresh orange) or 2 (a rotten orange), and return how "
      "many minutes it takes for every orange to rot, or -1 if some never will.\n\n"
      + MATRIX_NOTE +
      "\n\nA rotten orange spoils each of its four neighbours one minute later, and "
      "that spreads until nothing fresh is left. This is a wavefront, so process it "
      "one minute at a time with a queue rather than restarting the spread from each "
      "orange in turn.\n\nThe subtle part is which minute a cell is counted in. Take "
      "the size of the queue before doing any spreading, then spread once for each "
      "cell that was already in it: a cell enqueued partway through this minute does "
      "not get to spread until the next one, which is what makes the count come out "
      "right.\n\nA fresh orange next to nothing rotten never rots, so when the queue "
      "empties with fresh oranges still standing the answer is -1 rather than "
      "whatever has been counted so far.",
      (["grid"], [MATRIX]),
      [c([[[2, 1, 1], [1, 1, 0], [0, 1, 1]]], 4, INT),
       c([[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], -1, INT),
       c([[[0, 2], [1, 1], [1, 0, 1]]], 3, INT),
       c([[[2, 2, 2], [0, 1, 0], [0, 0, 0]]], 1, INT),
       c([[[1, 2], [2, 1]]], 1, INT),
       c([[[1]]], -1, INT),
       c([[[2]]], 0, INT),
       c([[[0, 0]]], 0, INT)],
      S('''def RottingOranges(grid):
    rows = len(grid)
    columns = len(grid[0])
    pending = []
    fresh = 0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] == 2:
                pending.append((row, column))
            elif grid[row][column] == 1:
                fresh += 1
    minutes = 0
    while pending and fresh:
        minutes += 1
        for _ in range(len(pending)):
            row, column = pending.pop(0)
            for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_row, next_column = row + row_step, column + column_step
                if not (0 <= next_row < rows and 0 <= next_column < columns):
                    continue
                if grid[next_row][next_column] == 1:
                    grid[next_row][next_column] = 2
                    fresh -= 1
                    pending.append((next_row, next_column))
    return -1 if fresh else minutes
''',
        """
int RottingOranges(vector<vector<int>> grid) {
  int rows = (int)grid.size(), columns = (int)grid[0].size();
  queue<pair<int, int>> pending;
  int fresh = 0;
  for (int row = 0; row < rows; ++row)
    for (int column = 0; column < columns; ++column) {
      if (grid[row][column] == 2) pending.push({row, column});
      else if (grid[row][column] == 1) ++fresh;
    }
  int minutes = 0;
  const int steps[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
  while (!pending.empty() && fresh > 0) {
    ++minutes;
    // The level is fixed before any spreading: a cell queued during this
    // minute must not spread until the next one.
    size_t level = pending.size();
    for (size_t k = 0; k < level; ++k) {
      pair<int, int> here = pending.front();
      pending.pop();
      for (int s = 0; s < 4; ++s) {
        int next_row = here.first + steps[s][0];
        int next_column = here.second + steps[s][1];
        if (next_row < 0 || next_row >= rows || next_column < 0 || next_column >= columns)
          continue;
        if (grid[next_row][next_column] == 1) {
          grid[next_row][next_column] = 2;
          --fresh;
          pending.push({next_row, next_column});
        }
      }
    }
  }
  return fresh > 0 ? -1 : minutes;
}
""",
        """
public class Solution
{
    public static int RottingOranges(int[][] grid)
    {
        int rows = grid.Length, columns = grid[0].Length;
        var pending = new System.Collections.Generic.Queue<int[]>();
        int fresh = 0;
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++)
            {
                if (grid[row][column] == 2) pending.Enqueue(new[] { row, column });
                else if (grid[row][column] == 1) fresh++;
            }
        int minutes = 0;
        int[][] steps = { new[] { 1, 0 }, new[] { -1, 0 }, new[] { 0, 1 }, new[] { 0, -1 } };
        while (pending.Count > 0 && fresh > 0)
        {
            minutes++;
            int level = pending.Count;
            for (int k = 0; k < level; k++)
            {
                int[] here = pending.Dequeue();
                foreach (int[] step in steps)
                {
                    int nextRow = here[0] + step[0], nextColumn = here[1] + step[1];
                    if (nextRow < 0 || nextRow >= rows || nextColumn < 0 || nextColumn >= columns)
                        continue;
                    if (grid[nextRow][nextColumn] == 1)
                    {
                        grid[nextRow][nextColumn] = 2;
                        fresh--;
                        pending.Enqueue(new[] { nextRow, nextColumn });
                    }
                }
            }
        }
        return fresh > 0 ? -1 : minutes;
    }
}
""",
        """
public class Solution {
    public static int rottingOranges(int[][] grid) {
        int rows = grid.length, columns = grid[0].length;
        java.util.ArrayDeque<int[]> pending = new java.util.ArrayDeque<>();
        int fresh = 0;
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++) {
                if (grid[row][column] == 2) pending.add(new int[] { row, column });
                else if (grid[row][column] == 1) fresh++;
            }
        int minutes = 0;
        int[][] steps = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } };
        while (!pending.isEmpty() && fresh > 0) {
            minutes++;
            int level = pending.size();
            for (int k = 0; k < level; k++) {
                int[] here = pending.poll();
                for (int[] step : steps) {
                    int nextRow = here[0] + step[0], nextColumn = here[1] + step[1];
                    if (nextRow < 0 || nextRow >= rows || nextColumn < 0 || nextColumn >= columns)
                        continue;
                    if (grid[nextRow][nextColumn] == 1) {
                        grid[nextRow][nextColumn] = 2;
                        fresh--;
                        pending.add(new int[] { nextRow, nextColumn });
                    }
                }
            }
        }
        return fresh > 0 ? -1 : minutes;
    }
}
"""),
      position=41, source=LC, sourceId=994,
      sourceNote="LeetCode 994 (Medium). Fixing the level size before spreading is the whole question: a cell that rots this minute must not spread until the next one, or the count comes out one short per round."),

    q("g-search-rotated", "Search in Rotated Sorted Array", STRETCH, [SEARCH, ALGO],
      "SearchInRotatedSortedArray",
      "Have the function SearchInRotatedSortedArray(nums, target) take a list of "
      "distinct integers that was sorted from smallest to largest and then rotated "
      "at some unknown point, and return the index of target in it, or -1 if target "
      "is not there.\n\nBinary search still works, and that is the point of the "
      "question. Look at the middle: one of the two halves around it must be sorted, "
      "and if it is, then either the target is inside that half or it is not, and "
      "which of those is true can be decided by comparing the target against that "
      "half's ends. So each step still throws away half the list.\n\nThe empty list "
      "has no answer, and neither does a target that is not present.",
      (["nums", "target"], [ARR, INT]),
      [c([[4, 5, 6, 7, 0, 1, 2], 0], 4, INT),
       c([[4, 5, 6, 7, 0, 1, 2], 3], -1, INT),
       c([[4, 5, 6, 7, 0, 1, 2], 2], 6, INT),
       c([[1, 3], 3], 1, INT),
       c([[3, 1], 1], 1, INT),
       c([[5, 1, 3], 3], 2, INT),
       c([[1], 0], -1, INT),
       c([[], 5], -1, INT)],
      S('''def SearchInRotatedSortedArray(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return mid
        if nums[low] <= nums[mid]:
            # The left half is in order, so it is the half worth ruling in or out.
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1
''',
        """
int SearchInRotatedSortedArray(const vector<int>& nums, int target) {
  int low = 0, high = (int)nums.size() - 1;
  while (low <= high) {
    int mid = low + (high - low) / 2;
    if (nums[mid] == target) return mid;
    if (nums[low] <= nums[mid]) {
      if (nums[low] <= target && target < nums[mid]) high = mid - 1;
      else low = mid + 1;
    } else {
      if (nums[mid] < target && target <= nums[high]) low = mid + 1;
      else high = mid - 1;
    }
  }
  return -1;
}
""",
        """
public class Solution
{
    public static int SearchInRotatedSortedArray(int[] nums, int target)
    {
        int low = 0, high = nums.Length - 1;
        while (low <= high)
        {
            int mid = low + (high - low) / 2;
            if (nums[mid] == target) return mid;
            if (nums[low] <= nums[mid])
            {
                if (nums[low] <= target && target < nums[mid]) high = mid - 1;
                else low = mid + 1;
            }
            else
            {
                if (nums[mid] < target && target <= nums[high]) low = mid + 1;
                else high = mid - 1;
            }
        }
        return -1;
    }
}
""",
        """
public class Solution {
    public static int searchInRotatedSortedArray(int[] nums, int target) {
        int low = 0, high = nums.length - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (nums[mid] == target) return mid;
            if (nums[low] <= nums[mid]) {
                if (nums[low] <= target && target < nums[mid]) high = mid - 1;
                else low = mid + 1;
            } else {
                if (nums[mid] < target && target <= nums[high]) low = mid + 1;
                else high = mid - 1;
            }
        }
        return -1;
    }
}
"""),
      position=42, source=LC, sourceId=33,
      sourceNote="LeetCode 33 (Medium). The rotation does not break binary search, it only means one half is always in order. Working out which half costs one comparison."),

    q("g-combination-sum", "Combination Sum", STRETCH, [ALGO, "backtracking"],
      "CombinationSum",
      "Have the function CombinationSum(candidates, target) take a list of distinct "
      "positive integers and a target, and return every combination of them that "
      "adds up to exactly the target.\n\n" + MATRIX_NOTE +
      "\n\nEach returned combination is a list of numbers, and it is read as a set "
      "rather than a sequence, so [2, 2, 3] and [3, 2, 2] are the same combination "
      "and only one of them comes back. Every candidate may be used any number of "
      "times, so a sum of zero is the empty combination and it does come back.\n\n"
      "Combinations come back in the order they are found by taking candidates from "
      "smallest to largest, and within a combination the numbers also come back "
      "smallest to largest.",
      (["candidates", "target"], [ARR, INT]),
      [c([[2, 3, 6, 7], 7], [[2, 2, 3], [7]], MATRIX),
       c([[2, 3, 5], 8], [[2, 2, 2, 2], [2, 3, 3], [3, 5]], MATRIX),
       c([[2], 1], [], MATRIX),
       c([[2], 0], [[]], MATRIX),
       c([[1], 1], [[1]], MATRIX),
       c([[], 3], [], MATRIX),
       c([[8, 4], 3], [], MATRIX)],
      S('''def CombinationSum(candidates, target):
    out = []
    ordered = sorted(candidates)

    def build(start, left, current):
        if left == 0:
            out.append(list(current))
            return
        for index in range(start, len(ordered)):
            if ordered[index] > left:
                break
            current.append(ordered[index])
            # The same index again, not the next one: a candidate is reusable.
            build(index, left - ordered[index], current)
            current.pop()

    build(0, target, [])
    return out
''',
        """
vector<vector<int>> CombinationSum(const vector<int>& candidates, int target) {
  vector<int> ordered = candidates;
  sort(ordered.begin(), ordered.end());
  vector<vector<int>> out;
  vector<int> current;
  function<void(size_t, int)> build = [&](size_t start, int left) {
    if (left == 0) { out.push_back(current); return; }
    for (size_t index = start; index < ordered.size(); ++index) {
      if (ordered[index] > left) break;
      current.push_back(ordered[index]);
      build(index, left - ordered[index]);
      current.pop_back();
    }
  };
  build(0, target);
  return out;
}
""",
        """
public class Solution
{
    public static int[][] CombinationSum(int[] candidates, int target)
    {
        var ordered = new int[candidates.Length];
        System.Array.Copy(candidates, ordered, candidates.Length);
        System.Array.Sort(ordered);
        var outp = new System.Collections.Generic.List<int[]>();
        var current = new System.Collections.Generic.List<int>();
        System.Action<int, int> build = null;
        build = (start, left) =>
        {
            if (left == 0) { outp.Add(current.ToArray()); return; }
            for (int index = start; index < ordered.Length; index++)
            {
                if (ordered[index] > left) break;
                current.Add(ordered[index]);
                build(index, left - ordered[index]);
                current.RemoveAt(current.Count - 1);
            }
        };
        build(0, target);
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[][] combinationSum(int[] candidates, int target) {
        int[] ordered = candidates.clone();
        java.util.Arrays.sort(ordered);
        java.util.List<java.util.List<Integer>> out = new java.util.ArrayList<>();
        build(ordered, 0, target, new java.util.ArrayList<Integer>(), out);
        int[][] result = new int[out.size()][];
        for (int i = 0; i < result.length; i++) {
            java.util.List<Integer> combination = out.get(i);
            int[] row = new int[combination.size()];
            for (int j = 0; j < row.length; j++) row[j] = combination.get(j);
            result[i] = row;
        }
        return result;
    }

    static void build(int[] ordered, int start, int left,
                      java.util.List<Integer> current,
                      java.util.List<java.util.List<Integer>> out) {
        if (left == 0) {
            out.add(new java.util.ArrayList<>(current));
            return;
        }
        for (int index = start; index < ordered.length; index++) {
            if (ordered[index] > left) break;
            current.add(ordered[index]);
            // The same index again, not the next one: a candidate is reusable.
            build(ordered, index, left - ordered[index], current, out);
            current.remove(current.size() - 1);
        }
    }
}
"""),
      position=43, source=LC, sourceId=39,
      sourceNote="LeetCode 39 (Medium). Recursing on the same index rather than the next one is what allows a candidate to repeat; recursing on the next index would forbid it and give a different question."),

    q("g-permutations", "Permutations", STRETCH, [ALGO, "backtracking"], "Permute",
      "Have the function Permute(nums) take a list of distinct integers and return "
      "every ordering of them, each ordering as a list of the same length.\n\n"
      + MATRIX_NOTE +
      "\n\nThe orderings come back in the order they are found by always taking the "
      "smallest number still unused first, so the first one is the list as given.\n\n"
      "The empty list has exactly one ordering, which is the empty list.",
      (["nums"], [ARR]),
      [c([[1, 2, 3]], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]], MATRIX),
       c([[1]], [[1]], MATRIX),
       c([[0]], [[0]], MATRIX),
       c([[3, 1]], [[3, 1], [1, 3]], MATRIX),
       c([[]], [[]], MATRIX)],
      S('''def Permute(nums):
    out = []

    def build(current, rest):
        if not rest:
            out.append(list(current))
            return
        for index in range(len(rest)):
            build(current + [rest[index]], rest[:index] + rest[index + 1:])

    build([], list(nums))
    return out
''',
        """
vector<vector<int>> Permute(const vector<int>& nums) {
  vector<vector<int>> out;
  vector<int> current;
  function<void(const vector<int>&)> build = [&](const vector<int>& rest) {
    if (rest.empty()) { out.push_back(current); return; }
    for (size_t index = 0; index < rest.size(); ++index) {
      current.push_back(rest[index]);
      vector<int> next;
      for (size_t k = 0; k < rest.size(); ++k)
        if (k != index) next.push_back(rest[k]);
      build(next);
      current.pop_back();
    }
  };
  build(nums);
  return out;
}
""",
        """
public class Solution
{
    public static int[][] Permute(int[] nums)
    {
        var outp = new System.Collections.Generic.List<int[]>();
        var current = new System.Collections.Generic.List<int>();
        System.Action<int[]> build = null;
        build = rest =>
        {
            if (rest.Length == 0) { outp.Add(current.ToArray()); return; }
            for (int index = 0; index < rest.Length; index++)
            {
                current.Add(rest[index]);
                var next = new System.Collections.Generic.List<int>();
                for (int k = 0; k < rest.Length; k++) if (k != index) next.Add(rest[k]);
                build(next.ToArray());
                current.RemoveAt(current.Count - 1);
            }
        };
        build((int[])nums.Clone());
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[][] permute(int[] nums) {
        java.util.List<int[]> out = new java.util.ArrayList<>();
        build(nums, new java.util.ArrayList<Integer>(), out);
        return out.toArray(new int[0][]);
    }

    static void build(int[] rest, java.util.List<Integer> current,
                      java.util.List<int[]> out) {
        if (rest.length == 0) {
            int[] row = new int[current.size()];
            for (int i = 0; i < row.length; i++) row[i] = current.get(i);
            out.add(row);
            return;
        }
        for (int index = 0; index < rest.length; index++) {
            current.add(rest[index]);
            java.util.List<Integer> next = new java.util.ArrayList<>();
            for (int k = 0; k < rest.length; k++) if (k != index) next.add(rest[k]);
            int[] rest2 = new int[next.size()];
            for (int k = 0; k < rest2.length; k++) rest2[k] = next.get(k);
            build(rest2, current, out);
            current.remove(current.size() - 1);
        }
    }
}
"""),
      position=44, source=LC, sourceId=46,
      sourceNote="LeetCode 46 (Medium). Same shape as Combination Sum with a different stopping rule, and the difference is the whole difference: here each number is used once, so the next call gets what is left rather than the same position."),

    q("g-merge-intervals", "Merge Intervals", STRETCH, [ALGO, "matrix"], "MergeIntervals",
      "Have the function MergeIntervals(intervals) take a list of intervals, each a "
      "pair of numbers giving its start and its end, and return the list with every "
      "pair of intervals that overlap or touch folded into one.\n\n" + MATRIX_NOTE +
      "\n\nTwo intervals that merely touch still count as one, so [1, 4] and [4, 5] "
      "become [1, 5] rather than staying apart. The answer is sorted by start.\n\n"
      "The input is not necessarily sorted, so it has to be sorted first. After that "
      "it is one pass: fold each interval into the one before it if they meet, and "
      "otherwise start a new one.",
      (["intervals"], [MATRIX]),
      [c([[[1, 3], [2, 6], [8, 10], [15, 18]]], [[1, 6], [8, 10], [15, 18]], MATRIX),
       c([[[1, 4], [4, 5]]], [[1, 5]], MATRIX),
       c([[[1, 4], [0, 4]]], [[0, 4]], MATRIX),
       c([[[1, 4], [2, 3]]], [[1, 4]], MATRIX),
       c([[[1, 4], [4, 4]]], [[1, 4]], MATRIX),
       c([[[1, 5], [2, 3], [3, 7], [4, 8]]], [[1, 8]], MATRIX),
       c([[]], [], MATRIX)],
      S('''def MergeIntervals(intervals):
    ordered = sorted([list(interval) for interval in intervals])
    out = []
    for start, end in ordered:
        if out and start <= out[-1][1]:
            if end > out[-1][1]:
                out[-1][1] = end
        else:
            out.append([start, end])
    return out
''',
        """
vector<vector<int>> MergeIntervals(const vector<vector<int>>& intervals) {
  vector<vector<int>> ordered = intervals;
  sort(ordered.begin(), ordered.end());
  vector<vector<int>> out;
  for (const auto& interval : ordered) {
    if (!out.empty() && interval[0] <= out.back()[1]) {
      if (interval[1] > out.back()[1]) out.back()[1] = interval[1];
    } else {
      out.push_back(interval);
    }
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[][] MergeIntervals(int[][] intervals)
    {
        var ordered = new int[intervals.Length][];
        for (int i = 0; i < intervals.Length; i++) ordered[i] = (int[])intervals[i].Clone();
        System.Array.Sort(ordered, (a, b) => a[0] != b[0] ? a[0].CompareTo(b[0]) : a[1].CompareTo(b[1]));
        var outp = new System.Collections.Generic.List<int[]>();
        foreach (int[] interval in ordered)
        {
            if (outp.Count > 0 && interval[0] <= outp[outp.Count - 1][1])
            {
                if (interval[1] > outp[outp.Count - 1][1]) outp[outp.Count - 1][1] = interval[1];
            }
            else outp.Add((int[])interval.Clone());
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[][] mergeIntervals(int[][] intervals) {
        int[][] ordered = intervals.clone();
        java.util.Arrays.sort(ordered, (a, b) -> a[0] != b[0]
            ? Integer.compare(a[0], b[0]) : Integer.compare(a[1], b[1]));
        java.util.List<int[]> out = new java.util.ArrayList<>();
        for (int[] interval : ordered) {
            if (!out.isEmpty() && interval[0] <= out.get(out.size() - 1)[1]) {
                if (interval[1] > out.get(out.size() - 1)[1])
                    out.get(out.size() - 1)[1] = interval[1];
            } else out.add(interval.clone());
        }
        return out.toArray(new int[0][]);
    }
}
"""),
      position=45, source=LC, sourceId=56,
      sourceNote="LeetCode 56 (Medium). The overlap test is <= rather than <, so touching intervals fold together. It is the same three-phase pass as Insert Interval with the input already in one piece."),

    q("g-lca-binary-tree", "Lowest Common Ancestor of a Binary Tree", STRETCH,
      [ALGO, "tree"], "LowestCommonAncestorBinaryTree",
      "Have the function LowestCommonAncestorBinaryTree(root, p, q) take a binary "
      "tree -- any binary tree, not necessarily a search tree -- and the values of "
      "two of its nodes, and return the value of the lowest node that is an ancestor "
      "of both. A node counts as its own ancestor. Return -1 if either value is not "
      "in the tree.\n\n" + TREE_NOTE +
      "\n\nThis is the same question as the lowest common ancestor of a *search* "
      "tree from wave 1, and the answer is a different shape of code. A search tree's "
      "ordering tells you which way to walk, so one path down is enough. A general "
      "tree tells you nothing, so both branches have to be searched.\n\nThe rule "
      "that makes it work: search each subtree for either value. If both subtrees "
      "come back with something, this node is the answer. If only one does, keep "
      "going. If a node is one of the two values, it is the answer immediately -- "
      "nothing below it can be an ancestor of the node itself.",
      (["root", "p", "q"], [TREE, INT, INT]),
      [c([[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1], 3, INT),
       c([[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4], 5, INT),
       c([[1, 2], 1, 2], 1, INT),
       c([[1, 2], 2, 1], 1, INT),
       c([[2, 1, 3], 1, 3], 2, INT),
       c([[1], 1, 1], 1, INT),
       c([[], 1, 1], -1, INT)],
      S('''def LowestCommonAncestorBinaryTree(root, p, q):
    def find(node):
        if node >= len(root) or root[node] is None:
            return None
        if root[node] == p or root[node] == q:
            return root[node]
        left = find(2 * node + 1)
        right = find(2 * node + 2)
        if left is not None and right is not None:
            return root[node]
        return left if left is not None else right

    hit = find(0)
    return -1 if hit is None else hit
''',
        """
int LowestCommonAncestorBinaryTree(const vector<optional<int>>& root, int p, int q) {
  // -1 means "nothing here"; the value itself is the answer otherwise. Both
  // branches are searched, and both coming back with something is what makes
  // the current node the ancestor.
  function<int(size_t)> find = [&](size_t node) -> int {
    if (node >= root.size() || !root[node].has_value()) return -1;
    int value = *root[node];
    if (value == p || value == q) return value;
    int left = find(2 * node + 1);
    int right = find(2 * node + 2);
    if (left != -1 && right != -1) return value;
    return left != -1 ? left : right;
  };
  return find(0);
}
""",
        """
public class Solution
{
    public static int LowestCommonAncestorBinaryTree(int?[] root, int p, int q)
    {
        int Find(int node)
        {
            if (node >= root.Length || !root[node].HasValue) return -1;
            int value = root[node].Value;
            if (value == p || value == q) return value;
            int left = Find(2 * node + 1);
            int right = Find(2 * node + 2);
            if (left != -1 && right != -1) return value;
            return left != -1 ? left : right;
        }
        return Find(0);
    }
}
""",
        """
public class Solution {
    public static int lowestCommonAncestorBinaryTree(Integer[] root, int p, int q) {
        return find(root, 0, p, q);
    }

    static int find(Integer[] root, int node, int p, int q) {
        if (node >= root.length || root[node] == null) return -1;
        int value = root[node];
        if (value == p || value == q) return value;
        int left = find(root, 2 * node + 1, p, q);
        int right = find(root, 2 * node + 2, p, q);
        if (left != -1 && right != -1) return value;
        return left != -1 ? left : right;
    }
}
"""),
      position=46, source=LC, sourceId=236,
      sourceNote="LeetCode 236 (Medium). The counterpart to the BST version at position 10, and worth doing next to it: without an ordering there is nothing to steer by, so both branches are searched and the first node whose two subtrees each hold one of the values is the answer."),

    q("g-accounts-merge", "Accounts Merge", STRETCH, [ALGO, "matrix", "sorting"],
      "AccountsMerge",
      "Have the function AccountsMerge(accounts) take a list of account rows, where "
      "each row is a person's name followed by one or more of that person's email "
      "addresses, and return the list with every person who shares an address with "
      "anyone merged into a single row.\n\n" + MATRIX_NOTE +
      "\n\nThe catch is that the rows are not consistent. The same person can appear "
      "under different names in different rows, and the same address can appear "
      "under different names, and the name that survives is the one from the row "
      "where that address was seen first. Every merged row is the name followed by "
      "that person's addresses, and the rows come back sorted.\n\nSo the answer is "
      "a matrix of words rather than of numbers, which is why it is declared as rows "
      "of strings.",
      (["accounts"], [STRMATRIX]),
      [c([[["John", "j1@m.co", "j2@m.co"], ["John", "j3@m.co", "j4@m.co"],
          ["Mary", "m1@m.co"]]],
         [["John", "j1@m.co", "j2@m.co", "j3@m.co", "j4@m.co"], ["Mary", "m1@m.co"]],
         STRMATRIX),
       c([[["Gabe", "G0@e.com"], ["Kevin", "Kevin0@e.com", "Kevin1@e.com"],
           ["Ethan", "E0@e.com"], ["Hanzo", "H0@e.com", "H1@e.com"]]],
         [["Ethan", "E0@e.com"], ["Gabe", "G0@e.com"], ["Hanzo", "H0@e.com", "H1@e.com"],
          ["Kevin", "Kevin0@e.com", "Kevin1@e.com"]], STRMATRIX),
       c([[["a", "b@c"], ["a", "b@c"], ["a", "d@c"]]], [["a", "b@c", "d@c"]], STRMATRIX),
       c([[["x", "p@q"], ["y", "r@q"]]], [["x", "p@q"], ["y", "r@q"]], STRMATRIX),
       c([[["z", "only@one"]]], [["z", "only@one"]], STRMATRIX)],
      S('''def AccountsMerge(accounts):
    # First sighting of an address decides the name it belongs to.
    owner = {}
    for row in accounts:
        for address in row[1:]:
            if address not in owner:
                owner[address] = row[0]
    groups = {}
    for address, name in owner.items():
        groups.setdefault(name, []).append(address)
    return sorted([name] + sorted(addresses) for name, addresses in groups.items())
''',
        """
vector<vector<string>> AccountsMerge(const vector<vector<string>>& accounts) {
  map<string, string> owner;
  for (const auto& row : accounts)
    for (size_t i = 1; i < row.size(); ++i)
      if (owner.find(row[i]) == owner.end()) owner[row[i]] = row[0];
  map<string, vector<string>> groups;
  for (const auto& entry : owner) groups[entry.second].push_back(entry.first);
  vector<vector<string>> out;
  for (auto& entry : groups) {
    vector<string> row{entry.first};
    vector<string> addresses = entry.second;
    sort(addresses.begin(), addresses.end());
    for (const string& address : addresses) row.push_back(address);
    out.push_back(row);
  }
  sort(out.begin(), out.end());
  return out;
}
""",
        """
public class Solution
{
    public static string[][] AccountsMerge(string[][] accounts)
    {
        var owner = new System.Collections.Generic.Dictionary<string, string>();
        foreach (string[] row in accounts)
            for (int i = 1; i < row.Length; i++)
                if (!owner.ContainsKey(row[i])) owner[row[i]] = row[0];
        var groups = new System.Collections.Generic.SortedDictionary<string,
            System.Collections.Generic.List<string>>();
        foreach (var entry in owner)
        {
            if (!groups.ContainsKey(entry.Value))
                groups[entry.Value] = new System.Collections.Generic.List<string>();
            groups[entry.Value].Add(entry.Key);
        }
        var outp = new System.Collections.Generic.List<string[]>();
        foreach (var entry in groups)
        {
            entry.Value.Sort();
            var row = new System.Collections.Generic.List<string> { entry.Key };
            row.AddRange(entry.Value);
            outp.Add(row.ToArray());
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static String[][] accountsMerge(String[][] accounts) {
        java.util.Map<String, String> owner = new java.util.LinkedHashMap<>();
        for (String[] row : accounts)
            for (int i = 1; i < row.length; i++)
                if (!owner.containsKey(row[i])) owner.put(row[i], row[0]);
        java.util.Map<String, java.util.List<String>> groups = new java.util.TreeMap<>();
        for (java.util.Map.Entry<String, String> entry : owner.entrySet())
            groups.computeIfAbsent(entry.getValue(), k -> new java.util.ArrayList<>())
                  .add(entry.getKey());
        java.util.List<String[]> out = new java.util.ArrayList<>();
        for (java.util.Map.Entry<String, java.util.List<String>> entry : groups.entrySet()) {
            java.util.List<String> addresses = entry.getValue();
            java.util.Collections.sort(addresses);
            java.util.List<String> row = new java.util.ArrayList<>();
            row.add(entry.getKey());
            row.addAll(addresses);
            out.add(row.toArray(new String[0]));
        }
        return out.toArray(new String[0][]);
    }
}
"""),
      position=48, source=LC, sourceId=721,
      sourceNote="LeetCode 721 (Medium). The first question here whose answer is a matrix of words rather than of numbers, and the reason the strmatrix contract exists. 'First sighting wins' is the rule that makes the name deterministic."),

    q("g-sort-colors", "Sort Colors", STRETCH, [ALGO, "sorting"], "SortColors",
      "Have the function SortColors(nums) take a list of 0s, 1s and 2s and return the "
      "same list with all the 0s first, then the 1s, then the 2s.\n\nThere are only "
      "three values, so a counting pass over the list would work, and so would any "
      "sort. The question is the one-pass version.\n\nThree cursors, all moving: "
      "one at the front of the 0s, one at the part not yet placed, and one at the "
      "back. A 2 is swapped with the back and the middle cursor does not move, "
      "because the value swapped in has not been looked at yet. A 0 is swapped with "
      "the front and both cursors move. Forgetting that the middle cursor stays put "
      "on a 2 is the one mistake this question is made of.",
      (["nums"], [ARR]),
      [c([[2, 0, 2, 1, 1, 0]], [0, 0, 1, 1, 2, 2], ARR),
       c([[2, 0, 1]], [0, 1, 2], ARR),
       c([[2, 2, 0, 0, 1, 1]], [0, 0, 1, 1, 2, 2], ARR),
       c([[1]], [1], ARR),
       c([[0]], [0], ARR),
       c([[2]], [2], ARR),
       c([[]], [], ARR)],
      S('''def SortColors(nums):
    out = list(nums)
    low, middle, high = 0, 0, len(out) - 1
    while middle <= high:
        if out[middle] == 0:
            out[low], out[middle] = out[middle], out[low]
            low += 1
            middle += 1
        elif out[middle] == 2:
            out[middle], out[high] = out[high], out[middle]
            high -= 1
            # The middle cursor stays put: whatever was swapped in from the back
            # has not been looked at yet.
        else:
            middle += 1
    return out
''',
        """
vector<int> SortColors(const vector<int>& nums) {
  vector<int> out = nums;
  int low = 0, middle = 0, high = (int)out.size() - 1;
  while (middle <= high) {
    if (out[middle] == 0) {
      swap(out[low], out[middle]);
      ++low;
      ++middle;
    } else if (out[middle] == 2) {
      swap(out[middle], out[high]);
      --high;
      // The middle cursor stays put: the value swapped in is unexamined.
    } else {
      ++middle;
    }
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[] SortColors(int[] nums)
    {
        var outp = new int[nums.Length];
        System.Array.Copy(nums, outp, nums.Length);
        int low = 0, middle = 0, high = outp.Length - 1;
        while (middle <= high)
        {
            if (outp[middle] == 0)
            {
                int swap = outp[low]; outp[low] = outp[middle]; outp[middle] = swap;
                low++;
                middle++;
            }
            else if (outp[middle] == 2)
            {
                int swap = outp[middle]; outp[middle] = outp[high]; outp[high] = swap;
                high--;
            }
            else middle++;
        }
        return outp;
    }
}
""",
        """
public class Solution {
    public static int[] sortColors(int[] nums) {
        int[] out = nums.clone();
        int low = 0, middle = 0, high = out.length - 1;
        while (middle <= high) {
            if (out[middle] == 0) {
                int swap = out[low]; out[low] = out[middle]; out[middle] = swap;
                low++;
                middle++;
            } else if (out[middle] == 2) {
                int swap = out[middle]; out[middle] = out[high]; out[high] = swap;
                high--;
            } else {
                middle++;
            }
        }
        return out;
    }
}
"""),
      position=49, source=LC, sourceId=75,
      sourceNote="LeetCode 75 (Medium). The Dutch national flag problem. Not advancing the middle cursor after swapping a 2 into place is the entire question, and it is the first time on this list that not moving is the right answer."),
]
