#!/usr/bin/env python3
"""Grind 75, wave 2: the rest of the easy block.

Positions 13-22. Contains Duplicate (23) and Maximum Subarray (24) are already
in the catalogue from the Coderbyte set, so the run picks up again at 25.

First Bad Version is the one adaptation in either wave worth flagging. The
original hands you an opaque `isBadVersion(n)` predicate and refuses to let you
invert it, which is the entire lesson. There is no opaque predicate to pass
across a function boundary here, so the good/bad flags arrive as a list --
still monotonic, still not invertible into arithmetic, so binary search is
still the answer rather than a scan.
"""

from __future__ import annotations

from grind75_common import (ALGO, ARR, BOOL, DP, INT, LC, LINKED_LIST_NOTE, LIST, SEARCH,
                            SM, STRETCH, STR, TREE, TREE_NOTE, c, q, S)

QUESTIONS = [
    q("g-first-bad-version", "First Bad Version", STRETCH, [SEARCH, ALGO], "FirstBadVersion",
      "Have the function FirstBadVersion(versions) take a list of 0s and 1s, where 0 "
      "marks a version that works and 1 marks a version that is broken, and return the "
      "index of the first broken version. Every working version is known to come before "
      "every broken one. Return -1 if no version is broken.\n\nThat ordering is what makes "
      "this worth binary search rather than a scan: the moment you find a 0, everything "
      "to its left is a 0 too, so half the list is ruled out in a single step.",
      (["versions"], [ARR]),
      [c([[0, 0, 1, 1, 1]], 2, INT), c([[0, 0, 0]], -1, INT), c([[1]], 0, INT),
       c([[0]], -1, INT), c([[0, 1]], 1, INT), c([[]], -1, INT)],
      S('''
def FirstBadVersion(versions):
    low, high = 0, len(versions)
    while low < high:
        mid = low + (high - low) // 2
        if versions[mid] == 0:
            low = mid + 1
        else:
            high = mid
    return low if low < len(versions) else -1
''',
        """
int FirstBadVersion(const vector<int>& versions) {
  int low = 0, high = (int)versions.size();
  while (low < high) {
    int mid = low + (high - low) / 2;
    if (versions[mid] == 0) low = mid + 1; else high = mid;
  }
  return low < (int)versions.size() ? low : -1;
}
""",
        """
public class Solution
{
    public static int FirstBadVersion(int[] versions)
    {
        int low = 0, high = versions.Length;
        while (low < high)
        {
            int mid = low + (high - low) / 2;
            if (versions[mid] == 0) low = mid + 1; else high = mid;
        }
        return low < versions.Length ? low : -1;
    }
}
""",
        """
public class Solution {
    public static int firstBadVersion(int[] versions) {
        int low = 0, high = versions.length;
        while (low < high) {
            int mid = low + (high - low) / 2;
            if (versions[mid] == 0) low = mid + 1; else high = mid;
        }
        return low < versions.length ? low : -1;
    }
}
"""),
      position=14, source=LC, sourceId=278,
      sourceNote="LeetCode 278 (Easy). The original hides the test behind an API call; here the flags arrive as a list, still monotonic, still not invertible."),

    q("g-ransom-note", "Ransom Note", STRETCH, [SM, "hash map"], "CanConstructNote",
      "Have the function CanConstructNote(magazine, note) take two strings and return the "
      "boolean true if every character of note can be taken from magazine, using each "
      "character of magazine at most once, otherwise return false. Order does not matter, "
      "and unused characters are allowed to go to waste.",
      (["magazine", "note"], [STR, STR]),
      [c(["aab", "aab"], True, BOOL), c(["aab", "aaa"], False, BOOL),
       c(["a", "b"], False, BOOL), c(["", "z"], False, BOOL),
       c(["aaa", ""], True, BOOL)],
      S('''
def CanConstructNote(magazine, note):
    counts = {}
    for ch in magazine:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in note:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] -= 1
    return True
''',
        """
bool CanConstructNote(const string& magazine, const string& note) {
  map<char, int> counts;
  for (char ch : magazine) counts[ch]++;
  for (char ch : note) {
    auto found = counts.find(ch);
    if (found == counts.end() || found->second == 0) return false;
    found->second--;
  }
  return true;
}
""",
        """
using System.Collections.Generic;

public class Solution
{
    public static bool CanConstructNote(string magazine, string note)
    {
        var counts = new Dictionary<char, int>();
        foreach (char ch in magazine)
        {
            counts.TryGetValue(ch, out int seen);
            counts[ch] = seen + 1;
        }
        foreach (char ch in note)
        {
            if (!counts.TryGetValue(ch, out int left) || left == 0) return false;
            counts[ch] = left - 1;
        }
        return true;
    }
}
""",
        """
public class Solution {
    public static boolean canConstructNote(String magazine, String note) {
        java.util.Map<Character, Integer> counts = new java.util.HashMap<>();
        for (char ch : magazine.toCharArray())
            counts.merge(ch, 1, Integer::sum);
        for (char ch : note.toCharArray()) {
            Integer left = counts.get(ch);
            if (left == null || left == 0) return false;
            counts.put(ch, left - 1);
        }
        return true;
    }
}
"""),
      position=15, source=LC, sourceId=383,
      sourceNote="LeetCode 383 (Easy). Spending from a count is what makes duplicates behave."),

    q("g-climbing-stairs", "Climbing Stairs", STRETCH, [DP, ALGO], "ClimbStairs",
      "Have the function ClimbStairs(n) take a number of stairs and return how many "
      "distinct ways there are to climb them taking either one or two stairs at a time. "
      "Zero stairs has one way: do nothing.\n\nThe answer is the Fibonacci sequence, and "
      "once you see that, the interesting question becomes whether you need the whole "
      "table to produce a single number.",
      (["n"], [INT]),
      [c([2], 2, INT), c([3], 3, INT), c([1], 1, INT), c([5], 8, INT),
       c([10], 89, INT), c([0], 1, INT)],
      S('''
def ClimbStairs(n):
    previous, current = 1, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous
''',
        """
int ClimbStairs(int n) {
  int previous = 1, current = 1;
  for (int i = 0; i < n; ++i) {
    int next = previous + current;
    previous = current;
    current = next;
  }
  return previous;
}
""",
        """
public class Solution
{
    public static int ClimbStairs(int n)
    {
        int previous = 1, current = 1;
        for (int i = 0; i < n; i++)
        {
            int next = previous + current;
            previous = current;
            current = next;
        }
        return previous;
    }
}
""",
        """
public class Solution {
    public static int climbStairs(int n) {
        int previous = 1, current = 1;
        for (int i = 0; i < n; i++) {
            int next = previous + current;
            previous = current;
            current = next;
        }
        return previous;
    }
}
"""),
      position=16, source=LC, sourceId=70,
      sourceNote="LeetCode 70 (Easy). Two variables beat a table, and the prompt says why."),

    q("g-longest-palindrome", "Longest Palindrome", STRETCH, [SM, "hash map"], "LongestPalindrome",
      "Have the function LongestPalindrome(s) take a string and return the length of the "
      "longest palindrome that can be built from its characters, each character used at "
      "most as often as it appears. Return 0 for an empty string.\n\nEvery matching pair "
      "goes in, and at most one unpaired character can sit in the middle.",
      (["s"], [STR]),
      [c(["abccccdd"], 7, INT), c(["a"], 1, INT), c(["bb"], 2, INT),
       c(["abc"], 1, INT), c([""], 0, INT), c(["aabb"], 4, INT)],
      S('''
def LongestPalindrome(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    pairs = sum(count - count % 2 for count in counts.values())
    return pairs + (1 if pairs < len(s) else 0)
''',
        """
int LongestPalindrome(const string& s) {
  map<char, int> counts;
  for (char ch : s) counts[ch]++;
  int length = 0;
  for (const auto& entry : counts) length += entry.second - entry.second % 2;
  return length < (int)s.size() ? length + 1 : length;
}
""",
        """
using System.Collections.Generic;

public class Solution
{
    public static int LongestPalindrome(string s)
    {
        var counts = new Dictionary<char, int>();
        foreach (char ch in s)
        {
            counts.TryGetValue(ch, out int seen);
            counts[ch] = seen + 1;
        }
        int length = 0;
        foreach (int seen in counts.Values) length += seen - seen % 2;
        return length < s.Length ? length + 1 : length;
    }
}
""",
        """
public class Solution {
    public static int longestPalindrome(String s) {
        java.util.Map<Character, Integer> counts = new java.util.HashMap<>();
        for (char ch : s.toCharArray()) counts.merge(ch, 1, Integer::sum);
        int length = 0;
        for (int seen : counts.values()) length += seen - seen % 2;
        return length < s.length() ? length + 1 : length;
    }
}
"""),
      position=17, source=LC, sourceId=409,
      sourceNote="LeetCode 409 (Easy). The lone centre character is the only subtlety."),

    q("g-reverse-linked-list", "Reverse Linked List", STRETCH, [ALGO, "linked list"],
      "ReverseLinkedList",
      "Have the function ReverseLinkedList(head) take a linked list and return the same "
      "values in the opposite order, so that what was the tail is now the head.\n\n"
      + LINKED_LIST_NOTE +
      "\n\nRelinking the nodes one at a time is the exercise the original sets. Here you "
      "hold the values, so the honest route is the same one a fresh node per step would "
      "take: walk what you have and put each next value on the front.",
      (["head"], [LIST]),
      [c([[1, 2, 3, 4, 5]], [5, 4, 3, 2, 1], LIST), c([[1]], [1], LIST),
       c([[]], [], LIST), c([[1, 2]], [2, 1], LIST), c([[7, 7, 7]], [7, 7, 7], LIST)],
      S('''
def ReverseLinkedList(head):
    out = []
    for value in head:
        out.insert(0, value)
    return out
''',
        """
vector<int> ReverseLinkedList(const vector<int>& head) {
  vector<int> out;
  for (int value : head) out.insert(out.begin(), value);
  return out;
}
""",
        """
using System.Collections.Generic;

public class Solution
{
    public static int[] ReverseLinkedList(int[] head)
    {
        var outp = new List<int>();
        foreach (int value in head) outp.Insert(0, value);
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[] reverseLinkedList(int[] head) {
        java.util.List<Integer> outp = new java.util.ArrayList<>();
        for (int value : head) outp.add(0, value);
        int[] reversed = new int[outp.size()];
        for (int i = 0; i < reversed.length; i++) reversed[i] = outp.get(i);
        return reversed;
    }
}
"""),
      position=18, source=LC, sourceId=206,
      sourceNote="LeetCode 206 (Easy). Front-insertion is what a head pointer would be doing."),

    q("g-majority-element", "Majority Element", STRETCH, [ALGO, "divide and conquer"],
      "MajorityElement",
      "Have the function MajorityElement(nums) take a list of integers and return the one "
      "that appears more than half the time. A majority is guaranteed to exist, so there "
      "is always exactly one answer.\n\nThe guarantee is what makes this tractable: pairing "
      "off elements that differ cancels both, and a majority survives every cancellation, "
      "so whatever is left standing is the answer. A hash map also works, and uses more "
      "memory.",
      (["nums"], [ARR]),
      [c([[3, 2, 3]], 3, INT), c([[2, 2, 1, 1, 1, 2, 2]], 2, INT),
       c([[1]], 1, INT), c([[1, 2]], 1, INT), c([[6, 5, 5]], 5, INT),
       c([[1, 1, 2]], 1, INT)],
      S('''
def MajorityElement(nums):
    candidate = 0
    count = 0
    for value in nums:
        if count == 0:
            candidate = value
        count += 1 if value == candidate else -1
    return candidate
''',
        """
int MajorityElement(const vector<int>& nums) {
  int candidate = 0, count = 0;
  for (int value : nums) {
    if (count == 0) candidate = value;
    count += value == candidate ? 1 : -1;
  }
  return candidate;
}
""",
        """
public class Solution
{
    public static int MajorityElement(int[] nums)
    {
        int candidate = 0, count = 0;
        foreach (int value in nums)
        {
            if (count == 0) candidate = value;
            count += value == candidate ? 1 : -1;
        }
        return candidate;
    }
}
""",
        """
public class Solution {
    public static int majorityElement(int[] nums) {
        int candidate = 0, count = 0;
        for (int value : nums) {
            if (count == 0) candidate = value;
            count += value == candidate ? 1 : -1;
        }
        return candidate;
    }
}
"""),
      position=19, source=LC, sourceId=169,
      sourceNote="LeetCode 169 (Easy). Boyer-Moore: cancellation leaves the majority standing."),

    q("g-add-binary", "Add Binary", STRETCH, [SM, "math fundamentals"], "AddBinary",
      "Have the function AddBinary(a, b) take two strings of 0s and 1s and return their sum "
      "as a binary string. Neither input carries leading zeros unless the input is itself "
      "\"0\".\n\nConvert to an integer only if you can prove it will not overflow. Carrying "
      "by hand is the same amount of work and does not care how long the strings are.",
      (["a", "b"], [STR, STR]),
      [c(["11", "1"], "100", STR), c(["1010", "1011"], "10101", STR),
       c(["0", "0"], "0", STR), c(["1", "1"], "10", STR),
       c(["1111", "1111"], "11110", STR), c(["0", "1"], "1", STR)],
      S('''
def AddBinary(a, b):
    i, j, carry = len(a) - 1, len(b) - 1, 0
    digits = []
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i]); i -= 1
        if j >= 0:
            total += int(b[j]); j -= 1
        digits.append(str(total % 2))
        carry = total // 2
    return "".join(reversed(digits)) or "0"
''',
        """
string AddBinary(const string& a, const string& b) {
  int i = (int)a.size() - 1, j = (int)b.size() - 1, carry = 0;
  string out;
  while (i >= 0 || j >= 0 || carry) {
    int total = carry;
    if (i >= 0) total += a[i--] - '0';
    if (j >= 0) total += b[j--] - '0';
    out.push_back((char)('0' + total % 2));
    carry = total / 2;
  }
  reverse(out.begin(), out.end());
  return out.empty() ? "0" : out;
}
""",
        """
public class Solution
{
    public static string AddBinary(string a, string b)
    {
        int i = a.Length - 1, j = b.Length - 1, carry = 0;
        var digits = new System.Text.StringBuilder();
        while (i >= 0 || j >= 0 || carry != 0)
        {
            int total = carry;
            if (i >= 0) total += a[i--] - '0';
            if (j >= 0) total += b[j--] - '0';
            digits.Append((char)('0' + total % 2));
            carry = total / 2;
        }
        char[] outp = digits.ToString().ToCharArray();
        System.Array.Reverse(outp);
        return outp.Length == 0 ? "0" : new string(outp);
    }
}
""",
        """
public class Solution {
    public static String addBinary(String a, String b) {
        int i = a.length() - 1, j = b.length() - 1, carry = 0;
        StringBuilder digits = new StringBuilder();
        while (i >= 0 || j >= 0 || carry != 0) {
            int total = carry;
            if (i >= 0) total += a.charAt(i--) - '0';
            if (j >= 0) total += b.charAt(j--) - '0';
            digits.append((char) ('0' + total % 2));
            carry = total / 2;
        }
        String outp = digits.reverse().toString();
        return outp.isEmpty() ? "0" : outp;
    }
}
"""),
      position=20, source=LC, sourceId=415,
      sourceNote="LeetCode 415 (Easy). Carrying by hand does not care how long the strings get."),

    q("g-diameter-binary-tree", "Diameter of a Binary Tree", STRETCH, [ALGO, "tree"],
      "DiameterOfBinaryTree",
      "Have the function DiameterOfBinaryTree(root) take a binary tree and return the "
      "number of edges on the longest path between any two nodes in it. A tree of one node "
      "has a diameter of 0, and so does the empty tree.\n\n" + TREE_NOTE +
      "\n\nThe path may start and end anywhere, not only at the root, so for every node the "
      "thing to measure is the two deepest branches hanging below it.",
      (["root"], [TREE]),
      [c([[1, 2, 3, 4, 5]], 3, INT), c([[1, 2]], 1, INT), c([[1]], 0, INT),
       c([[]], 0, INT), c([[1, 2, 3, 4, 5, 6, 7]], 4, INT)],
      S('''
def DiameterOfBinaryTree(root):
    best = 0

    def depth(node):
        nonlocal best
        if node >= len(root) or root[node] is None:
            return 0
        left = depth(2 * node + 1)
        right = depth(2 * node + 2)
        best = max(best, left + right)
        return max(left, right) + 1

    depth(0)
    return best
''',
        """
int DiameterOfBinaryTree(const vector<optional<int>>& root) {
  int best = 0;
  function<int(size_t)> depth = [&](size_t node) -> int {
    if (node >= root.size() || !root[node].has_value()) return 0;
    int left = depth(2 * node + 1);
    int right = depth(2 * node + 2);
    best = max(best, left + right);
    return max(left, right) + 1;
  };
  depth(0);
  return best;
}
""",
        """
public class Solution
{
    public static int DiameterOfBinaryTree(int?[] root)
    {
        int best = 0;
        int Depth(int node)
        {
            if (node >= root.Length || !root[node].HasValue) return 0;
            int left = Depth(2 * node + 1);
            int right = Depth(2 * node + 2);
            best = Math.Max(best, left + right);
            return Math.Max(left, right) + 1;
        }
        Depth(0);
        return best;
    }
}
""",
        """
public class Solution {
    static int[] best = { 0 };

    public static int diameterOfBinaryTree(Integer[] root) {
        best[0] = 0;
        depth(root, 0);
        return best[0];
    }

    static int depth(Integer[] root, int node) {
        if (node >= root.length || root[node] == null) return 0;
        int left = depth(root, 2 * node + 1);
        int right = depth(root, 2 * node + 2);
        best[0] = Math.max(best[0], left + right);
        return Math.max(left, right) + 1;
    }
}
"""),
      position=21, source=LC, sourceId=543,
      sourceNote="LeetCode 543 (Easy). The widest path through a node is its two deepest branches."),

    q("g-middle-linked-list", "Middle of the Linked List", STRETCH,
      [ALGO, "linked list", "two pointers"], "MiddleOfLinkedList",
      "Have the function MiddleOfLinkedList(head) take a linked list and return the value "
      "at its middle. When the list has an even number of nodes, return the value at index "
      "length/2, which is the second of the two middle values. Return -1 for the empty "
      "list.\n\n" + LINKED_LIST_NOTE +
      "\n\nOne pointer at the end of the list and one at the half-way mark gets there "
      "without counting first, which matters when counting costs a second pass.",
      (["head"], [LIST]),
      [c([[1, 2, 3, 4, 5]], 3, INT), c([[1, 2, 3, 4, 5, 6]], 4, INT),
       c([[1]], 1, INT), c([[1, 2]], 2, INT), c([[]], -1, INT)],
      S('''
def MiddleOfLinkedList(head):
    if not head:
        return -1
    slow = fast = 0
    while fast + 1 < len(head):
        slow += 1
        fast += 2
    return head[slow]
''',
        """
int MiddleOfLinkedList(const vector<int>& head) {
  if (head.empty()) return -1;
  size_t slow = 0, fast = 0;
  while (fast + 1 < head.size()) {
    slow++;
    fast += 2;
  }
  return head[slow];
}
""",
        """
public class Solution
{
    public static int MiddleOfLinkedList(int[] head)
    {
        if (head.Length == 0) return -1;
        int slow = 0, fast = 0;
        while (fast + 1 < head.Length)
        {
            slow++;
            fast += 2;
        }
        return head[slow];
    }
}
""",
        """
public class Solution {
    public static int middleOfLinkedList(int[] head) {
        if (head.length == 0) return -1;
        int slow = 0, fast = 0;
        while (fast + 1 < head.length) {
            slow++;
            fast += 2;
        }
        return head[slow];
    }
}
"""),
      position=22, source=LC, sourceId=876,
      sourceNote="LeetCode 876 (Easy). Fast and slow pointers, no counting pass."),

    q("g-maximum-depth-binary-tree", "Maximum Depth of a Binary Tree", STRETCH,
      [ALGO, "tree"], "MaxDepthOfBinaryTree",
      "Have the function MaxDepthOfBinaryTree(root) take a binary tree and return the "
      "number of levels it has. The empty tree has depth 0.\n\n" + TREE_NOTE +
      "\n\nBe aware that the encoding hands this one over: a node at index p sits at level "
      "floor(log2(p + 1)), so the depth is the level of the last occupied index and the "
      "tree never has to be walked at all. The reference below walks it anyway, because "
      "the traversal is the part you want.",
      (["root"], [TREE]),
      [c([[3, 9, 20, None, None, 15, 7]], 3, INT), c([[1, None, 2]], 2, INT),
       c([[]], 0, INT), c([[1]], 1, INT), c([[1, 2, 3, 4]], 3, INT)],
      S('''
def MaxDepthOfBinaryTree(root):
    def depth(node):
        if node >= len(root) or root[node] is None:
            return 0
        return 1 + max(depth(2 * node + 1), depth(2 * node + 2))
    return depth(0)
''',
        """
int MaxDepthOfBinaryTree(const vector<optional<int>>& root) {
  function<int(size_t)> depth = [&](size_t node) -> int {
    if (node >= root.size() || !root[node].has_value()) return 0;
    return 1 + max(depth(2 * node + 1), depth(2 * node + 2));
  };
  return depth(0);
}
""",
        """
public class Solution
{
    public static int MaxDepthOfBinaryTree(int?[] root)
    {
        int Depth(int node)
        {
            if (node >= root.Length || !root[node].HasValue) return 0;
            return 1 + Math.Max(Depth(2 * node + 1), Depth(2 * node + 2));
        }
        return Depth(0);
    }
}
""",
        """
public class Solution {
    public static int maxDepthOfBinaryTree(Integer[] root) {
        return depth(root, 0);
    }

    static int depth(Integer[] root, int node) {
        if (node >= root.length || root[node] == null) return 0;
        return 1 + Math.max(depth(root, 2 * node + 1), depth(root, 2 * node + 2));
    }
}
"""),
      position=23, source=LC, sourceId=111,
      sourceNote="LeetCode 111 (Easy). The prompt flags the shortcut the heap encoding hands you."),
]
