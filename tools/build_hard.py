#!/usr/bin/env python3
"""Harder questions, in two deliberately separate tiers.

TIER `hard`
    Shaped exactly like a Coderbyte question -- one function, a few arguments,
    a handful of cases -- but genuinely harder than the Medium tier. These are
    what a Coderbyte Hard challenge would look like. Target 5-12 minutes.

TIER `stretch`
    Real LeetCode problems, adapted to this harness. These are NOT Coderbyte-
    shaped: a LeetCode Hard runs 45 minutes to several hours, which is 15-100x
    the budget of a Coderbyte question. They are here for long-form practice
    and pattern-building, and every one is labelled so they can never be
    mistaken for assessment preparation.

Each entry carries `source` and `sourceNote` so the UI can show the provenance
honestly. Run with the self-test afterwards:

    python3 tools/build_hard.py && python3 -m cbp.selftest
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_PATH = os.path.join(ROOT, "cbp", "data", "questions.json")

STR, INT, BOOL, ARR = "string", "int", "bool", "array"
HARD, STRETCH = "hard", "stretch"
SM, MA, SEARCH, MATH, ALGO, DP = (
    "string manipulation", "math fundamentals", "searching",
    "math fundamentals", "algorithm", "algorithm",
)


def q(qid, title, tier, tags, fn, prompt, sig, cases, sol, **extra):
    arg_names, arg_types = sig
    case_types = {c["expectedType"] for c in cases}
    question = {
        "id": qid,
        "title": title,
        "tier": tier,
        "tags": list(dict.fromkeys(tags)),
        "verified": extra.pop("verified", True),
        "functionName": fn,
        "expectedType": cases[0]["expectedType"],
        "prompt": prompt,
        "signature": {"argNames": arg_names, "argTypes": arg_types},
        "cases": cases,
        "solution": sol,
    }
    if len(case_types) > 1:
        question["polymorphic"] = True
        question.setdefault("polymorphicNote", (
            "This question returns more than one type depending on the input "
            f"({', '.join(sorted(case_types))}). Statically typed languages must "
            "return a variant type (std::variant in C++, object in C#, Object "
            "in Java, the CBResult enum in Rust)."
        ))
    question.update(extra)
    return question


def S(p, cpp, cs, java):
    return {"python": p, "cpp": cpp, "csharp": cs, "java": java}


def c(args, expected, t):
    return {"args": args, "expected": expected, "expectedType": t}


LC = "LeetCode"

QUESTIONS = [
    # ══ hard tier: Coderbyte-shaped, harder than Medium ══════════════════

    q("valid-anagram", "Valid Anagram", HARD, [SM, SEARCH], "IsAnagram",
      "Have the function IsAnagram(str1, str2) take two strings and return the string true if "
      "str2 is an anagram of str1, otherwise return false. Both strings will contain only "
      "lowercase letters. Do not use sorting.",
      (["str1", "str2"], [STR, STR]),
      [c(["anagram", "nagaram"], "true", STR), c(["rat", "car"], "false", STR),
       c(["abc", "abd"], "false", STR), c(["a", "a"], "true", STR)],
      S("""def IsAnagram(a, b):
    if len(a) != len(b):
        return "false"
    counts = {}
    for ch in a:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in b:
        if ch not in counts:
            return "false"
        counts[ch] -= 1
    return "true"
""",
        """#include <string>
#include <map>
using namespace std;
string IsAnagram(string a, string b) {
    if (a.size() != b.size()) return "false";
    map<char, int> counts;
    for (char ch : a) counts[ch]++;
    for (char ch : b) {
        auto it = counts.find(ch);
        if (it == counts.end() || it->second == 0) return "false";
        it->second--;
    }
    return "true";
}""",
        """using System;
using System.Linq;
public class Program {
  public static string IsAnagram(string a, string b) {
    if (a.Length != b.Length) return "false";
    var counts = new int[26];
    foreach (char ch in a) counts[ch - 'a']++;
    foreach (char ch in b) if (--counts[ch - 'a'] < 0) return "false";
    return "true";
  }
}""",
        """public class Solution {
  public static String isAnagram(String a, String b) {
    if (a.length() != b.length()) return "false";
    int[] counts = new int[26];
    for (char ch : a.toCharArray()) counts[ch - 'a']++;
    for (char ch : b.toCharArray()) if (--counts[ch - 'a'] < 0) return "false";
    return "true";
  }
}""")),

    q("contains-duplicate", "Contains Duplicate", HARD, [SEARCH, ALGO], "ContainsDuplicate",
      "Have the function ContainsDuplicate(arr) take the array of numbers stored in arr and return "
      "the string true if any number appears more than once, otherwise return false.",
      (["arr"], ["array"]),
      [c([[1, 2, 3, 1]], "true", STR), c([[1, 2, 3, 4]], "false", STR),
       c([[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], "true", STR),
       c([[1]], "false", STR)],
      S("""def ContainsDuplicate(a):
    seen = set()
    for v in a:
        if v in seen:
            return "true"
        seen.add(v)
    return "false"
""",
        """#include <vector>
#include <set>
using namespace std;
string ContainsDuplicate(vector<int> arr) {
    set<int> seen;
    for (int v : arr) {
        if (seen.count(v)) return "true";
        seen.insert(v);
    }
    return "false";
}""",
        """public class Program {
  public static string ContainsDuplicate(int[] arr) {
    var seen = new System.Collections.Generic.HashSet<int>();
    foreach (int v in arr) if (!seen.Add(v)) return "true";
    return "false";
  }
}""",
        """import java.util.*;
public class Solution {
  public static String containsDuplicate(int[] arr) {
    Set<Integer> seen = new HashSet<>();
    for (int v : arr) if (!seen.add(v)) return "true";
    return "false";
  }
}""")),

    q("single-number", "Single Number", HARD, [ALGO, MATH], "SingleNumber",
      "Have the function SingleNumber(arr) take the array of integers stored in arr, in which "
      "every number appears exactly twice except one, and return that single number.",
      (["arr"], ["array"]),
      [c([[2, 2, 1]], 1, INT), c([[4, 1, 2, 1, 2]], 4, INT),        c([[1]], 1, INT), c([[7, 3, 5, 5, 3]], 7, INT)],
      S("""def SingleNumber(arr):
    result = 0
    for v in arr:
        result ^= v
    return result""",
        """int SingleNumber(vector<int> arr) {
    int result = 0;
    for (int v : arr) result ^= v;
    return result;
}""",
        """public class Program {
  public static int SingleNumber(int[] arr) {
    int result = 0;
    foreach (int v in arr) result ^= v;
    return result;
  }
}""",
        """public class Solution {
  public static int singleNumber(int[] arr) {
    int result = 0;
    for (int v : arr) result ^= v;
    return result;
  }
}""")),

    q("maximum-subarray", "Maximum Subarray", HARD, [ALGO], "MaxSubarray",
      "Have the function MaxSubarray(arr) take the array of integers stored in arr and return the "
      "largest sum of a non-empty contiguous subarray. The array will contain at least one number.",
      (["arr"], ["array"]),
      [c([[-2, 1, -3, 4, -1, 2, 1, -5, 4]], 6, INT),
       c([[1]], 1, INT), c([[5, 4, -1, 7, 8]], 23, INT),
       c([[-3, -1, -2]], -1, INT)],
      S("""def MaxSubarray(arr):
    best = current = arr[0]
    for v in arr[1:]:
        current = max(v, current + v)
        best = max(best, current)
    return best""",
        """#include <vector>
#include <algorithm>
using namespace std;
int MaxSubarray(vector<int> arr) {
    int best = arr[0], current = arr[0];
    for (size_t i = 1; i < arr.size(); i++) {
        current = max(arr[i], current + arr[i]);
        best = max(best, current);
    }
    return best;
}""",
        """using System;
using System.Linq;
public class Program {
  public static int MaxSubarray(int[] arr) {
    int best = arr[0], current = arr[0];
    for (int i = 1; i < arr.Length; i++) {
      current = Math.Max(arr[i], current + arr[i]);
      best = Math.Max(best, current);
    }
    return best;
  }
}""",
        """public class Solution {
  public static int maxSubarray(int[] arr) {
    int best = arr[0], current = arr[0];
    for (int i = 1; i < arr.length; i++) {
      current = Math.max(arr[i], current + arr[i]);
      best = Math.max(best, current);
    }
    return best;
  }
}""")),

    q("best-time-to-trade", "Best Time to Trade", HARD, [ALGO, MATH], "MaxProfit",
      "Have the function MaxProfit(arr) take the array of daily prices stored in arr, where arr[i] "
      "is the price of an item on day i, and return the maximum profit of a single buy then sell. "
      "Return 0 if no profit is possible.",
      (["arr"], ["array"]),
      [c([[7, 1, 5, 3, 6, 4]], 5, INT), c([[7, 6, 4, 3, 1]], 0, INT),
       c([[1, 2]], 1, INT), c([[5, 4, 3, 2, 1]], 0, INT)],
      S("""def MaxProfit(prices):
    best = 0
    low = prices[0]
    for price in prices[1:]:
        if price - low > best:
            best = price - low
        if price < low:
            low = price
    return best""",
        """#include <vector>
using namespace std;
int MaxProfit(vector<int> prices) {
    int best = 0, low = prices[0];
    for (size_t i = 1; i < prices.size(); i++) {
        if (prices[i] - low > best) best = prices[i] - low;
        if (prices[i] < low) low = prices[i];
    }
    return best;
}""",
        """using System;
public class Program {
  public static int MaxProfit(int[] prices) {
    int best = 0, low = prices[0];
    for (int i = 1; i < prices.Length; i++) {
      if (prices[i] - low > best) best = prices[i] - low;
      if (prices[i] < low) low = prices[i];
    }
    return best;
  }
}""",
        """public class Solution {
  public static int maxProfit(int[] prices) {
    int best = 0, low = prices[0];
    for (int i = 1; i < prices.length; i++) {
      if (prices[i] - low > best) best = prices[i] - low;
      if (prices[i] < low) low = prices[i];
    }
    return best;
  }
}""")),

    q("house-robber", "House Robber", HARD, [ALGO, DP], "Robber",
      "Have the function Robber(arr) take the array of amounts stored in arr, where arr[i] is the "
      "money in house i, and return the most money you can steal without ever visiting two "
      "adjacent houses.",
      (["arr"], ["array"]),
      [c([[1, 2, 3, 1]], 4, INT), c([[2, 7, 9, 3, 1]], 12, INT),
       c([[5]], 5, INT), c([[2, 1, 1, 2]], 4, INT)],
      S("""def Robber(arr):
    prev = best = 0
    for v in arr:
        prev, best = best, max(best, prev + v)
    return best""",
        """#include <vector>
#include <algorithm>
using namespace std;
int Robber(vector<int> arr) {
    int prev = 0, best = 0;
    for (int v : arr) { int t = best; best = max(best, prev + v); prev = t; }
    return best;
}""",
        """using System;
public class Program {
  public static int Robber(int[] arr) {
    int prev = 0, best = 0;
    foreach (int v in arr) { int t = best; best = Math.Max(best, prev + v); prev = t; }
    return best;
  }
}""",
        """public class Solution {
  public static int robber(int[] arr) {
    int prev = 0, best = 0;
    for (int v : arr) { int t = best; best = Math.max(best, prev + v); prev = t; }
    return best;
  }
}""")),

    q("missing-number", "Missing Number", HARD, [ALGO, SEARCH], "MissingNumber",
      "Have the function MissingNumber(arr) take the array of integers stored in arr, which "
      "contains n distinct numbers from 0 to n-1 with exactly one missing, and return the number "
      "that is missing.",
      (["arr"], ["array"]),
      [c([[3, 0, 1]], 2, INT), c([[0, 1]], 2, INT), c([[9, 6, 4, 2, 3, 5, 7, 0, 1]], 8, INT),
       c([[0]], 1, INT)],
      S("""def MissingNumber(arr):
    n = len(arr)
    expected = n * (n + 1) // 2
    return expected - sum(arr)""",
        """#include <vector>
using namespace std;
int MissingNumber(vector<int> arr) {
    int n = arr.size();
    int expected = n * (n + 1) / 2;
    int total = 0;
    for (int v : arr) total += v;
    return expected - total;
}""",
        """public class Program {
  public static int MissingNumber(int[] arr) {
    int n = arr.Length;
    return n * (n + 1) / 2 - arr.Sum();
  }
}""",
        """public class Solution {
  public static int missingNumber(int[] arr) {
    int n = arr.length;
    int expected = n * (n + 1) / 2;
    for (int v : arr) expected -= v;
    return expected;
  }
}""")),

    q("product-except-self", "Product Except Self", HARD, [ALGO, MATH], "ProductExceptSelf",
      "Have the function ProductExceptSelf(arr) take the array of integers stored in arr and "
      "return an array where each element is the product of every element except itself. You may "
      "not use division.",
      (["arr"], ["array"]),
      [c([[1, 2, 3, 4]], [24, 12, 8, 6], "array"),
       c([[-1, 1, 0, -3, 3]], [0, 0, 9, 0, 0], "array"),
       c([[2, 3]], [3, 2], "array")],
      S("""def ProductExceptSelf(a):
    n = len(a)
    out = [1] * n
    for i in range(n):
        for j in range(n):
            if i != j:
                out[i] *= a[j]
    return out""",
        """#include <vector>
using namespace std;
vector<int> ProductExceptSelf(vector<int> a) {
    int n = a.size();
    vector<int> out(n, 1);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            if (i != j) out[i] *= a[j];
    return out;
}""",
        """public class Program {
  public static int[] ProductExceptSelf(int[] a) {
    int n = a.Length;
    var outv = new int[n];
    for (int i = 0; i < n; i++) {
      outv[i] = 1;
      for (int j = 0; j < n; j++) if (i != j) outv[i] *= a[j];
    }
    return outv;
  }
}""",
        """public class Solution {
  public static int[] productExceptSelf(int[] a) {
    int n = a.length;
    int[] out = new int[n];
    for (int i = 0; i < n; i++) {
      out[i] = 1;
      for (int j = 0; j < n; j++) if (i != j) out[i] *= a[j];
    }
    return out;
  }
}""")),

    q("search-insert-position", "Search Insert Position", HARD, [SEARCH, ALGO], "SearchInsert",
      "Have the function SearchInsert(arr, target) take a sorted array of distinct integers and a "
      "target, and return the index where target would be inserted to keep the array sorted.",
      (["arr", "target"], ["array", INT]),
      [c([[1, 3, 5, 6], 5], 2, INT), c([[1, 3, 5, 6], 2], 1, INT),
       c([[1, 3, 5, 6], 7], 4, INT), c([[1], 0], 0, INT)],
      S("""def SearchInsert(arr, target):
    low, high = 0, len(arr)
    while low < high:
        mid = (low + high) // 2
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid
    return low""",
        """#include <vector>
using namespace std;
int SearchInsert(vector<int> arr, int target) {
    int low = 0, high = arr.size();
    while (low < high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] < target) low = mid + 1; else high = mid;
    }
    return low;
}""",
        """public class Program {
  public static int SearchInsert(int[] arr, int target) {
    int low = 0, high = arr.Length;
    while (low < high) {
      int mid = low + (high - low) / 2;
      if (arr[mid] < target) low = mid + 1; else high = mid;
    }
    return low;
  }
}""",
        """public class Solution {
  public static int searchInsert(int[] arr, int target) {
    int low = 0, high = arr.length;
    while (low < high) {
      int mid = low + (high - low) / 2;
      if (arr[mid] < target) low = mid + 1; else high = mid;
    }
    return low;
  }
}""")),

    q("plus-one", "Plus One", HARD, [ALGO, MA], "PlusOne",
      "Have the function PlusOne(arr) take the array of digits stored in arr, most significant "
      "first, and return the array of digits representing the number plus one.",
      (["arr"], ["array"]),
      [c([[1, 2, 3]], [1, 2, 4], "array"), c([[4, 3, 2, 1]], [4, 3, 2, 2], "array"),
       c([[9]], [1, 0], "array"), c([[9, 9]], [1, 0, 0], "array")],
      S("""def PlusOne(digits):
    out = list(digits)
    for i in range(len(out) - 1, -1, -1):
        if out[i] < 9:
            out[i] += 1
            return out
        out[i] = 0
    return [1] + out""",
        """#include <vector>
using namespace std;
vector<int> PlusOne(vector<int> digits) {
    vector<int> out = digits;
    for (int i = (int)out.size() - 1; i >= 0; i--) {
        if (out[i] < 9) { out[i]++; return out; }
        out[i] = 0;
    }
    out.insert(out.begin(), 1);
    return out;
}""",
        """using System.Collections.Generic;
public class Program {
  public static int[] PlusOne(int[] digits) {
    var outv = new List<int>(digits);
    for (int i = outv.Count - 1; i >= 0; i--) {
      if (outv[i] < 9) { outv[i]++; return outv.ToArray(); }
      outv[i] = 0;
    }
    outv.Insert(0, 1);
    return outv.ToArray();
  }
}""",
        """import java.util.*;
public class Solution {
  public static int[] plusOne(int[] digits) {
    int[] out = digits.clone();
    for (int i = out.length - 1; i >= 0; i--) {
      if (out[i] < 9) { out[i]++; return out; }
      out[i] = 0;
    }
    int[] res = new int[out.length + 1];
    res[0] = 1;
    return res;
  }
}""")),

    q("longest-common-prefix", "Longest Common Prefix", HARD, [SM, SEARCH], "LongestCommonPrefix",
      "Have the function LongestCommonPrefix(arr) take the array of strings stored in arr and "
      "return the longest common prefix shared by every string. Return the empty string if there "
      "is none.",
      (["arr"], ["array"]),
      [c([["flower", "flow", "flight"]], "fl", STR),
       c([["dog", "racecar", "car"]], "", STR),
       c([["a"]], "a", STR), c([["abc", "abc"]], "abc", STR)],
      S("""def LongestCommonPrefix(words):
    if not words:
        return ""
    prefix = words[0]
    for word in words[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix""",
        """#include <vector>
#include <string>
using namespace std;
string LongestCommonPrefix(vector<string> words) {
    if (words.empty()) return "";
    string prefix = words[0];
    for (size_t i = 1; i < words.size(); i++) {
        while (words[i].compare(0, prefix.size(), prefix) != 0) {
            prefix.pop_back();
            if (prefix.empty()) return "";
        }
    }
    return prefix;
}""",
        """public class Program {
  public static string LongestCommonPrefix(string[] words) {
    if (words.Length == 0) return "";
    string prefix = words[0];
    foreach (var word in words.Skip(1)) {
      while (!word.StartsWith(prefix)) {
        prefix = prefix.Substring(0, prefix.Length - 1);
        if (prefix.Length == 0) return "";
      }
    }
    return prefix;
  }
}""",
        """public class Solution {
  public static String longestCommonPrefix(String[] words) {
    if (words.length == 0) return "";
    String prefix = words[0];
    for (int i = 1; i < words.length; i++) {
      while (!words[i].startsWith(prefix)) {
        prefix = prefix.substring(0, prefix.length() - 1);
        if (prefix.isEmpty()) return "";
      }
    }
    return prefix;
  }
}""")),

    q("reverse-words", "Reverse Word Order", HARD, [SM, ALGO], "ReverseWords",
      "Have the function ReverseWords(str) take the string of words stored in str and return the "
      "string with the word order reversed. Any number of spaces between words counts as a single "
      "space, and there are no leading or trailing spaces.",
      (["str"], [STR]),
      [c(["the sky is blue"], "blue is sky the", STR),
       c(["  hello world  "], "world hello", STR),
       c(["a good   example"], "example good a", STR)],
      S("""def ReverseWords(s):
    return " ".join(reversed(s.split()))""",
        """#include <string>
#include <sstream>
#include <vector>
#include <algorithm>
using namespace std;
string ReverseWords(string str) {
    vector<string> words;
    istringstream in(str);
    string w;
    while (in >> w) words.push_back(w);
    reverse(words.begin(), words.end());
    string out;
    for (size_t i = 0; i < words.size(); i++) { if (i) out += " "; out += words[i]; }
    return out;
}""",
        """using System;
using System.Linq;
public class Program {
  public static string ReverseWords(string str) {
    return string.Join(" ", str.Split(' ', System.StringSplitOptions.RemoveEmptyEntries).Reverse());
  }
}""",
        """public class Solution {
  public static String reverseWords(String str) {
    String[] words = str.trim().split("\\\\s+");
    StringBuilder sb = new StringBuilder();
    for (int i = words.length - 1; i >= 0; i--) {
      if (sb.length() > 0) sb.append(" ");
      sb.append(words[i]);
    }
    return sb.toString();
  }
}""")),

    q("valid-palindrome-ii", "Almost Palindrome", HARD, [SM, ALGO], "IsPalindromeII",
      "Have the function IsPalindromeII(str) take the string stored in str and return the string "
      "true if it can become a palindrome by deleting at most one character, otherwise return "
      "false. Only letters, digits and spaces are used.",
      (["str"], [STR]),
      [c(["racecar"], "true", STR), c(["abca"], "true", STR),
       c(["abc"], "false", STR), c(["a"], "true", STR), c(["abcba"], "true", STR)],
      S("""def IsPalindromeII(s):
    def check(t):
        return t == t[::-1]
    if check(s):
        return "true"
    for i in range(len(s)):
        if check(s[:i] + s[i+1:]):
            return "true"
    return "false"
""",
        """#include <string>
using namespace std;
static bool check(const string& s) {
    string r = s; reverse(r.begin(), r.end());
    return s == r;
}
string IsPalindromeII(string str) {
    if (check(str)) return "true";
    for (size_t i = 0; i < str.size(); i++) {
        string t = str.substr(0, i) + str.substr(i + 1);
        if (check(t)) return "true";
    }
    return "false";
}""",
        """using System;
using System.Linq;
public class Program {
  public static string IsPalindromeII(string str) {
    bool Check(string t) => t.SequenceEqual(t.Reverse());
    if (Check(str)) return "true";
    for (int i = 0; i < str.Length; i++)
      if (Check(str.Remove(i, 1))) return "true";
    return "false";
  }
}""",
        """public class Solution {
  static boolean check(String s) {
    return new StringBuilder(s).reverse().toString().equals(s);
  }
  public static String isPalindromeII(String str) {
    if (check(str)) return "true";
    for (int i = 0; i < str.length(); i++) {
      String t = str.substring(0, i) + str.substring(i + 1);
      if (check(t)) return "true";
    }
    return "false";
  }
}""")),

    q("longest-repeating-char", "Longest Repeating Run", HARD, [SM, ALGO], "LongestRepeatingRun",
      "Have the function LongestRepeatingRun(str) take the string stored in str and return the "
      "length of the longest run of the same character. Return 0 for an empty string.",
      (["str"], [STR]),
      [c(["aaabb"], 3, INT), c(["abcbba"], 2, INT), c(["a"], 1, INT),
       c(["abab"], 1, INT)],
      S("""def LongestRepeatingRun(s):
    if not s:
        return 0
    best = current = 1
    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            current += 1
        else:
            current = 1
        if current > best:
            best = current
    return best""",
        """#include <string>
using namespace std;
int LongestRepeatingRun(string str) {
    if (str.empty()) return 0;
    int best = 1, current = 1;
    for (size_t i = 1; i < str.size(); i++) {
        if (str[i] == str[i-1]) current++; else current = 1;
        if (current > best) best = current;
    }
    return best;
}""",
        """using System;
public class Program {
  public static int LongestRepeatingRun(string str) {
    if (str.Length == 0) return 0;
    int best = 1, current = 1;
    for (int i = 1; i < str.Length; i++) {
      if (str[i] == str[i-1]) current++; else current = 1;
      if (current > best) best = current;
    }
    return best;
  }
}""",
        """public class Solution {
  public static int longestRepeatingRun(String str) {
    if (str.isEmpty()) return 0;
    int best = 1, current = 1;
    for (int i = 1; i < str.length(); i++) {
      if (str.charAt(i) == str.charAt(i-1)) current++; else current = 1;
      if (current > best) best = current;
    }
    return best;
  }
}""")),

    # ══ stretch tier: real LeetCode, NOT assessment-shaped ═══════════════

    q("lc-trapping-rain-water", "Trapping Rain Water", STRETCH, [ALGO], "Trap",
      "Have the function Trap(heights) take the array of bar heights stored in heights and return "
      "how much water is trapped between the bars. This is LeetCode 42, adapted to this harness.",
      (["heights"], ["array"]),
      [c([[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], 6, INT),
       c([[4, 2, 0, 3, 2, 5]], 9, INT), c([[]], 0, INT), c([[3]], 0, INT)],
      S("""def Trap(h):
    if not h:
        return 0
    left, right = 0, len(h) - 1
    left_max = right_max = 0
    total = 0
    while left < right:
        if h[left] < h[right]:
            left_max = max(left_max, h[left])
            total += left_max - h[left]
            left += 1
        else:
            right_max = max(right_max, h[right])
            total += right_max - h[right]
            right -= 1
    return total""",
        """#include <vector>
using namespace std;
int Trap(vector<int> h) {
    if (h.empty()) return 0;
    int left = 0, right = h.size() - 1;
    int leftMax = 0, rightMax = 0, total = 0;
    while (left < right) {
        if (h[left] < h[right]) {
            if (h[left] > leftMax) leftMax = h[left];
            total += leftMax - h[left];
            left++;
        } else {
            if (h[right] > rightMax) rightMax = h[right];
            total += rightMax - h[right];
            right--;
        }
    }
    return total;
}""",
        """using System;
public class Program {
  public static int Trap(int[] h) {
    if (h.Length == 0) return 0;
    int left = 0, right = h.Length - 1, leftMax = 0, rightMax = 0, total = 0;
    while (left < right) {
      if (h[left] < h[right]) {
        leftMax = Math.Max(leftMax, h[left]);
        total += leftMax - h[left];
        left++;
      } else {
        rightMax = Math.Max(rightMax, h[right]);
        total += rightMax - h[right];
        right--;
      }
    }
    return total;
  }
}""",
        """public class Solution {
  public static int trap(int[] h) {
    if (h.length == 0) return 0;
    int left = 0, right = h.length - 1, leftMax = 0, rightMax = 0, total = 0;
    while (left < right) {
      if (h[left] < h[right]) {
        leftMax = Math.max(leftMax, h[left]);
        total += leftMax - h[left];
        left++;
      } else {
        rightMax = Math.max(rightMax, h[right]);
        total += rightMax - h[right];
        right--;
      }
    }
    return total;
  }
}"""),
      source=LC, sourceId=42, sourceNote="LeetCode 42 (Hard). Expect 30-60 minutes cold."),

    q("lc-first-missing-positive", "First Missing Positive", STRETCH, [ALGO, SEARCH], "FirstMissing",
      "Have the function FirstMissing(arr) take the array of integers stored in arr and return the "
      "smallest positive integer that does not occur. Runs in O(n) time. This is LeetCode 41.",
      (["arr"], ["array"]),
      [c([[1, 2, 0]], 3, INT), c([[3, 4, -1, 1]], 2, INT),
       c([[7, 8, 9, 11, 12]], 1, INT), c([[1]], 2, INT)],
      S("""def FirstMissing(arr):
    n = len(arr)
    for i in range(n):
        while 1 <= arr[i] <= n and arr[arr[i] - 1] != arr[i]:
            target = arr[i] - 1
            arr[i], arr[target] = arr[target], arr[i]
    for i in range(n):
        if arr[i] != i + 1:
            return i + 1
    return n + 1""",
        """#include <vector>
using namespace std;
int FirstMissing(vector<int> arr) {
    int n = arr.size();
    for (int i = 0; i < n; i++) {
        while (arr[i] >= 1 && arr[i] <= n && arr[arr[i] - 1] != arr[i]) {
            int target = arr[i] - 1;
            int tmp = arr[target];
            arr[target] = arr[i];
            arr[i] = tmp;
        }
    }
    for (int i = 0; i < n; i++) if (arr[i] != i + 1) return i + 1;
    return n + 1;
}""",
        """public class Program {
  public static int FirstMissing(int[] input) {
    int n = input.Length;
    var arr = (int[])input.Clone();
    for (int i = 0; i < n; i++) {
      while (arr[i] >= 1 && arr[i] <= n && arr[arr[i] - 1] != arr[i]) {
        int target = arr[i] - 1;
        int tmp = arr[target]; arr[target] = arr[i]; arr[i] = tmp;
      }
    }
    for (int i = 0; i < n; i++) if (arr[i] != i + 1) return i + 1;
    return n + 1;
  }
}""",
        """public class Solution {
  public static int firstMissing(int[] input) {
    int n = input.length;
    int[] arr = input.clone();
    for (int i = 0; i < n; i++) {
      while (arr[i] >= 1 && arr[i] <= n && arr[arr[i] - 1] != arr[i]) {
        int target = arr[i] - 1;
        int tmp = arr[target]; arr[target] = arr[i]; arr[i] = tmp;
      }
    }
    for (int i = 0; i < n; i++) if (arr[i] != i + 1) return i + 1;
    return n + 1;
  }
}"""),
      source=LC, sourceId=41, sourceNote="LeetCode 41 (Hard). The O(n) indexing trick is the whole point."),

    q("lc-search-rotated", "Search Rotated Array", STRETCH, [SEARCH, ALGO], "SearchRotated",
      "Have the function SearchRotated(arr, target) take a sorted array of distinct integers that "
      "has been rotated at an unknown pivot, and return the index of target or -1 if absent. This "
      "is LeetCode 33.",
      (["arr", "target"], ["array", INT]),
      [c([[4, 5, 6, 7, 0, 1, 2], 0], 4, INT), c([[4, 5, 6, 7, 0, 1, 2], 3], -1, INT),
       c([[1], 0], -1, INT), c([[1, 3], 3], 1, INT)],
      S("""def SearchRotated(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        if arr[low] <= arr[mid]:
            if arr[low] <= target < arr[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if arr[mid] < target <= arr[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1""",
        """#include <vector>
using namespace std;
int SearchRotated(vector<int> arr, int target) {
    int low = 0, high = arr.size() - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] == target) return mid;
        if (arr[low] <= arr[mid]) {
            if (arr[low] <= target && target < arr[mid]) high = mid - 1;
            else low = mid + 1;
        } else {
            if (arr[mid] < target && target <= arr[high]) low = mid + 1;
            else high = mid - 1;
        }
    }
    return -1;
}""",
        """public class Program {
  public static int SearchRotated(int[] arr, int target) {
    int low = 0, high = arr.Length - 1;
    while (low <= high) {
      int mid = low + (high - low) / 2;
      if (arr[mid] == target) return mid;
      if (arr[low] <= arr[mid]) {
        if (arr[low] <= target && target < arr[mid]) high = mid - 1;
        else low = mid + 1;
      } else {
        if (arr[mid] < target && target <= arr[high]) low = mid + 1;
        else high = mid - 1;
      }
    }
    return -1;
  }
}""",
        """public class Solution {
  public static int searchRotated(int[] arr, int target) {
    int low = 0, high = arr.length - 1;
    while (low <= high) {
      int mid = low + (high - low) / 2;
      if (arr[mid] == target) return mid;
      if (arr[low] <= arr[mid]) {
        if (arr[low] <= target && target < arr[mid]) high = mid - 1;
        else low = mid + 1;
      } else {
        if (arr[mid] < target && target <= arr[high]) low = mid + 1;
        else high = mid - 1;
      }
    }
    return -1;
  }
}"""),
      source=LC, sourceId=33, sourceNote="LeetCode 33 (Medium). Modified binary search."),

    q("lc-container-water", "Container With Most Water", STRETCH, [ALGO], "MaxArea",
      "Have the function MaxArea(heights) take the array of vertical line heights stored in "
      "heights and return the largest area of water a container can hold. This is LeetCode 11.",
      (["heights"], ["array"]),
      [c([[1, 8, 6, 2, 5, 4, 8, 3, 7]], 49, INT),
       c([[1, 1]], 1, INT), c([[4, 3, 2, 1, 4]], 16, INT)],
      S("""def MaxArea(h):
    left, right = 0, len(h) - 1
    best = 0
    while left < right:
        best = max(best, min(h[left], h[right]) * (right - left))
        if h[left] < h[right]:
            left += 1
        else:
            right -= 1
    return best""",
        """#include <vector>
#include <algorithm>
using namespace std;
int MaxArea(vector<int> h) {
    int left = 0, right = h.size() - 1, best = 0;
    while (left < right) {
        best = max(best, min(h[left], h[right]) * (right - left));
        if (h[left] < h[right]) left++; else right--;
    }
    return best;
}""",
        """using System;
public class Program {
  public static int MaxArea(int[] h) {
    int left = 0, right = h.Length - 1, best = 0;
    while (left < right) {
      best = Math.Max(best, Math.Min(h[left], h[right]) * (right - left));
      if (h[left] < h[right]) left++; else right--;
    }
    return best;
  }
}""",
        """public class Solution {
  public static int maxArea(int[] h) {
    int left = 0, right = h.length - 1, best = 0;
    while (left < right) {
      best = Math.max(best, Math.min(h[left], h[right]) * (right - left));
      if (h[left] < h[right]) left++; else right--;
    }
    return best;
  }
}"""),
      source=LC, sourceId=11, sourceNote="LeetCode 11 (Medium). Two pointers."),

    q("lc-median-two-sorted", "Median of Two Sorted Arrays", STRETCH, [SEARCH, ALGO], "MedianTwoSorted",
      "Have the function MedianTwoSorted(a, b) take two sorted arrays and return the median of "
      "their combined elements. Runs in O(log(m+n)). This is LeetCode 4.",
      (["a", "b"], ["array", "array"]),
      [c([[1, 3], [2]], 2.0, "float"), c([[1, 2], [3, 4]], 2.5, "float"),
       c([[], [1]], 1.0, "float"), c([[2], []], 2.0, "float")],
      S("""def MedianTwoSorted(a, b):
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    if n == 0:
        return -1
    low, high = 0, m
    half = (m + n + 1) // 2
    while low <= high:
        i = (low + high) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2 == 1:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2.0
        if a_left > b_right:
            high = i - 1
        else:
            low = i + 1
    return -1""",
        """#include <vector>
#include <algorithm>
#include <limits>
using namespace std;
double MedianTwoSorted(vector<int> a, vector<int> b) {
    if (a.size() > b.size()) swap(a, b);
    int m = a.size(), n = b.size();
    if (n == 0) return -1;
    int low = 0, high = m, half = (m + n + 1) / 2;
    while (low <= high) {
        int i = (low + high) / 2, j = half - i;
        double aL = i > 0 ? a[i-1] : -1e18;
        double aR = i < m ? a[i] : 1e18;
        double bL = j > 0 ? b[j-1] : -1e18;
        double bR = j < n ? b[j] : 1e18;
        if (aL <= bR && bL <= aR) {
            if ((m + n) % 2 == 1) return max(aL, bL);
            return (max(aL, bL) + min(aR, bR)) / 2.0;
        }
        if (aL > bR) high = i - 1; else low = i + 1;
    }
    return -1;
}""",
        """using System;
using System.Linq;
public class Program {
  public static double MedianTwoSorted(int[] a, int[] b) {
    if (a.Length > b.Length) { var t = a; a = b; b = t; }
    int m = a.Length, n = b.Length;
    if (n == 0) return -1;
    int low = 0, high = m, half = (m + n + 1) / 2;
    while (low <= high) {
      int i = (low + high) / 2, j = half - i;
      double aL = i > 0 ? a[i-1] : double.NegativeInfinity;
      double aR = i < m ? a[i] : double.PositiveInfinity;
      double bL = j > 0 ? b[j-1] : double.NegativeInfinity;
      double bR = j < n ? b[j] : double.PositiveInfinity;
      if (aL <= bR && bL <= aR)
        return (m + n) % 2 == 1 ? Math.Max(aL, bL) : (Math.Max(aL, bL) + Math.Min(aR, bR)) / 2.0;
      if (aL > bR) high = i - 1; else low = i + 1;
    }
    return -1;
  }
}""",
        """public class Solution {
  public static double medianTwoSorted(int[] a, int[] b) {
    if (a.length > b.length) { int[] t = a; a = b; b = t; }
    int m = a.length, n = b.length;
    if (n == 0) return -1;
    int low = 0, high = m, half = (m + n + 1) / 2;
    while (low <= high) {
      int i = (low + high) / 2, j = half - i;
      double aL = i > 0 ? a[i-1] : Double.NEGATIVE_INFINITY;
      double aR = i < m ? a[i] : Double.POSITIVE_INFINITY;
      double bL = j > 0 ? b[j-1] : Double.NEGATIVE_INFINITY;
      double bR = j < n ? b[j] : Double.POSITIVE_INFINITY;
      if (aL <= bR && bL <= aR)
        return (m + n) % 2 == 1 ? Math.max(aL, bL) : (Math.max(aL, bL) + Math.min(aR, bR)) / 2.0;
      if (aL > bR) high = i - 1; else low = i + 1;
    }
    return -1;
  }
}"""),
      source=LC, sourceId=4, sourceNote="LeetCode 4 (Hard). Binary search on the partition point."),

    q("lc-decode-ways", "Decode Ways", STRETCH, [SM, DP, ALGO], "DecodeWays",
      "Have the function DecodeWays(str) take a digit string stored in str and return the number of "
      "ways to decode it, where 1 maps to A and 26 maps to Z. A 0 must be followed by a valid "
      "code. This is LeetCode 91.",
      (["str"], [STR]),
      [c(["226"], 3, INT), c(["06"], 0, INT), c(["2101"], 1, INT),
       c(["10"], 1, INT), c(["27"], 1, INT)],
      S("""def DecodeWays(s):
    if not s or s[0] == "0":
        return 0
    prev_prev, prev = 1, 1
    for i in range(1, len(s)):
        current = 0
        if s[i] != "0":
            current += prev
        two = int(s[i-1:i+1])
        if 10 <= two <= 26:
            current += prev_prev
        if current == 0:
            return 0
        prev_prev, prev = prev, current
    return prev""",
        """#include <string>
using namespace std;
int DecodeWays(string s) {
    if (s.empty() || s[0] == '0') return 0;
    int prevPrev = 1, prev = 1;
    for (size_t i = 1; i < s.size(); i++) {
        int current = 0;
        if (s[i] != '0') current += prev;
        int two = (s[i-1] - '0') * 10 + (s[i] - '0');
        if (two >= 10 && two <= 26) current += prevPrev;
        if (current == 0) return 0;
        prevPrev = prev;
        prev = current;
    }
    return prev;
}""",
        """public class Program {
  public static int DecodeWays(string s) {
    if (s.Length == 0 || s[0] == '0') return 0;
    int prevPrev = 1, prev = 1;
    for (int i = 1; i < s.Length; i++) {
      int current = 0;
      if (s[i] != '0') current += prev;
      int two = (s[i-1] - '0') * 10 + (s[i] - '0');
      if (two >= 10 && two <= 26) current += prevPrev;
      if (current == 0) return 0;
      prevPrev = prev;
      prev = current;
    }
    return prev;
  }
}""",
        """public class Solution {
  public static int decodeWays(String s) {
    if (s.isEmpty() || s.charAt(0) == '0') return 0;
    int prevPrev = 1, prev = 1;
    for (int i = 1; i < s.length(); i++) {
      int current = 0;
      if (s.charAt(i) != '0') current += prev;
      int two = (s.charAt(i-1) - '0') * 10 + (s.charAt(i) - '0');
      if (two >= 10 && two <= 26) current += prevPrev;
      if (current == 0) return 0;
      prevPrev = prev;
      prev = current;
    }
    return prev;
  }
}"""),
      source=LC, sourceId=91, sourceNote="LeetCode 91 (Medium). First dynamic-programming problem most people meet."),

    q("lc-candy", "Candy", STRETCH, [ALGO, DP], "Candy",
      "Have the function Candy(ratings) take the array of child ratings stored in ratings and "
      "return the fewest candies you must distribute so that every child with a higher rating gets "
      "more than their neighbour, and the difference is at most one. This is LeetCode 135.",
      (["ratings"], ["array"]),
      [c([[1, 0, 2]], 5, INT), c([[1, 2, 2]], 4, INT),
       c([[1, 3, 2, 2, 1]], 7, INT), c([[5]], 1, INT)],
      S("""def Candy(ratings):
    n = len(ratings)
    if n == 0:
        return 0
    candies = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i-1]:
            candies[i] = candies[i-1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i+1]:
            candies[i] = max(candies[i], candies[i+1] + 1)
    return sum(candies)""",
        """#include <vector>
#include <algorithm>
using namespace std;
int Candy(vector<int> ratings) {
    int n = ratings.size();
    if (n == 0) return 0;
    vector<int> candies(n, 1);
    for (int i = 1; i < n; i++)
        if (ratings[i] > ratings[i-1]) candies[i] = candies[i-1] + 1;
    for (int i = n - 2; i >= 0; i--)
        if (ratings[i] > ratings[i+1]) candies[i] = max(candies[i], candies[i+1] + 1);
    int total = 0;
    for (int c : candies) total += c;
    return total;
}""",
        """using System;
using System.Linq;
public class Program {
  public static int Candy(int[] ratings) {
    int n = ratings.Length;
    if (n == 0) return 0;
    var candies = new int[n];
    for (int i = 0; i < n; i++) candies[i] = 1;
    for (int i = 1; i < n; i++)
      if (ratings[i] > ratings[i-1]) candies[i] = candies[i-1] + 1;
    for (int i = n - 2; i >= 0; i--)
      if (ratings[i] > ratings[i+1]) candies[i] = Math.Max(candies[i], candies[i+1] + 1);
    return candies.Sum();
  }
}""",
        """public class Solution {
  public static int candy(int[] ratings) {
    int n = ratings.length;
    if (n == 0) return 0;
    int[] candies = new int[n];
    java.util.Arrays.fill(candies, 1);
    for (int i = 1; i < n; i++)
      if (ratings[i] > ratings[i-1]) candies[i] = candies[i-1] + 1;
    for (int i = n - 2; i >= 0; i--)
      if (ratings[i] > ratings[i+1]) candies[i] = Math.max(candies[i], candies[i+1] + 1);
    int total = 0;
    for (int c : candies) total += c;
    return total;
  }
}"""),
      source=LC, sourceId=135, sourceNote="LeetCode 135 (Hard). Two passes: left, then right."),

    q("lc-subarray-sum-k", "Subarray Sum Equals K", STRETCH, [SEARCH, ALGO], "SubarraySumK",
      "Have the function SubarraySumK(arr, k) take the array of integers stored in arr and return "
      "the number of contiguous subarrays whose elements sum to k. This is LeetCode 560.",
      (["arr", "k"], ["array", INT]),
      [c([[1, 1, 1], 2], 2, INT), c([[1, 2, 3], 3], 2, INT),
       c([[1, -1, 0], 0], 3, INT), c([[], 0], 0, INT)],
      S("""def SubarraySumK(arr, k):
    seen = {0: 1}
    total = 0
    count = 0
    for v in arr:
        total += v
        count += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count""",
        """#include <vector>
#include <map>
using namespace std;
int SubarraySumK(vector<int> arr, int k) {
    map<long long, int> seen;
    seen[0] = 1;
    long long total = 0;
    int count = 0;
    for (int v : arr) {
        total += v;
        auto it = seen.find(total - k);
        if (it != seen.end()) count += it->second;
        seen[total]++;
    }
    return count;
}""",
        """using System;
using System.Collections.Generic;
public class Program {
  public static int SubarraySumK(int[] arr, int k) {
    var seen = new Dictionary<long, int> { { 0, 1 } };
    long total = 0;
    int count = 0;
    foreach (int v in arr) {
      total += v;
      if (seen.TryGetValue(total - k, out int n)) count += n;
      seen[total] = seen.TryGetValue(total, out int m) ? m + 1 : 1;
    }
    return count;
  }
}""",
        """import java.util.*;
public class Solution {
  public static int subarraySumK(int[] arr, int k) {
    Map<Long, Integer> seen = new HashMap<>();
    seen.put(0L, 1);
    long total = 0;
    int count = 0;
    for (int v : arr) {
      total += v;
      count += seen.getOrDefault(total - k, 0);
      seen.merge(total, 1, Integer::sum);
    }
    return count;
  }
}"""),
      source=LC, sourceId=560, sourceNote="LeetCode 560 (Medium). Prefix sums plus a hash map."),
]


def main() -> int:
    with open(QUESTIONS_PATH) as fh:
        existing = json.load(fh)["questions"]

    by_id = {question["id"]: question for question in existing}
    added = 0
    for question in QUESTIONS:
        if question["id"] not in by_id:
            added += 1
        by_id[question["id"]] = question

    # Rust goes on last: the merge above replaces whole question objects, so
    # attaching earlier would be undone by every question defined here.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from rust_solutions import attach

    attach(list(by_id.values()))

    order = {"easy": 0, "medium": 1, "hard": 2, "stretch": 3}
    merged = sorted(
        by_id.values(),
        key=lambda question: (order.get(question["tier"], 9), question["title"].lower()),
    )

    # The patterns are assigned centrally, here and in the other two builders,
    # so the catalogue is correct whichever of them ran last.
    from patterns import apply as apply_patterns

    apply_patterns(merged)

    # Tiering runs here too. It used to be a separate step that the build
    # instructions forgot, so building the catalogue reverted every Grind 75
    # question to the old "stretch" tier and 68 questions fell out of the
    # sidebar. Idempotent, which is what makes this safe to repeat.
    from retier import retier as retier_question

    for question in merged:
        retier_question(question)

    with open(QUESTIONS_PATH, "w") as fh:
        json.dump({"questions": merged}, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    counts = {}
    for question in merged:
        counts[question["tier"]] = counts.get(question["tier"], 0) + 1
    print(f"added {added} questions; catalogue now {len(merged)}")
    for tier in ("easy", "medium", "hard", "stretch"):
        print(f"  {tier:8s} {counts.get(tier, 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
