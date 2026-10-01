#!/usr/bin/env python3
"""Grind 75, wave 6: positions 62-75.

This is the end of the list. Three positions in the range are skipped, so ten
questions are here and three are not:

  * 65 LRU Cache, 68 Serialize and Deserialize Binary Tree and 70 Find Median
    from Data Stream all build a class and keep state between calls. A
    harness that runs one function, a few arguments, a value back has nowhere
    to put that state, so they are skipped for the same reason the other eight
    design problems are.
  * 69 Trapping Rain Water was already in the catalogue from the original
    LeetCode set, under its own id, so `build_grind75.py` stamps the position
    onto that one instead of adding a copy.

Every expectation came out of `tools/_ref_wave56.py`, and the four reference
implementations that could be checked against a brute force were: Minimum
Height Trees against computing every node's eccentricity, Minimum Window
Substring against enumerating all substrings, Trapping Rain Water and Largest
Rectangle in Histogram against the obvious two-loop and nested-loop versions,
Find All Anagrams against a sliding counter, and Maximum Profit in Job
Scheduling against trying every subset of jobs for compatibility. All of them
agreed.

Two questions in this wave are the first to take three or more arguments:
Word Ladder takes a start word, an end word and a word list, and Maximum Profit
in Job Scheduling takes three parallel lists. Maximum Profit in Job Scheduling
is also the first to make half-open intervals matter -- a job ending at 5 does
not block one starting at 5, and getting that comparison wrong costs a job
from the answer.

Merge k Sorted Lists is the odd one out. The list it takes is a list of lists,
which is a `matrix`, and the list it returns is flat, which is a `list`. The
two are the same shape on the wire and the harness renders them the same way,
which is the honest outcome: the difference between a linked list and an array
of lists is a difference of meaning that a single return value cannot carry.
"""

from __future__ import annotations

from grind75_common import (ALGO, ARR, BOOL, DP, INT, LC, LIST, MATRIX, MATRIX_NOTE,
                            SEARCH, SM, STRETCH, STR, STRARRAY, STRI, TREE, TREE_NOTE,
                            TREE_TAG, c, q, S)

QUESTIONS = [
    q("g-find-anagrams", "Find All Anagrams in a String", STRETCH, [ALGO, SM, "sliding window"],
      "FindAnagrams",
      "Have the function FindAnagrams(str, pattern) take a string and a shorter "
      "pattern and return the list of starting positions at which some slice of "
      "str of the pattern's length is a rearrangement of the pattern.\n\nThe "
      "positions come back in increasing order, and a string shorter than the "
      "pattern has none.\n\nThe window is always the pattern's length, and it "
      "moves one place at a time. What changes per move is two counts: one "
      "letter leaves the window and one enters. So a count of 26 numbers is "
      "enough for the whole search, and comparing the window's count against the "
      "pattern's count is the whole test.\n\nA count of 26 works because the "
      "letters are lower case. A window that has the right letters but in the "
      "wrong order still matches, which is exactly what an anagram is.",
      (["str", "pattern"], [STR, STR]),
      [c(["cbaebabacd", "abc"], [0, 6], ARR),
       c(["abab", "ab"], [0, 1, 2], ARR),
       c(["aaaaaaaaaa", "a"], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ARR),
       c(["aaa", "a"], [0, 1, 2], ARR),
       c(["ab", "ab"], [0], ARR),
       c(["abc", "wxyz"], [], ARR)],
      S('''def FindAnagrams(str, pattern):
    if not pattern or len(pattern) > len(str):
        return []
    # 26 counters: one per lower case letter. The window count and the pattern
    # count are equal exactly when the window is an anagram of the pattern.
    need = [0] * 26
    for letter in pattern:
        need[ord(letter) - 97] += 1
    window = [0] * 26
    for letter in str[:len(pattern)]:
        window[ord(letter) - 97] += 1
    out = [0] if window == need else []
    for end in range(len(pattern), len(str)):
        window[ord(str[end]) - 97] += 1
        window[ord(str[end - len(pattern)]) - 97] -= 1
        if window == need:
            out.append(end - len(pattern) + 1)
    return out
''',
        """
vector<int> FindAnagrams(const string& str, const string& pattern) {
  vector<int> out;
  if (pattern.empty() || pattern.size() > str.size()) return out;
  array<int, 26> need{}, window{};
  for (char letter : pattern) need[letter - 'a']++;
  for (size_t i = 0; i < pattern.size(); ++i) window[str[i] - 'a']++;
  if (window == need) out.push_back(0);
  for (size_t end = pattern.size(); end < str.size(); ++end) {
    // Two counts change per move: one letter in, one letter out.
    window[str[end] - 'a']++;
    window[str[end - pattern.size()] - 'a']--;
    if (window == need) out.push_back((int)(end - pattern.size() + 1));
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[] FindAnagrams(string str, string pattern)
    {
        var outp = new System.Collections.Generic.List<int>();
        if (pattern.Length == 0 || pattern.Length > str.Length) return outp.ToArray();
        var need = new int[26];
        var window = new int[26];
        foreach (char letter in pattern) need[letter - 'a']++;
        for (int i = 0; i < pattern.Length; i++) window[str[i] - 'a']++;
        if (window.SequenceEqual(need)) outp.Add(0);
        for (int end = pattern.Length; end < str.Length; end++)
        {
            window[str[end] - 'a']++;
            window[str[end - pattern.Length] - 'a']--;
            if (window.SequenceEqual(need)) outp.Add(end - pattern.Length + 1);
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[] findAnagrams(String str, String pattern) {
        java.util.List<Integer> out = new java.util.ArrayList<>();
        if (pattern.length() == 0 || pattern.length() > str.length())
            return new int[0];
        int[] need = new int[26];
        int[] window = new int[26];
        for (int i = 0; i < pattern.length(); i++) need[pattern.charAt(i) - 'a']++;
        for (int i = 0; i < pattern.length(); i++) window[str.charAt(i) - 'a']++;
        if (java.util.Arrays.equals(window, need)) out.add(0);
        for (int end = pattern.length(); end < str.length(); end++) {
            window[str.charAt(end) - 'a']++;
            window[str.charAt(end - pattern.length()) - 'a']--;
            if (java.util.Arrays.equals(window, need)) out.add(end - pattern.length() + 1);
        }
        int[] result = new int[out.size()];
        for (int i = 0; i < result.length; i++) result[i] = out.get(i);
        return result;
    }
}
"""),
      position=62, source=LC, sourceId=438,
      sourceNote="LeetCode 438 (Medium). The window never changes length, so one array of 26 counters answers every position and each move updates two entries."),

    q("g-min-height-trees", "Minimum Height Trees", STRETCH, [ALGO, "trees", "graphs"],
      "MinHeightTrees",
      "Have the function MinHeightTrees(n, edges) take the number of nodes in an "
      "undirected tree and its edges as pairs of node numbers, and return the "
      "node numbers that could be the root of the shortest possible tree -- the "
      "ones that give the smallest greatest distance to any other node.\n\nA "
      "single node is its own answer.\n\nThe answer is the middle of the tree, "
      "and stripping the tree from the outside in finds it without any measuring. "
      "Start with the leaves -- the nodes of degree one -- and remove a whole "
      "round of them at a time. Every node removed is too far from the middle to "
      "be a root, and what is left at the end is one node or two neighbours, and "
      "those are the answers.\n\nSo the work is a queue of leaves and a degree "
      "count. A node's degree drops as its neighbours are removed, and the moment "
      "it reaches one it is a leaf itself and joins the queue. The queue's length "
      "has to be read before the round starts, because the nodes that become "
      "leaves during the round belong to the next one. Getting that wrong peels "
      "the tree twice as fast and returns the wrong answer.",
      (["n", "edges"], [INT, MATRIX]),
      [c([6, [[0, 1], [0, 2], [3, 4], [5, 4]]], [0, 4], ARR),
       c([4, [[0, 1], [1, 2], [1, 3]]], [1], ARR),
       c([7, [[0, 1], [0, 2], [0, 3], [1, 4], [2, 5], [3, 6]]], [0], ARR),
       c([3, [[0, 1], [1, 2]]], [1], ARR),
       c([2, [[0, 1]]], [0, 1], ARR),
       c([1, []], [0], ARR)],
      S('''from collections import deque


def MinHeightTrees(n, edges):
    if n <= 0:
        return []
    if n == 1:
        return [0]
    adjacency = [[] for _ in range(n)]
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    degree = [len(neighbours) for neighbours in adjacency]
    leaves = deque(node for node in range(n) if degree[node] == 1)
    remaining = n
    while remaining > 2:
        # The queue's length is read before the round: nodes that drop to one
        # degree during this round belong to the next one, not this one.
        level = len(leaves)
        remaining -= level
        for _ in range(level):
            leaf = leaves.popleft()
            for neighbour in adjacency[leaf]:
                degree[neighbour] -= 1
                if degree[neighbour] == 1:
                    leaves.append(neighbour)
    return sorted(leaves)
''',
        """
vector<int> MinHeightTrees(int n, const vector<vector<int>>& edges) {
  vector<int> out;
  if (n <= 0) return out;
  if (n == 1) { out.push_back(0); return out; }
  vector<vector<int>> adjacency(n);
  for (const auto& edge : edges) {
    adjacency[edge[0]].push_back(edge[1]);
    adjacency[edge[1]].push_back(edge[0]);
  }
  vector<int> degree(n);
  queue<int> leaves;
  for (int node = 0; node < n; ++node) {
    degree[node] = (int)adjacency[node].size();
    if (degree[node] == 1) leaves.push(node);
  }
  int remaining = n;
  while (remaining > 2) {
    // Read the level size before peeling it, or the tree collapses twice as
    // fast and the answer is a ring further in.
    int level = (int)leaves.size();
    remaining -= level;
    while (level--) {
      int leaf = leaves.front();
      leaves.pop();
      for (int neighbour : adjacency[leaf]) {
        if (--degree[neighbour] == 1) leaves.push(neighbour);
      }
    }
  }
  while (!leaves.empty()) { out.push_back(leaves.front()); leaves.pop(); }
  sort(out.begin(), out.end());
  return out;
}
""",
        """
public class Solution
{
    public static int[] MinHeightTrees(int n, int[][] edges)
    {
        if (n <= 0) return new int[0];
        if (n == 1) return new int[] { 0 };
        var adjacency = new System.Collections.Generic.List<int>[n];
        for (int i = 0; i < n; i++) adjacency[i] = new System.Collections.Generic.List<int>();
        foreach (int[] edge in edges)
        {
            adjacency[edge[0]].Add(edge[1]);
            adjacency[edge[1]].Add(edge[0]);
        }
        var degree = new int[n];
        var leaves = new System.Collections.Generic.Queue<int>();
        for (int node = 0; node < n; node++)
        {
            degree[node] = adjacency[node].Count;
            if (degree[node] == 1) leaves.Enqueue(node);
        }
        int remaining = n;
        while (remaining > 2)
        {
            int level = leaves.Count;
            remaining -= level;
            while (level-- > 0)
            {
                int leaf = leaves.Dequeue();
                foreach (int neighbour in adjacency[leaf])
                    if (--degree[neighbour] == 1) leaves.Enqueue(neighbour);
            }
        }
        var outp = new System.Collections.Generic.List<int>();
        while (leaves.Count > 0) outp.Add(leaves.Dequeue());
        outp.Sort();
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[] minHeightTrees(int n, int[][] edges) {
        if (n <= 0) return new int[0];
        if (n == 1) return new int[] { 0 };
        java.util.List<java.util.List<Integer>> adjacency = new java.util.ArrayList<>();
        for (int i = 0; i < n; i++) adjacency.add(new java.util.ArrayList<Integer>());
        for (int[] edge : edges) {
            adjacency.get(edge[0]).add(edge[1]);
            adjacency.get(edge[1]).add(edge[0]);
        }
        int[] degree = new int[n];
        java.util.Queue<Integer> leaves = new java.util.ArrayDeque<>();
        for (int node = 0; node < n; node++) {
            degree[node] = adjacency.get(node).size();
            if (degree[node] == 1) leaves.add(node);
        }
        int remaining = n;
        while (remaining > 2) {
            int level = leaves.size();
            remaining -= level;
            for (int i = 0; i < level; i++) {
                int leaf = leaves.poll();
                for (int neighbour : adjacency.get(leaf))
                    if (--degree[neighbour] == 1) leaves.add(neighbour);
            }
        }
        java.util.List<Integer> out = new java.util.ArrayList<>();
        while (!leaves.isEmpty()) out.add(leaves.poll());
        java.util.Collections.sort(out);
        int[] result = new int[out.size()];
        for (int i = 0; i < result.length; i++) result[i] = out.get(i);
        return result;
    }
}
"""),
      position=63, source=LC, sourceId=310,
      sourceNote="LeetCode 310 (Hard). Reading the queue's length before each round is the whole trick: a node that becomes a leaf mid-round belongs to the next ring."),

    q("g-task-scheduler", "Task Scheduler", STRETCH, [ALGO, "greedy", "scheduling"],
      "TaskScheduler",
      "Have the function TaskScheduler(tasks) take a list of task letters and "
      "return the fewest time units needed to run all of them, where the same "
      "letter cannot appear twice in a row -- there has to be at least one unit "
      "of something else between two runs of the same task. A gap may be filled "
      "with another task or left idle. The empty list takes no time.\n\nOnly "
      "two numbers matter: how many times the most common task runs, and how "
      "many tasks are tied at that count.\n\nThe most common task is the "
      "constraint, because its runs have to be spread across separate time units "
      "with the whole set of most common tasks between each pair. That forces "
      "`most - 1` rounds of `kinds` slots, plus one more round at the end to "
      "place the final run of each -- so `(most - 1) * (kinds + 1) + kinds`.\n\n"
      "But the schedule can never be shorter than just running the tasks in "
      "order, which is `len(tasks)`. When there is no cooldown to observe at "
      "all -- one kind of task, or every task appearing once -- the two disagree "
      "and the larger one is the answer. A hundred of the same letter is 199 "
      "units, not 100.",
      (["tasks"], [STRI]),
      [c([["A", "A", "A", "B", "B", "B"]], 8, INT),
       c([["A", "A", "A", "B", "B", "B", "C", "C", "C", "C", "C"]], 11, INT),
       c([["A", "B", "C", "D", "D", "D", "D", "E", "E", "E", "F", "F"]], 12, INT),
       c([["A", "A", "A", "A", "A", "A", "A", "A"]], 15, INT),
       c([["A"]], 1, INT)],
      S('''from collections import Counter


def TaskScheduler(tasks):
    if not tasks:
        return 0
    counts = Counter(tasks)
    most = max(counts.values())
    kinds = sum(1 for count in counts.values() if count == most)
    # The most common task's runs have to be `most - 1` rounds of `kinds` slots
    # apart, plus a final round to place the last run of each.
    forced = (most - 1) * (kinds + 1) + kinds
    # Never shorter than just running the tasks.
    return max(len(tasks), forced)
''',
        """
int TaskScheduler(const vector<string>& tasks) {
  if (tasks.empty()) return 0;
  map<string, int> counts;
  for (const string& task : tasks) counts[task]++;
  int most = 0, kinds = 0;
  for (const auto& entry : counts) {
    if (entry.second > most) { most = entry.second; kinds = 1; }
    else if (entry.second == most) kinds++;
  }
  int forced = (most - 1) * (kinds + 1) + kinds;
  return max((int)tasks.size(), forced);
}
""",
        """
public class Solution
{
    public static int TaskScheduler(string[] tasks)
    {
        if (tasks.Length == 0) return 0;
        var counts = new System.Collections.Generic.Dictionary<string, int>();
        foreach (string task in tasks)
        {
            int seen;
            counts[task] = counts.TryGetValue(task, out seen) ? seen + 1 : 1;
        }
        int most = 0, kinds = 0;
        foreach (int count in counts.Values)
        {
            if (count > most) { most = count; kinds = 1; }
            else if (count == most) kinds++;
        }
        int forced = (most - 1) * (kinds + 1) + kinds;
        return Math.Max(tasks.Length, forced);
    }
}
""",
        """
public class Solution {
    public static int taskScheduler(String[] tasks) {
        if (tasks.length == 0) return 0;
        java.util.Map<String, Integer> counts = new java.util.HashMap<>();
        for (String task : tasks)
            counts.put(task, counts.getOrDefault(task, 0) + 1);
        int most = 0, kinds = 0;
        for (int count : counts.values()) {
            if (count > most) { most = count; kinds = 1; }
            else if (count == most) kinds++;
        }
        int forced = (most - 1) * (kinds + 1) + kinds;
        return Math.max(tasks.length, forced);
    }
}
"""),
      position=64, source=LC, sourceId=621,
      sourceNote="LeetCode 621 (Medium). Two numbers decide it: the largest count and how many tasks share it. Forgetting the max against len(tasks) over-answers the easy case."),

    q("g-kth-smallest", "Kth Smallest Element in a BST", STRETCH,
      [TREE_TAG, "trees", "stacks"], "KthSmallest",
      "Have the function KthSmallest(root, k) take a binary search tree and a "
      "one-based position and return the value at that position when the tree's "
      "values are in order.\n\n" + TREE_NOTE +
      "\n\nA binary search tree has one property that matters here: an in-order "
      "walk -- left subtree, then the node, then right subtree -- visits the "
      "values in increasing order. So the answer is the kth value that walk "
      "reaches, and the whole question is how to count visits without building "
      "an array of them.\n\nThe walk does not have to recurse. Keep the path "
      "down the left spine on a stack, and when the spine runs out take the top "
      "of the stack as the next value in order and step to its right subtree. "
      "Each value is counted as it comes off the stack, and the kth one is the "
      "answer. That is O(height) space instead of O(n), which is the reason to "
      "write it this way.\n\nA k past the number of nodes has no answer, and "
      "this returns -1 for it.",
      (["root", "k"], [TREE, INT]),
      [c([[3, 1, 4, None, 2], 1], 1, INT),
       c([[3, 1, 4, None, 2], 2], 2, INT),
       c([[5, 3, 6, 2, 4, None, None, 1], 3], 3, INT),
       c([[2, 1, 3], 2], 2, INT),
       c([[2, 1, 3], 1], 1, INT),
       c([[2, 1, 3], 3], 3, INT),
       c([[1, 2], 1], 2, INT),
       c([[1], 1], 1, INT)],
      S('''def KthSmallest(root, k):
    if k < 1:
        return -1
    # The stack holds the left spine. When it runs out, the top is the next
    # value in order, and the walk continues into that node's right subtree.
    stack = []
    node = 0
    while True:
        while node < len(root) and root[node] is not None:
            stack.append(node)
            node = 2 * node + 1
        if not stack:
            return -1
        node = stack.pop()
        k -= 1
        if k == 0:
            return root[node]
        node = 2 * node + 2
''',
        """
int KthSmallest(const vector<optional<int>>& root, int k) {
  if (k < 1) return -1;
  // The stack holds the left spine. When it runs out the top is the next
  // value in in-order, and the walk steps into that node's right subtree.
  vector<size_t> stack;
  size_t node = 0;
  while (true) {
    while (node < root.size() && root[node].has_value()) {
      stack.push_back(node);
      node = 2 * node + 1;
    }
    if (stack.empty()) return -1;
    node = stack.back();
    stack.pop_back();
    if (--k == 0) return *root[node];
    node = 2 * node + 2;
  }
}
""",
        """
public class Solution
{
    public static int KthSmallest(int?[] root, int k)
    {
        if (k < 1) return -1;
        // The stack holds the left spine. When it runs out the top is the next
        // value in order, and the walk steps into its right subtree.
        var stack = new System.Collections.Generic.Stack<int>();
        int node = 0;
        while (true)
        {
            while (node < root.Length && root[node].HasValue)
            {
                stack.Push(node);
                node = 2 * node + 1;
            }
            if (stack.Count == 0) return -1;
            node = stack.Pop();
            if (--k == 0) return root[node].Value;
            node = 2 * node + 2;
        }
    }
}
""",
        """
public class Solution {
    public static int kthSmallest(Integer[] root, int k) {
        if (k < 1) return -1;
        java.util.Deque<Integer> stack = new java.util.ArrayDeque<>();
        int node = 0;
        while (true) {
            while (node < root.length && root[node] != null) {
                stack.push(node);
                node = 2 * node + 1;
            }
            if (stack.isEmpty()) return -1;
            node = stack.pop();
            if (--k == 0) return root[node];
            node = 2 * node + 2;
        }
    }
}
"""),
      position=66, source=LC, sourceId=230,
      sourceNote="LeetCode 230 (Medium). The stack version is O(height) space rather than O(n), because nothing has to be collected before the kth value is known."),

    q("g-min-window-substring", "Minimum Window Substring", STRETCH,
      [ALGO, SM, "sliding window"], "MinWindowSubstring",
      "Have the function MinWindowSubstring(str, target) return the shortest "
      "piece of str that contains every character of target, counting "
      "repeats -- so a target of abb needs two b's, not one. Return the empty "
      "string when no such piece exists.\n\nWhen two pieces are the same "
      "length, return the one that starts earlier.\n\nA window with two ends "
      "that only move forward is the whole idea, and the right end advances a "
      "step at a time. What the left end does depends on the window. When the "
      "window has everything it needs, it is a candidate answer, and then the "
      "left end moves in for as long as the window is still valid -- every one "
      "of those shorter windows is also a candidate, and taking the shortest "
      "found overall settles it. When the window is missing something, the "
      "right end moves.\n\nThe check is a count of how many distinct "
      "characters are still short of their target counts, rather than a "
      "comparison of two whole tables.",
      (["str", "target"], [STR, STR]),
      [c(["ADOBECODEBANC", "ABC"], "BANC", STR),
       c(["a", "a"], "a", STR),
       c(["a", "aa"], "", STR),
       c(["ab", "b"], "b", STR),
       c(["bba", "ab"], "ba", STR)],
      S('''def MinWindowSubstring(str, target):
    if not target or len(target) > len(str):
        return ""
    need = {}
    for letter in target:
        need[letter] = need.get(letter, 0) + 1
    # missing counts the distinct characters whose window count is still short
    # of its target count. The window is valid exactly when it is zero.
    missing = len(need)
    have = {}
    best = ""
    left = 0
    for right in range(len(str)):
        letter = str[right]
        have[letter] = have.get(letter, 0) + 1
        if have[letter] == need.get(letter, 0):
            missing -= 1
        # Shrink while the window is still valid, recording each shorter one.
        while missing == 0:
            if not best or right - left + 1 < len(best):
                best = str[left:right + 1]
            leaving = str[left]
            have[leaving] -= 1
            if have[leaving] < need.get(leaving, 0):
                missing += 1
            left += 1
    return best
''',
        """
string MinWindowSubstring(const string& str, const string& target) {
  if (target.empty() || target.size() > str.size()) return "";
  map<char, int> need, have;
  for (char letter : target) need[letter]++;
  // missing counts the distinct characters still short of their target count.
  int missing = (int)need.size();
  string best;
  size_t left = 0;
  for (size_t right = 0; right < str.size(); ++right) {
    char letter = str[right];
    have[letter]++;
    if (have[letter] == need[letter]) missing--;
    while (missing == 0) {
      if (best.empty() || right - left + 1 < best.size())
        best = str.substr(left, right - left + 1);
      char leaving = str[left++];
      // Only a count dropping *below* its target invalidates the window.
      if (--have[leaving] < need[leaving]) missing++;
    }
  }
  return best;
}
""",
        """
public class Solution
{
    public static string MinWindowSubstring(string str, string target)
    {
        if (target.Length == 0 || target.Length > str.Length) return "";
        var need = new System.Collections.Generic.Dictionary<char, int>();
        var have = new System.Collections.Generic.Dictionary<char, int>();
        foreach (char letter in target)
        {
            int seen;
            need[letter] = need.TryGetValue(letter, out seen) ? seen + 1 : 1;
        }
        int missing = need.Count;
        string best = "";
        int left = 0;
        for (int right = 0; right < str.Length; right++)
        {
            char letter = str[right];
            int seen;
            have[letter] = have.TryGetValue(letter, out seen) ? seen + 1 : 1;
            // A character the target never wanted has no entry, so the lookup
            // is guarded at both ends of the window rather than just one.
            int wantedHere;
            if (!need.TryGetValue(letter, out wantedHere)) wantedHere = 0;
            if (have[letter] == wantedHere) missing--;
            while (missing == 0)
            {
                if (best.Length == 0 || right - left + 1 < best.Length)
                    best = str.Substring(left, right - left + 1);
                char leaving = str[left++];
                have[leaving]--;
                // A character the target never wanted has no entry, and looking
                // one up unconditionally throws rather than answering false.
                int wanted;
                if (!need.TryGetValue(leaving, out wanted)) wanted = 0;
                if (have[leaving] < wanted) missing++;
            }
        }
        return best;
    }
}
""",
        """
public class Solution {
    public static String minWindowSubstring(String str, String target) {
        if (target.length() == 0 || target.length() > str.length()) return "";
        java.util.Map<Character, Integer> need = new java.util.HashMap<>();
        java.util.Map<Character, Integer> have = new java.util.HashMap<>();
        for (int i = 0; i < target.length(); i++)
            need.put(target.charAt(i), need.getOrDefault(target.charAt(i), 0) + 1);
        int missing = need.size();
        String best = "";
        int left = 0;
        for (int right = 0; right < str.length(); right++) {
            char letter = str.charAt(right);
            have.put(letter, have.getOrDefault(letter, 0) + 1);
            // A character the target never wanted has no entry, and Map.get
            // answers null rather than zero, so both ends of the window
            // compare against a defaulted zero.
            if (have.get(letter) == need.getOrDefault(letter, 0)) missing--;
            while (missing == 0) {
                if (best.length() == 0 || right - left + 1 < best.length())
                    best = str.substring(left, right + 1);
                char leaving = str.charAt(left++);
                have.put(leaving, have.getOrDefault(leaving, 0) - 1);
                if (have.get(leaving) < need.getOrDefault(leaving, 0)) missing++;
            }
        }
        return best;
    }
}
"""),
      position=67, source=LC, sourceId=76,
      sourceNote="LeetCode 76 (Hard). Shrinking only while the window is valid is what makes it linear; a window that is compared against the target on every move is quadratic."),

    q("g-ladder-length", "Word Ladder", STRETCH, [ALGO, SEARCH, "graphs"], "LadderLength",
      "Have the function LadderLength(begin, end, words) take two words and a "
      "list of allowed words and return the number of words in the shortest "
      "sequence that starts at begin, ends at end and changes exactly one "
      "letter at each step. Every word in the sequence has to be in words, "
      "including the first and the last. Return 0 when there is no such "
      "sequence.\n\nIf begin and end are the same word the answer is 1.\n\n"
      "This is a breadth first search where the neighbours of a word are the "
      "words differing from it in one position. Each rung of the search is one "
      "step further along, so the first time end is reached it has been reached "
      "by the fewest possible steps -- which is what a breadth first search "
      "gives for free. A depth first search would have to try every longer "
      "sequence too.\n\nThe neighbours can be generated rather than looked "
      "up: for each position in the word, try all 26 letters and keep the ones "
      "that are in the list. That is a fixed amount of work per word, so a "
      "search that would otherwise compare every pair of words does not.\n\n"
      "It is worth checking that end is in the list before starting, because "
      "otherwise a search can wander to a word one letter from end, call that a "
      "hit, and report a ladder that was never on the list.",
      (["begin", "end", "words"], [STR, STR, STRARRAY]),
      [c(["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]], 5, INT),
       c(["hit", "cog", ["hot", "dot", "dog", "lot", "log"]], 0, INT),
       c(["a", "c", ["a", "b", "c"]], 2, INT),
       c(["hot", "dog", ["hot", "dog"]], 0, INT),
       c(["aa", "bb", ["aa", "ab", "bb"]], 3, INT)],
      S('''ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def LadderLength(begin, end, words):
    if begin == end:
        return 1
    allowed = set(words)
    # Every word on the ladder has to be in the list, the end word included.
    if end not in allowed:
        return 0
    frontier = {begin}
    seen = {begin}
    steps = 1
    while frontier:
        steps += 1
        nxt = set()
        for word in frontier:
            for index in range(len(word)):
                for letter in ALPHABET:
                    if letter == word[index]:
                        continue
                    candidate = word[:index] + letter + word[index + 1:]
                    if candidate == end:
                        return steps
                    if candidate in allowed and candidate not in seen:
                        seen.add(candidate)
                        nxt.add(candidate)
        frontier = nxt
    return 0
''',
        """
int LadderLength(const string& begin, const string& end,
                const vector<string>& words) {
  if (begin == end) return 1;
  set<string> allowed(words.begin(), words.end());
  if (!allowed.count(end)) return 0;
  const string alphabet = "abcdefghijklmnopqrstuvwxyz";
  set<string> frontier{begin}, seen{begin};
  int steps = 1;
  while (!frontier.empty()) {
    steps++;
    set<string> nxt;
    for (const string& word : frontier) {
      for (size_t index = 0; index < word.size(); ++index) {
        for (char letter : alphabet) {
          if (letter == word[index]) continue;
          // Generated rather than looked up: a fixed amount of work per word
          // instead of a comparison against every other word.
          string candidate = word;
          candidate[index] = letter;
          if (candidate == end) return steps;
          if (allowed.count(candidate) && !seen.count(candidate)) {
            seen.insert(candidate);
            nxt.insert(candidate);
          }
        }
      }
    }
    frontier = nxt;
  }
  return 0;
}
""",
        """
public class Solution
{
    public static int LadderLength(string begin, string end, string[] words)
    {
        if (begin == end) return 1;
        var allowed = new System.Collections.Generic.HashSet<string>(words);
        if (!allowed.Contains(end)) return 0;
        const string alphabet = "abcdefghijklmnopqrstuvwxyz";
        var frontier = new System.Collections.Generic.HashSet<string> { begin };
        var seen = new System.Collections.Generic.HashSet<string> { begin };
        int steps = 1;
        while (frontier.Count > 0)
        {
            steps++;
            var next = new System.Collections.Generic.HashSet<string>();
            foreach (string word in frontier)
            {
                for (int index = 0; index < word.Length; index++)
                    foreach (char letter in alphabet)
                    {
                        if (letter == word[index]) continue;
                        var candidate = word.ToCharArray();
                        candidate[index] = letter;
                        string attempt = new string(candidate);
                        if (attempt == end) return steps;
                        if (allowed.Contains(attempt) && !seen.Contains(attempt))
                        {
                            seen.Add(attempt);
                            next.Add(attempt);
                        }
                    }
            }
            frontier = next;
        }
        return 0;
    }
}
""",
        """
public class Solution {
    public static int ladderLength(String begin, String end, String[] words) {
        if (begin.equals(end)) return 1;
        java.util.Set<String> allowed = new java.util.HashSet<>(java.util.Arrays.asList(words));
        if (!allowed.contains(end)) return 0;
        final String alphabet = "abcdefghijklmnopqrstuvwxyz";
        java.util.Set<String> frontier = new java.util.HashSet<>();
        frontier.add(begin);
        java.util.Set<String> seen = new java.util.HashSet<>();
        seen.add(begin);
        int steps = 1;
        while (!frontier.isEmpty()) {
            steps++;
            java.util.Set<String> next = new java.util.HashSet<>();
            for (String word : frontier) {
                for (int index = 0; index < word.length(); index++) {
                    for (char letter : alphabet.toCharArray()) {
                        if (letter == word.charAt(index)) continue;
                        String candidate = word.substring(0, index) + letter
                                         + word.substring(index + 1);
                        if (candidate.equals(end)) return steps;
                        if (allowed.contains(candidate) && !seen.contains(candidate)) {
                            seen.add(candidate);
                            next.add(candidate);
                        }
                    }
                }
            }
            frontier = next;
        }
        return 0;
    }
}
"""),
      position=71, source=LC, sourceId=127,
      sourceNote="LeetCode 127 (Hard). Breadth first is the algorithm, not an optimisation: the first hit is the shortest ladder. Checking the end word is on the list first is the part that is easy to miss."),

    q("g-basic-calculator", "Basic Calculator", STRETCH, [ALGO, "stack", SM],
      "Calculate",
      "Have the function Calculate(str) return the value of an arithmetic "
      "expression using + and - with parentheses and whole numbers, ignoring "
      "spaces. So 1 + 2 is 3, 2-1 + 2 is 3, and (1+(4+5+2)-3)+(6+8) is 23. A "
      "minus may also apply to a parenthesised group, so -(2+3) is -5. There "
      "are no other operators.\n\nThere is no multiplication, so the answer "
      "is a running total, and the only thing that is hard is the parentheses. "
      "Two numbers on a stack do it: the total accumulated outside the current "
      "group, and the sign that total is to be added with.\n\nOn an opening "
      "bracket both are pushed and the running total restarts at zero, so the "
      "group inside is computed on its own. On a closing bracket the running "
      "total is multiplied by the saved sign and added to the saved total, and "
      "the stack pops.\n\nThe detail that trips people up is a minus with "
      "nothing in front of it, as in -(2+3). There is no number to subtract, so "
      "the sign is stored on its own and the zero that precedes it simply "
      "contributes nothing. That is why the sign is kept apart from the number "
      "rather than being read straight off the character.",
      (["str"], [STR]),
      [c(["1 + 2"], 3, INT),
       c([" 2-1 + 2 "], 3, INT),
       c(["(1+(4+5+2)-3)+(6+8)"], 23, INT),
       c(["-2+ 6"], 4, INT),
       c(["-(2+3)"], -5, INT),
       c(["1-(2+3)"], -4, INT),
       c(["2-(5-6)"], 3, INT),
       c(["10-(5+6)"], -1, INT),
       c(["(1)"], 1, INT),
       c(["2147483647"], 2147483647, INT)],
      S('''def Calculate(str):
    total = 0
    sign = 1
    stack = []
    number = 0
    have_digit = False
    for character in str:
        if character.isdigit():
            number = number * 10 + int(character)
            have_digit = True
        elif character in "+-":
            if have_digit:
                total += sign * number
            number = 0
            have_digit = False
            # A minus with no number in front of it -- as in -(2+3) -- just
            # sets the sign; the zero before it contributes nothing.
            sign = 1 if character == "+" else -1
        elif character == "(":
            # Save what is outside the group and start the group from zero.
            stack.append(total)
            stack.append(sign)
            total = 0
            sign = 1
        elif character == ")":
            if have_digit:
                total += sign * number
            number = 0
            have_digit = False
            outer_sign = stack.pop()
            outer_total = stack.pop()
            total = outer_total + outer_sign * total
            sign = 1
    if have_digit:
        total += sign * number
    return total
''',
        """
int Calculate(const string& str) {
  // long long, so a run of digits cannot overflow before the end.
  long long total = 0, sign = 1, number = 0;
  bool have_digit = false;
  vector<long long> stack;
  for (char character : str) {
    if (character >= '0' && character <= '9') {
      number = number * 10 + (character - '0');
      have_digit = true;
    } else if (character == '+' || character == '-') {
      if (have_digit) total += sign * number;
      number = 0;
      have_digit = false;
      sign = (character == '+') ? 1 : -1;
    } else if (character == '(') {
      // Save what is outside the group; the group itself starts from zero.
      stack.push_back(total);
      stack.push_back(sign);
      total = 0;
      sign = 1;
    } else if (character == ')') {
      if (have_digit) total += sign * number;
      number = 0;
      have_digit = false;
      long long outer_sign = stack.back(); stack.pop_back();
      long long outer_total = stack.back(); stack.pop_back();
      total = outer_total + outer_sign * total;
      sign = 1;
    }
  }
  if (have_digit) total += sign * number;
  return (int)total;
}
""",
        """
public class Solution
{
    public static int Calculate(string str)
    {
        // long, so a run of digits cannot overflow before the end.
        long total = 0, sign = 1, number = 0;
        bool haveDigit = false;
        var stack = new System.Collections.Generic.Stack<long>();
        foreach (char character in str)
        {
            if (character >= '0' && character <= '9')
            {
                number = number * 10 + (character - '0');
                haveDigit = true;
            }
            else if (character == '+' || character == '-')
            {
                if (haveDigit) total += sign * number;
                number = 0;
                haveDigit = false;
                sign = (character == '+') ? 1 : -1;
            }
            else if (character == '(')
            {
                stack.Push(total);
                stack.Push(sign);
                total = 0;
                sign = 1;
            }
            else if (character == ')')
            {
                if (haveDigit) total += sign * number;
                number = 0;
                haveDigit = false;
                long outerSign = stack.Pop();
                long outerTotal = stack.Pop();
                total = outerTotal + outerSign * total;
                sign = 1;
            }
        }
        if (haveDigit) total += sign * number;
        return (int)total;
    }
}
""",
        """
public class Solution {
    public static int calculate(String str) {
        long total = 0, sign = 1, number = 0;
        boolean haveDigit = false;
        java.util.Deque<Long> stack = new java.util.ArrayDeque<>();
        for (int i = 0; i < str.length(); i++) {
            char character = str.charAt(i);
            if (character >= '0' && character <= '9') {
                number = number * 10 + (character - '0');
                haveDigit = true;
            } else if (character == '+' || character == '-') {
                if (haveDigit) total += sign * number;
                number = 0;
                haveDigit = false;
                sign = (character == '+') ? 1 : -1;
            } else if (character == '(') {
                // An ArrayDeque pushes and pops at the head, so the pair is
                // pushed sign first and popped total first. Reversing that
                // silently swaps the two and every parenthesised group comes
                // out with the wrong sign.
                // first, then the sign it gets applied with.
                stack.push(sign);
                stack.push(total);
                total = 0;
                sign = 1;
            } else if (character == ')') {
                if (haveDigit) total += sign * number;
                number = 0;
                haveDigit = false;
                long outerTotal = stack.pop();
                long outerSign = stack.pop();
                total = outerTotal + outerSign * total;
                sign = 1;
            }
        }
        if (haveDigit) total += sign * number;
        return (int) total;
    }
}
"""),
      position=72, source=LC, sourceId=224,
      sourceNote="LeetCode 224 (Hard). Keeping the sign separate from the number is what makes -(2+3) work: there is no number for that minus to attach to."),

    q("g-max-profit-jobs", "Maximum Profit in Job Scheduling",
      STRETCH, [DP, "sorting"], "MaxProfitInJobScheduling",
      "Have the function MaxProfitInJobScheduling(startTime, endTime, profit) "
      "take three lists of the same length describing jobs -- each job starts "
      "at startTime[i], ends at endTime[i] and pays profit[i] -- and return the "
      "largest total profit from jobs that can all be done.\n\nA job that ends "
      "at 5 and a job that starts at 5 are compatible: a job can start the "
      "moment the previous one ends. A job that ends at 5 and one that starts at "
      "4 are not.\n\nSorting the jobs by start time and asking, for each one, "
      "the best profit available before it, is one way. Sorting by end time and "
      "asking, for each one, whether to take it or skip it, is the other, and "
      "the second is the one that works without a search.\n\nSo: sort by end "
      "time, and keep one number per job -- the most profit obtainable from the "
      "jobs before it. For each job, the answer is either the previous job's "
      "answer, or the profit of every compatible earlier job plus this one. "
      "The half-open rule is the one detail worth being careful about: the "
      "compatibility test is that an earlier job's end is at or before this "
      "job's start, not strictly before it.",
      (["startTime", "endTime", "profit"], [ARR, ARR, ARR]),
      [c([[1, 2, 3, 3], [3, 4, 5, 6], [2, 7, 9, 3]], 11, INT),
       c([[1, 2, 3], [2, 3, 5], [0, 6, 8]], 14, INT),
       c([[1, 2, 3], [2, 3, 4], [3, 4, 5]], 12, INT),
       c([[1, 2, 1], [2, 3, 2], [3, 4, 1]], 7, INT)],
      S('''def MaxProfitInJobScheduling(startTime, endTime, profit):
    jobs = sorted(zip(startTime, endTime, profit))
    # best[i] is the most profit from the first i jobs in end-time order.
    best = [0] * (len(jobs) + 1)
    for i, (start, end, money) in enumerate(jobs):
        # The highest-numbered job that finishes at or before this one starts.
        # Jobs are sorted by start, so the scan can stop at the first job that
        # starts too late -- and the test is <= because a job may start the
        # moment the previous one ends.
        earlier = 0
        for j, (other_start, other_end, _) in enumerate(jobs):
            if other_start > start:
                break
            if other_end <= start:
                earlier = max(earlier, j + 1)
        best[i + 1] = max(best[i], best[earlier] + money)
    return best[len(jobs)]
''',
        """
int MaxProfitInJobScheduling(const vector<int>& startTime, const vector<int>& endTime,
                             const vector<int>& profit) {
  vector<array<int, 3>> jobs;
  for (size_t i = 0; i < startTime.size(); ++i)
    jobs.push_back({startTime[i], endTime[i], profit[i]});
  sort(jobs.begin(), jobs.end());
  // best[i] is the most profit from the first i jobs in end-time order.
  vector<long long> best(jobs.size() + 1, 0);
  for (size_t i = 0; i < jobs.size(); ++i) {
    size_t earlier = 0;
    for (size_t j = 0; j < jobs.size(); ++j) {
      if (jobs[j][0] > jobs[i][0]) break;
      // <= not <: a job may start the moment the previous one ends.
      if (jobs[j][1] <= jobs[i][0]) earlier = max(earlier, j + 1);
    }
    best[i + 1] = max(best[i], best[earlier] + jobs[i][2]);
  }
  return (int)best[jobs.size()];
}
""",
        """
public class Solution
{
    public static int MaxProfitInJobScheduling(int[] startTime, int[] endTime, int[] profit)
    {
        int n = startTime.Length;
        var jobs = new System.Collections.Generic.List<int[]>();
        for (int i = 0; i < n; i++) jobs.Add(new int[] { startTime[i], endTime[i], profit[i] });
        jobs.Sort((a, b) =>
        {
            if (a[0] != b[0]) return a[0].CompareTo(b[0]);
            return a[1].CompareTo(b[1]);
        });
        // best[i] is the most profit from the first i jobs in end-time order.
        var best = new long[n + 1];
        for (int i = 0; i < n; i++)
        {
            int earlier = 0;
            for (int j = 0; j < n; j++)
            {
                if (jobs[j][0] > jobs[i][0]) break;
                // <= not <: a job may start the moment the previous one ends.
                if (jobs[j][1] <= jobs[i][0]) earlier = Math.Max(earlier, j + 1);
            }
            best[i + 1] = Math.Max(best[i], best[earlier] + jobs[i][2]);
        }
        return (int)best[n];
    }
}
""",
        """
public class Solution {
    public static int maxProfitInJobScheduling(int[] startTime, int[] endTime, int[] profit) {
        int n = startTime.length;
        int[][] jobs = new int[n][];
        for (int i = 0; i < n; i++) jobs[i] = new int[] { startTime[i], endTime[i], profit[i] };
        java.util.Arrays.sort(jobs, (a, b) -> a[0] != b[0] ? Integer.compare(a[0], b[0])
                                                          : Integer.compare(a[1], b[1]));
        // best[i] is the most profit from the first i jobs in end-time order.
        long[] best = new long[n + 1];
        for (int i = 0; i < n; i++) {
            int earlier = 0;
            for (int j = 0; j < n; j++) {
                if (jobs[j][0] > jobs[i][0]) break;
                // <= not <: a job may start the moment the previous one ends.
                if (jobs[j][1] <= jobs[i][0]) earlier = Math.max(earlier, j + 1);
            }
            best[i + 1] = Math.max(best[i], best[earlier] + jobs[i][2]);
        }
        return (int) best[n];
    }
}
"""),
      position=73, source=LC, sourceId=1235,
      sourceNote="LeetCode 1235 (Hard). The compatibility test is end <= start, not end < start; a job starting the moment another ends is a legal schedule."),

    q("g-merge-k-sorted", "Merge k Sorted Lists", STRETCH, [ALGO, "heaps", "lists"],
      "MergeKSorted",
      "Have the function MergeKSorted(lists) take a list of lists, each already "
      "in ascending order, and return one list holding all of their values in "
      "ascending order.\n\n" + MATRIX_NOTE.replace(
          "A matrix arrives as a list of rows, each row a list of the same length, "
          "and is returned the same way.",
          "The argument arrives as a list of rows and the answer is a single flat "
          "list, so the two are shaped differently: [[1, 4, 5], [1, 3, 4]] in and "
          "[1, 1, 3, 4, 4, 5] out.") +
      "\n\nThree ways to do it, in increasing order of interest. Concatenate "
      "and sort, which is simple and uses that each row is already sorted not "
      "at all. Take the smallest remaining first element of each row, which is a "
      "merge of k sorted runs and needs no comparisons against rows that are not "
      "the smallest. Or push the current head of every row onto a heap and pop "
      "the smallest, refilling from the row it came from -- that is linear in the "
      "total once the heap is built, and it is the version that scales when k is "
      "large.\n\nWith rows of different lengths a row can run out early, so the "
      "head that was taken from it has to be replaced with the next value from "
      "that same row, or the row's remaining values are simply lost.",
      (["lists"], [MATRIX]),
      [c([[[1, 4, 5], [1, 3, 4], [2, 6]]], [1, 1, 2, 3, 4, 4, 5, 6], LIST),
       c([[[-1], [0], [1]]], [-1, 0, 1], LIST),
       c([[[1]]], [1], LIST),
       c([[[1, 2, 3], []]], [1, 2, 3], LIST),
       c([[[], []]], [], LIST)],
      S('''def MergeKSorted(lists):
    # A heap of the current head of each row. Popping the smallest and pushing
    # the next value from the row it came from keeps every row in order, and
    # costs one comparison per value after the heads are in.
    import heapq
    heap = []
    for index, row in enumerate(lists):
        if row:
            heapq.heappush(heap, (row[0], index, 0))
    out = []
    while heap:
        value, index, position = heapq.heappop(heap)
        out.append(value)
        if position + 1 < len(lists[index]):
            heapq.heappush(heap, (lists[index][position + 1], index, position + 1))
    return out
''',
        """
vector<int> MergeKSorted(const vector<vector<int>>& lists) {
  // A heap of the current head of each row. Popping the smallest and pushing
  // the next value from the row it came from keeps every row in order.
  vector<int> out;
  vector<array<int, 3>> heap;  // (value, row, position)
  for (size_t index = 0; index < lists.size(); ++index)
    if (!lists[index].empty()) heap.push_back({lists[index][0], (int)index, 0});
  auto later = [](const array<int, 3>& a, const array<int, 3>& b) {
    if (a[0] != b[0]) return a[0] > b[0];
    return a[1] > b[1];
  };
  make_heap(heap.begin(), heap.end(), later);
  while (!heap.empty()) {
    pop_heap(heap.begin(), heap.end(), later);
    array<int, 3> top = heap.back();
    heap.pop_back();
    out.push_back(top[0]);
    int index = top[1], position = top[2];
    if (position + 1 < (int)lists[index].size()) {
      heap.push_back({lists[index][position + 1], index, position + 1});
      push_heap(heap.begin(), heap.end(), later);
    }
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[] MergeKSorted(int[][] lists)
    {
        // A heap of the current head of each row. The value is the *priority*,
        // not merely part of the element: a PriorityQueue given a null priority
        // falls back to insertion order and comes out as the rows laid end to
        // end. The element carries the row and position so equal values from
        // different rows can still be told apart.
        var heap = new System.Collections.Generic.PriorityQueue<(int row, int pos), long>();
        for (int index = 0; index < lists.Length; index++)
            if (lists[index].Length > 0) heap.Enqueue((index, 0), lists[index][0]);
        var outp = new System.Collections.Generic.List<int>();
        while (heap.Count > 0)
        {
            // Dequeue hands back the element -- the row and position -- and
            // the value came off as the priority, so it is read from the row.
            var top = heap.Dequeue();
            outp.Add(lists[top.row][top.pos]);
            int next = top.pos + 1;
            if (next < lists[top.row].Length)
                heap.Enqueue((top.row, next), lists[top.row][next]);
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[] mergeKSorted(int[][] lists) {
        // A heap of the current head of each row. The row index travels with
        // the value so that two equal values from different rows still order.
        java.util.PriorityQueue<int[]> heap =
            new java.util.PriorityQueue<>((a, b) -> {
                if (a[0] != b[0]) return Integer.compare(a[0], b[0]);
                return Integer.compare(a[1], b[1]);
            });
        for (int index = 0; index < lists.length; index++)
            if (lists[index].length > 0) heap.add(new int[] { lists[index][0], index, 0 });
        int[] out = new int[total(lists)];
        int at = 0;
        while (!heap.isEmpty()) {
            int[] top = heap.poll();
            out[at++] = top[0];
            int next = top[2] + 1;
            if (next < lists[top[1]].length)
                heap.add(new int[] { lists[top[1]][next], top[1], next });
        }
        return out;
    }

    private static int total(int[][] lists) {
        int sum = 0;
        for (int[] row : lists) sum += row.length;
        return sum;
    }
}
"""),
      position=74, source=LC, sourceId=23,
      sourceNote="LeetCode 23 (Hard). The row index has to travel with the value in the heap, or two equal values from different rows compare unequal and the order is wrong."),

    q("g-largest-rectangle", "Largest Rectangle in Histogram", STRETCH,
      [ALGO, "stacks", "monotonic stack"], "LargestRectangle",
      "Have the function LargestRectangle(heights) take a list of bar heights and "
      "return the largest rectangle that fits under the bars and above the "
      "ground, and the empty list has no rectangle.\n\nThe height of a "
      "rectangle is its shortest bar, and its width is how many bars are at "
      "least that tall. So a bar's real question is how far the bars reach on "
      "each side without dropping below it.\n\nA stack of bars with increasing "
      "heights answers that. Push a bar, and when a shorter one arrives it "
      "closes every taller bar on top of the stack: that bar cannot extend past "
      "the new one, and it can extend to just past whatever is now on top of the "
      "stack, so its area is its height times the distance between those two. "
      "Pop and repeat.\n\nA bar of zero at the end finishes the stack off, and "
      "so does any bar shorter than the whole stack. A stack of heights alone "
      "does not know where each bar started, so the indices are what gets "
      "pushed.\n\nEvery bar is pushed once and popped at most once, which is "
      "where the linear time comes from.",
      (["heights"], [ARR]),
      [c([[2, 1, 5, 6, 2, 3]], 10, INT),
       c([[5, 4, 3, 2, 1]], 9, INT),
       c([[2, 1, 2]], 3, INT),
       c([[1, 1, 1, 1]], 4, INT),
       c([[2, 4]], 4, INT),
       c([[]], 0, INT)],
      S('''def LargestRectangle(heights):
    best = 0
    # Indices, with the heights they point at in increasing order. A shorter
    # bar arriving pops every taller one, which is how each bar learns how far
    # it can reach.
    stack = []
    for index in range(len(heights) + 1):
        # A bar of zero past the end finishes off whatever is left.
        current = heights[index] if index < len(heights) else 0
        while stack and heights[stack[-1]] >= current:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (index - left - 1))
        stack.append(index)
    return best
''',
        """
int LargestRectangle(const vector<int>& heights) {
  int best = 0;
  // Indices whose heights are in increasing order. A shorter bar arriving pops
  // every taller one, which is how each bar learns how far it can reach.
  vector<size_t> stack;
  for (size_t index = 0; index <= heights.size(); ++index) {
    // A bar of zero past the end finishes off whatever is left on the stack.
    int current = index < heights.size() ? heights[index] : 0;
    while (!stack.empty() && heights[stack.back()] >= current) {
      int height = heights[stack.back()];
      stack.pop_back();
      size_t left = stack.empty() ? (size_t)-1 : stack.back();
      // Width runs from just past the new top of the stack to this index.
      best = max(best, height * (int)(index - left - 1));
    }
    stack.push_back(index);
  }
  return best;
}
""",
        """
public class Solution
{
    public static int LargestRectangle(int[] heights)
    {
        int best = 0;
        // Indices whose heights are in increasing order.
        var stack = new System.Collections.Generic.Stack<int>();
        for (int index = 0; index <= heights.Length; index++)
        {
            // A bar of zero past the end finishes off whatever is left.
            int current = index < heights.Length ? heights[index] : 0;
            while (stack.Count > 0 && heights[stack.Peek()] >= current)
            {
                int height = heights[stack.Pop()];
                int left = stack.Count > 0 ? stack.Peek() : -1;
                // Width runs from just past the new top to this index.
                best = Math.Max(best, height * (index - left - 1));
            }
            stack.Push(index);
        }
        return best;
    }
}
""",
        """
public class Solution {
    public static int largestRectangle(int[] heights) {
        int best = 0;
        // Indices whose heights are in increasing order.
        java.util.Deque<Integer> stack = new java.util.ArrayDeque<>();
        for (int index = 0; index <= heights.length; index++) {
            int current = index < heights.length ? heights[index] : 0;
            while (!stack.isEmpty() && heights[stack.peek()] >= current) {
                int height = heights[stack.pop()];
                int left = stack.isEmpty() ? -1 : stack.peek();
                best = Math.max(best, height * (index - left - 1));
            }
            stack.push(index);
        }
        return best;
    }
}
"""),
      position=75, source=LC, sourceId=84,
      sourceNote="LeetCode 84 (Hard). Each bar is pushed once and popped at most once, and the width comes from the gap the pop leaves behind -- that is where the linear time comes from."),
]
