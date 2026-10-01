#!/usr/bin/env python3
"""Build the expanded question catalogue.

Keeps the four reference solutions for a question next to each other in one
place, so they cannot drift apart. Run:

    python3 tools/build_questions.py

It merges the hand-written core questions with the generated ones and writes
cbp/data/questions.json, sorted easy -> medium, preserving difficulty order.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

OUT = os.path.join(ROOT, "cbp", "data", "questions.json")
CORE = os.path.join(ROOT, "cbp", "data", "questions.json")

# ── helpers shared by every generated question ──────────────────────────────

def q(qid, title, tier, tags, fn, prompt, sig, cases, sol, **extra):
    arg_names, arg_types = sig
    case_types = {case["expectedType"] for case in cases}

    # A question whose cases disagree on return type needs a variant return in
    # the statically typed languages. Detect that here rather than trusting a
    # hand-maintained flag, which is exactly the kind of thing that goes stale.
    if len(case_types) > 1 and "polymorphicNote" not in extra:
        extra["polymorphic"] = True
        extra["polymorphicNote"] = (
            "This question returns more than one type depending on the input "
            f"({', '.join(sorted(case_types))}). Statically typed languages must return a "
            "variant type (std::variant in C++, object in C#, Object in Java, the "
            "CBResult enum in Rust)."
        )

    question = {
        "id": qid,
        "title": title,
        "tier": tier,
        "tags": tags,
        "verified": extra.pop("verified", True),
        "functionName": fn,
        "expectedType": cases[0]["expectedType"],
        "prompt": prompt,
        "signature": {"argNames": arg_names, "argTypes": arg_types},
        "cases": cases,
        "solution": sol,
    }
    question.update(extra)
    return question


def S(p, cpp, cs, java):
    return {"python": p, "cpp": cpp, "csharp": cs, "java": java}


def c(args, expected, t):
    return {"args": args, "expected": expected, "expectedType": t}


STR, INT, BOOL = "string", "int", "bool"
EASY, MEDIUM = "easy", "medium"
SM, SEARCH, MATH, ALGO = "string manipulation", "searching", "math fundamentals", "algorithm"

QUESTIONS = [

    # ── Easy ────────────────────────────────────────────────────────────────
    q("letter-capitalize", "Letter Capitalize", EASY, [SM], "LetterCapitalize",
      "For this challenge you will be capitalizing the first letter of every word in a string. "
      "The rest of the letters in the word are left as they are.",
      (["str"], [STR]),
      [c(["i am legend"], "I Am Legend", STR),
       c(["a beautiful sentence"], "A Beautiful Sentence", STR),
       c(["hello world"], "Hello World", STR)],
      S("""def LetterCapitalize(s):
    words = []
    for word in s.split():
        if word:
            words.append(word[0].upper() + word[1:])
    return " ".join(words)""",
        """#include <string>
#include <vector>
#include <sstream>
using namespace std;
string LetterCapitalize(string str) {
    istringstream in(str);
    string word, out;
    while (in >> word) {
        word[0] = toupper(word[0]);
        if (!out.empty()) out += " ";
        out += word;
    }
    return out;
}""",
        """using System;
using System.Linq;
public class Program {
  public static string LetterCapitalize(string str) {
    return string.Join(" ", str.Split(' ', StringSplitOptions.RemoveEmptyEntries)
      .Select(w => char.ToUpper(w[0]) + w.Substring(1)));
  }
}""",
        """public class Solution {
  public static String letterCapitalize(String str) {
    String[] words = str.trim().split("\\\\s+");
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < words.length; i++) {
      if (i > 0) sb.append(" ");
      String w = words[i];
      if (!w.isEmpty()) sb.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1));
    }
    return sb.toString();
  }
}""")),

    q("simple-symbols", "Simple Symbols", EASY, [SM, SEARCH], "SimpleSymbols",
      "Have the function SimpleSymbols(str) take the str parameter being passed and return true "
      "if every alphabetic character in the string is surrounded by + symbols, otherwise return false.",
      (["str"], [STR]),
      [c(["+d+"], "true", STR), c(["+d===+a+"], "false", STR),
       c(["2+a+a+"], "true", STR), c(["+a++"], "true", STR),
       c(["+a="], "false", STR), c(["b"], "false", STR)],
      S("""def SimpleSymbols(s):
    for i, ch in enumerate(s):
        if ch.isalpha():
            if i == 0 or s[i-1] != "+" or i+1 >= len(s) or s[i+1] != "+":
                return "false"
    return "true\"""",
        """#include <string>
#include <cctype>
using namespace std;
string SimpleSymbols(string str) {
    for (size_t i = 0; i < str.size(); i++) {
        if (isalpha((unsigned char)str[i])) {
            if (i == 0 || str[i-1] != '+' ||
                i+1 >= str.size() || str[i+1] != '+') return "false";
        }
    }
    return "true";
}""",
        """public class Program {
  public static string SimpleSymbols(string str) {
    for (int i = 0; i < str.Length; i++) {
      if (char.IsLetter(str[i])) {
        if (i == 0 || str[i-1] != '+' || i+1 >= str.Length || str[i+1] != '+')
          return "false";
      }
    }
    return "true";
  }
}""",
        """public class Solution {
  public static String simpleSymbols(String str) {
    for (int i = 0; i < str.length(); i++) {
      if (Character.isLetter(str.charAt(i))) {
        if (i == 0 || str.charAt(i-1) != '+' ||
            i+1 >= str.length() || str.charAt(i+1) != '+') return "false";
      }
    }
    return "true";
  }
}""")),

    q("word-count", "Word Count", EASY, [SM], "WordCount",
      "Have the function WordCount(str) take the str parameter being passed and return the number "
      "of words the string contains (ie. all cows eat grass would return 4).",
      (["str"], [STR]),
      [c(["all cows eat grass"], "4", STR), c(["hello how are you"], "4", STR),
       c(["a"], "1", STR)],
      S("""def WordCount(s):
    return str(len(s.split()))""",
        """#include <string>
#include <sstream>
using namespace std;
string WordCount(string str) {
    istringstream in(str);
    string w;
    int n = 0;
    while (in >> w) n++;
    return to_string(n);
}""",
        """public class Program {
  public static string WordCount(string str) {
    return System.Linq.Enumerable.Count(str.Split(' ', System.StringSplitOptions.RemoveEmptyEntries))
      .ToString();
  }
}""",
        """public class Solution {
  public static String wordCount(String str) {
    return String.valueOf(str.trim().split("\\\\s+").length);
  }
}""")),

    q("ex-oh", "Ex Oh", EASY, [SM], "ExOh",
      "Have the function ExOh(str) take the str parameter being passed and return the string true if "
      "there is an equal number of x's and o's in the string, otherwise return false.",
      (["str"], [STR]),
      [c(["xoxo"], "true", STR), c(["xxooo"], "false", STR),
       c(["x"], "false", STR), c(["ooo"], "false", STR)],
      S("""def ExOh(s):
    x = s.count("x")
    o = s.count("o")
    return "true" if x == o else "false\"""",
        """#include <string>
using namespace std;
string ExOh(string str) {
    int x = 0, o = 0;
    for (char c : str) { if (c == 'x') x++; else if (c == 'o') o++; }
    return x == o ? "true" : "false";
}""",
        """public class Program {
  public static string ExOh(string str) {
    return str.Count(c => c == 'x') == str.Count(c => c == 'o') ? "true" : "false";
  }
}""",
        """public class Solution {
  public static String exOh(String str) {
    int x = 0, o = 0;
    for (char c : str.toCharArray()) { if (c == 'x') x++; else if (c == 'o') o++; }
    return x == o ? "true" : "false";
  }
}""")),

    q("arith-geo", "Arith Geo", EASY, [MATH, ALGO], "ArithGeo",
      "Have the function ArithGeo(arr) take the array of numbers stored in arr and return the string "
      "Arithmetic if the sequence follows an arithmetic pattern or return the string Geometric if it "
      "follows a geometric pattern. If the sequence doesn't follow either pattern return -1.",
      (["arr"], ["array"]),
      [c([[2, 4, 6, 8]], "Arithmetic", STR), c([[2, 6, 18, 54]], "Geometric", STR),
       c([[1, 2, 3, 5]], -1, INT),      c([[5, 6, 7, 9]], -1, INT)],
      S("""def ArithGeo(arr):
    if len(arr) < 3:
        return -1
    if all(arr[i] - arr[i-1] == arr[1] - arr[0] for i in range(2, len(arr))):
        return "Arithmetic"
    if arr[0] != 0 and all(
        arr[i] * arr[0] == arr[i-1] * arr[1] for i in range(2, len(arr))
    ):
        return "Geometric"
    return -1""",
        """#include <vector>
#include <string>
#include <variant>
using namespace std;
CBResult ArithGeo(vector<int> arr) {
    int n = arr.size();
    if (n < 3) return -1;
    int d = arr[1] - arr[0];
    bool arith = true;
    for (int i = 2; i < n; i++) if (arr[i] - arr[i-1] != d) { arith = false; break; }
    if (arith) return string("Arithmetic");
    if (arr[0] != 0) {
        for (int i = 2; i < n; i++)
            if (arr[i] * arr[0] != arr[i-1] * arr[1]) return -1;
        return string("Geometric");
    }
    return -1;
}""",
        """public class Program {
  public static object ArithGeo(int[] arr) {
    int n = arr.Length;
    if (n < 3) return -1;
    int d = arr[1] - arr[0];
    for (int i = 2; i < n; i++) if (arr[i] - arr[i-1] != d) d = int.MinValue;
    if (d != int.MinValue) return "Arithmetic";
    if (arr[0] != 0) {
      for (int i = 2; i < n; i++) if (arr[i] * arr[0] != arr[i-1] * arr[1]) return -1;
      return "Geometric";
    }
    return -1;
  }
}""",
        """public class Solution {
  public static Object arithGeo(int[] arr) {
    int n = arr.length;
    if (n < 3) return -1;
    int d = arr[1] - arr[0];
    for (int i = 2; i < n; i++) if (arr[i] - arr[i-1] != d) { d = Integer.MIN_VALUE; break; }
    if (d != Integer.MIN_VALUE) return "Arithmetic";
    if (arr[0] != 0) {
      for (int i = 2; i < n; i++) if (arr[i] * arr[0] != arr[i-1] * arr[1]) return -1;
      return "Geometric";
    }
    return -1;
  }
}""")),

    q("array-addition-i", "Array Addition I", EASY, [ALGO, SEARCH], "ArrayAdditionI",
      "Have the function ArrayAdditionI(arr) take the array of numbers stored in arr and return the "
      "largest sum of the two numbers in the array. The array will always have at least two elements.",
      (["arr"], ["array"]),
      [c([[1, 2, 3, 4]], 7, INT), c([[-1, -2, -3]], -3, INT),
       c([[1, 1, 1, 1]], 2, INT)],
      S("""def ArrayAdditionI(arr):
    best = None
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            total = arr[i] + arr[j]
            if best is None or total > best:
                best = total
    return best""",
        """#include <vector>
using namespace std;
int ArrayAdditionI(vector<int> arr) {
    int best = arr[0] + arr[1];
    for (size_t i = 0; i < arr.size(); i++)
        for (size_t j = i+1; j < arr.size(); j++)
            if (arr[i] + arr[j] > best) best = arr[i] + arr[j];
    return best;
}""",
        """using System.Linq;
public class Program {
  public static int ArrayAdditionI(int[] arr) {
    int best = int.MinValue;
    for (int i = 0; i < arr.Length; i++)
      for (int j = i+1; j < arr.Length; j++)
        if (arr[i] + arr[j] > best) best = arr[i] + arr[j];
    return best;
  }
}""",
        """public class Solution {
  public static int arrayAdditionI(int[] arr) {
    int best = Integer.MIN_VALUE;
    for (int i = 0; i < arr.length; i++)
      for (int j = i+1; j < arr.length; j++)
        if (arr[i] + arr[j] > best) best = arr[i] + arr[j];
    return best;
  }
}""")),

    q("letter-count-i", "Letter Count I", EASY, [SM], "LetterCountI",
      "Have the function LetterCountI(str) take the str parameter being passed and return a string "
      "with all the letters that show up exactly once in the string, in alphabetical order.",
      (["str"], [STR]),
      [c(["abc"], "abc", STR), c(["aabbbcccc"], "", STR),
       c(["zxy"], "xyz", STR), c(["aabb"], "", STR)],
      S("""def LetterCountI(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    return "".join(sorted(ch for ch, n in counts.items() if n == 1))""",
        """#include <string>
#include <map>
using namespace std;
string LetterCountI(string str) {
    map<char, int> counts;
    for (char c : str) counts[c]++;
    string out;
    for (auto& kv : counts) if (kv.second == 1) out += kv.first;
    return out;
}""",
        """public class Program {
  public static string LetterCountI(string str) {
    return new string(str.GroupBy(c => c).Where(g => g.Count() == 1)
      .Select(g => g.Key).OrderBy(c => c).ToArray());
  }
}""",
        """public class Solution {
  public static String letterCountI(String str) {
    java.util.Map<Character, Integer> counts = new java.util.HashMap<>();
    for (char c : str.toCharArray())
      counts.merge(c, 1, Integer::sum);
    java.util.TreeMap<Character, Integer> sorted = new java.util.TreeMap<>(counts);
    StringBuilder sb = new StringBuilder();
    for (java.util.Map.Entry<Character, Integer> e : sorted.entrySet())
      if (e.getValue() == 1) sb.append(e.getKey());
    return sb.toString();
  }
}""")),

    q("second-greatlow", "Second GreatLow", EASY, [ALGO, SEARCH], "SecondGreatLow",
      "Have the function SecondGreatLow(arr) take the array of numbers stored in arr and return the "
      "second lowest distinct number in the array as an int. The array will not be empty, will "
      "contain only ints, and will not contain negative numbers.",
      (["arr"], ["array"]),
      [c([[2, 2, 5, 5, 5, 10, 10, 10]], 5, INT), c([[1, 2]], 2, INT),
       c([[3, 1, 2]], 2, INT)],
      S("""def SecondGreatLow(arr):
    distinct = sorted(set(arr))
    return distinct[1] if len(distinct) > 1 else -1""",
        """#include <vector>
#include <set>
using namespace std;
int SecondGreatLow(vector<int> arr) {
    set<int> s(arr.begin(), arr.end());
    if (s.size() < 2) return -1;
    auto it = s.begin();
    advance(it, 1);
    return *it;
}""",
        """using System.Linq;
public class Program {
  public static int SecondGreatLow(int[] arr) {
    var d = arr.Distinct().OrderBy(x => x).ToList();
    return d.Count > 1 ? d[1] : -1;
  }
}""",
        """import java.util.*;
public class Solution {
  public static int secondGreatLow(int[] arr) {
    TreeSet<Integer> s = new TreeSet<>();
    for (int v : arr) s.add(v);
    if (s.size() < 2) return -1;
    Iterator<Integer> it = s.iterator();
    it.next();
    return it.next();
  }
}""")),

    q("division-stringified", "Division Stringified", EASY, [MATH], "DivisionStringified",
      "Have the function DivisionStringified(number) take the number parameter being passed and "
      "return the number of seconds converted into a string format HH:MM:SS.",
      (["number"], [INT]),
      [c([100], "0:01:40", STR), c([3600], "1:00:00", STR),
       c([5030], "1:23:50", STR)],
      S("""def DivisionStringified(n):
    h = n // 3600
    m = (n % 3600) // 60
    s = n % 60
    return f"{h}:{m:02d}:{s:02d}\"""",
        """#include <string>
#include <cstdio>
using namespace std;
string DivisionStringified(int number) {
    int h = number / 3600;
    int m = (number % 3600) / 60;
    int s = number % 60;
    char buf[32];
    snprintf(buf, sizeof(buf), "%d:%02d:%02d", h, m, s);
    return string(buf);
}""",
        """public class Program {
  public static string DivisionStringified(int number) {
    return (number / 3600) + ":" + ((number % 3600) / 60).ToString("00")
         + ":" + (number % 60).ToString("00");
  }
}""",
        """public class Solution {
  public static String divisionStringified(int number) {
    return (number / 3600) + ":" + String.format("%02d", (number % 3600) / 60)
         + ":" + String.format("%02d", number % 60);
  }
}""")),

    q("counting-minutes-i", "Counting Minutes I", EASY, [MATH], "CountingMinutesI",
      "Have the function CountingMinutesI(str) take the str parameter being passed and give an array "
      "of the number of minutes for each segment of the day described by the input.",
      (["str"], [STR]),
      [c(["00:00 00:00"], [0], "array"), c(["09:00 12:00"], [180], "array"),
       c(["12:00 12:05"], [5], "array")],
      S("""def CountingMinutesI(s):
    a, b = s.split()
    to_min = lambda t: int(t[:2]) * 60 + int(t[3:])
    return [to_min(b) - to_min(a)]""",
        """#include <string>
#include <vector>
#include <sstream>
#include <cstdlib>
using namespace std;
static int to_min(const string& t) {
    return (t[0]-'0')*600 + (t[1]-'0')*60 + (t[3]-'0')*10 + (t[4]-'0');
}
vector<int> CountingMinutesI(string str) {
    stringstream ss(str);
    string a, b;
    ss >> a >> b;
    return vector<int>{ to_min(b) - to_min(a) };
}""",
        """public class Program {
  public static int[] CountingMinutesI(string str) {
    var parts = str.Split(' ');
    int Min(string t) => int.Parse(t.Substring(0,2)) * 60 + int.Parse(t.Substring(3,2));
    return new[] { Min(parts[1]) - Min(parts[0]) };
  }
}""",
        """import java.util.*;
public class Solution {
  static int toMin(String t) {
    return Integer.parseInt(t.substring(0,2)) * 60 + Integer.parseInt(t.substring(3,5));
  }
  public static int[] countingMinutesI(String str) {
    String[] parts = str.split(" ");
    return new int[]{ toMin(parts[1]) - toMin(parts[0]) };
  }
}""")),

    q("mean-mode", "Mean Mode", EASY, [ALGO, MATH], "MeanMode",
      "Have the function MeanMode(arr) take the array of numbers stored in arr and return the mode of "
      "the array. The array will always be non-empty and will not contain negative numbers. The mode "
      "is the number that appears most often; if several appear equally often, return the smallest.",
      (["arr"], ["array"]),
      [c([[1, 2, 2, 3]], 2, INT), c([[1, 1, 1, 2, 2]], 1, INT),
       c([[5, 4, 4, 4, 3, 3]], 4, INT)],
      S("""def MeanMode(arr):
    counts = {}
    for v in arr:
        counts[v] = counts.get(v, 0) + 1
    best, best_n = None, -1
    for v in arr:  # iterates in first-appearance order, so ties keep the first
        if counts[v] > best_n:
            best, best_n = v, counts[v]
    return best""",
        """#include <vector>
#include <map>
using namespace std;
int MeanMode(vector<int> arr) {
    map<int, int> counts;
    for (int v : arr) counts[v]++;
    int best = arr[0], best_n = 0;
    for (auto& kv : counts) if (kv.second > best_n) { best = kv.first; best_n = kv.second; }
    return best;
}""",
        """public class Program {
  public static int MeanMode(int[] arr) {
    return arr.GroupBy(x => x)
      .OrderByDescending(g => g.Count())
      .ThenBy(g => g.Key)
      .First().Key;
  }
}""",
        """import java.util.*;
public class Solution {
  public static int meanMode(int[] arr) {
    Map<Integer, Integer> counts = new java.util.HashMap<>();
    for (int v : arr) counts.merge(v, 1, Integer::sum);
    int best = Integer.MAX_VALUE, bestN = 0;
    for (Map.Entry<Integer, Integer> e : counts.entrySet())
      if (e.getValue() > bestN) { best = e.getKey(); bestN = e.getValue(); }
    return best;
  }
}""")),

    q("dash-insert", "Dash Insert", EASY, [SM], "DashInsert",
      "Have the function DashInsert(str) take the str parameter being passed and insert dashes "
      "between odd characters in odd-numbered positions.",
      (["str"], [STR]),
      [c(["13579"], "1-35-79", STR), c(["abcde"], "abcde", STR),
       c(["246"], "2-46", STR)],
      S("""def DashInsert(s):
    out = ''
    for i, ch in enumerate(s):
        if i > 0 and i % 2 == 1 and ch.isdigit() and s[i-1].isdigit():
            out += '-'
        out += ch
    return out""",
        """#include <string>
#include <cctype>
using namespace std;
string DashInsert(string str) {
    string out;
    for (size_t i = 0; i < str.size(); i++) {
        if (i > 0 && i % 2 == 1 && isdigit((unsigned char)str[i])
            && isdigit((unsigned char)str[i-1])) out += '-';
        out += str[i];
    }
    return out;
}""",
        """public class Program {
  public static string DashInsert(string str) {
    var sb = new System.Text.StringBuilder();
    for (int i = 0; i < str.Length; i++) {
      if (i > 0 && i % 2 == 1 && char.IsDigit(str[i]) && char.IsDigit(str[i-1]))
        sb.Append('-');
      sb.Append(str[i]);
    }
    return sb.ToString();
  }
}""",
        """public class Solution {
  public static String dashInsert(String str) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < str.length(); i++) {
      if (i > 0 && i % 2 == 1 && Character.isDigit(str.charAt(i))
          && Character.isDigit(str.charAt(i-1))) sb.append('-');
      sb.append(str.charAt(i));
    }
    return sb.toString();
  }
}""")),

    q("number-addition", "Number Addition", EASY, [SM], "NumberAddition",
      "Have the function NumberAddition(num) take the num parameter being passed and return the "
      "sum of its digits.",
      (["num"], [INT]),
      [c([5],  5, INT), c([12],  3, INT), c([34],  7, INT)],
      S("""def NumberAddition(n):
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total""",
        """int NumberAddition(int num) {
    int t = 0;
    while (num > 0) { t += num % 10; num /= 10; }
    return t;
}""",
        """public class Program {
  public static int NumberAddition(int num) {
    int t = 0;
    while (num > 0) { t += num % 10; num /= 10; }
    return t;
  }
}""",
        """public class Solution {
  public static int numberAddition(int num) {
    int t = 0;
    while (num > 0) { t += num % 10; num /= 10; }
    return t;
  }
}""")),

    q("multiplicative-persistence", "Multiplicative Persistence", EASY, [MATH], "MultiplicativePersistence",
      "Have the function MultiplicativePersistence(n) take the n parameter being passed and return "
      "the number of times you must multiply the digits until the result is a single digit.",
      (["n"], [INT]),
      [c([39],  3, INT), c([999],  4, INT), c([679],  5, INT), c([7],  0, INT)],
      S("""def MultiplicativePersistence(n):
    count = 0
    while n > 9:
        product = 1
        while n > 0:
            product *= n % 10
            n //= 10
        n = product
        count += 1
    return count""",
        """int MultiplicativePersistence(int n) {
    int count = 0;
    while (n > 9) {
        int p = 1;
        while (n > 0) { p *= n % 10; n /= 10; }
        n = p;
        count++;
    }
    return count;
}""",
        """public class Program {
  public static int MultiplicativePersistence(int n) {
    int count = 0;
    while (n > 9) {
      int p = 1;
      while (n > 0) { p *= n % 10; n /= 10; }
      n = p; count++;
    }
    return count;
  }
}""",
        """public class Solution {
  public static int multiplicativePersistence(int n) {
    int count = 0;
    while (n > 9) {
      int p = 1;
      while (n > 0) { p *= n % 10; n /= 10; }
      n = p; count++;
    }
    return count;
  }
}""")),

    q("off-line-minimum", "Off Line Minimum", EASY, [ALGO], "OffLineMinimum",
      "Have the function OffLineMinimum(arr) take the array of numbers stored in arr and return the "
      "lowest number that is not found in the sequence starting at 1.",
      (["arr"], ["array"]),
      [c([[1, 2, 5]],  3, INT), c([[3, 5, 8, 9]], 1, INT),
       c([[2, 3, 4, 5]], 1, INT), c([[1, 2, 3]], 4, INT)],
      S("""def OffLineMinimum(arr):
    numbers = set(arr)
    n = 1
    while n in numbers:
        n += 1
    return n""",
        """#include <vector>
#include <set>
using namespace std;
int OffLineMinimum(vector<int> arr) {
    set<int> s(arr.begin(), arr.end());
    int n = 1;
    while (s.count(n)) n++;
    return n;
}""",
        """public class Program {
  public static int OffLineMinimum(int[] arr) {
    var s = new System.Collections.Generic.HashSet<int>(arr);
    int n = 1;
    while (s.Contains(n)) n++;
    return n;
  }
}""",
        """import java.util.*;
public class Solution {
  public static int offLineMinimum(int[] arr) {
    Set<Integer> s = new HashSet<>();
    for (int v : arr) s.add(v);
    int n = 1;
    while (s.contains(n)) n++;
    return n;
  }
}""")),

    q("changing-sequence", "Changing Sequence", EASY, [MATH, ALGO], "ChangingSequence",
      "Have the function ChangingSequence(num) take the num parameter being passed and return the "
      "number of steps it takes to reach 1 by repeatedly dividing by 2 when even and subtracting 1 "
      "when odd.",
      (["num"], [INT]),
      [c([3],  2, INT), c([1],  0, INT), c([7],  4, INT), c([16],  4, INT)],
      S("""def ChangingSequence(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else n - 1
        steps += 1
    return steps""",
        """int ChangingSequence(int num) {
    int steps = 0;
    while (num != 1) {
        if (num % 2 == 0) num /= 2; else num -= 1;
        steps++;
    }
    return steps;
}""",
        """public class Program {
  public static int ChangingSequence(int num) {
    int steps = 0;
    while (num != 1) {
      if (num % 2 == 0) num /= 2; else num -= 1;
      steps++;
    }
    return steps;
  }
}""",
        """public class Solution {
  public static int changingSequence(int num) {
    int steps = 0;
    while (num != 1) {
      if (num % 2 == 0) num /= 2; else num -= 1;
      steps++;
    }
    return steps;
  }
}""")),

    q("overlapping-ranges", "Overlapping Ranges", EASY, [ALGO, MATH], "OverlappingRanges",
      "Have the function OverlappingRanges(array) take the array of strings stored in array and "
      "return the string true if any two ranges overlap, otherwise return false.",
      (["array"], ["array"]),
      [c([["1-3", "5-9"]], "false", STR), c([["1-3", "2-5"]], "true", STR),
       c([["1-3", "3-5"]], "true", STR)],
      S("""def OverlappingRanges(ranges):
    spans = []
    for r in ranges:
        a, b = r.split("-")
        spans.append((int(a), int(b)))
    for i in range(len(spans)):
        for j in range(i+1, len(spans)):
            s1, e1 = spans[i]
            s2, e2 = spans[j]
            if s1 <= e2 and s2 <= e1:
                return "true"
    return "false\"""",
        """#include <vector>
#include <string>
#include <sstream>
using namespace std;
static pair<int,int> parse(const string& r) {
    size_t d = r.find('-');
    return { atoi(r.substr(0, d).c_str()), atoi(r.substr(d+1).c_str()) };
}
string OverlappingRanges(vector<string> ranges) {
    for (size_t i = 0; i < ranges.size(); i++)
        for (size_t j = i+1; j < ranges.size(); j++) {
            auto a = parse(ranges[i]);
            auto b = parse(ranges[j]);
            if (a.first <= b.second && b.first <= a.second) return "true";
        }
    return "false";
}""",
        """public class Program {
  public static string OverlappingRanges(string[] ranges) {
    var spans = ranges.Select(r => r.Split('-')
      .Select(int.Parse).ToArray()).Select(p => (p[0], p[1])).ToArray();
    for (int i = 0; i < spans.Length; i++)
      for (int j = i+1; j < spans.Length; j++)
        if (spans[i].Item1 <= spans[j].Item2 && spans[j].Item1 <= spans[i].Item2)
          return "true";
    return "false";
  }
}""",
        """import java.util.*;
public class Solution {
  public static String overlappingRanges(String[] ranges) {
    int[][] spans = new int[ranges.length][2];
    for (int i = 0; i < ranges.length; i++) {
      String[] p = ranges[i].split("-");
      spans[i][0] = Integer.parseInt(p[0]);
      spans[i][1] = Integer.parseInt(p[1]);
    }
    for (int i = 0; i < spans.length; i++)
      for (int j = i+1; j < spans.length; j++)
        if (spans[i][0] <= spans[j][1] && spans[j][0] <= spans[i][1]) return "true";
    return "false";
  }
}""")),

    q("superincreasing", "Superincreasing", EASY, [ALGO], "Superincreasing",
      "Have the function Superincreasing(arr) take the array of numbers stored in arr and return "
      "the string true if each number in the array is greater than the sum of all numbers before it.",
      (["arr"], ["array"]),
      [c([[1, 2, 4, 8]],  "true", STR), c([[1, 2, 3, 4]],  "false", STR),
       c([[1]],  "true", STR)],
      S("""def Superincreasing(arr):
    total = 0
    for v in arr:
        if v <= total:
            return "false"
        total += v
    return "true\"""",
        """#include <vector>
using namespace std;
string Superincreasing(vector<int> arr) {
    int total = 0;
    for (int v : arr) { if (v <= total) return "false"; total += v; }
    return "true";
}""",
        """public class Program {
  public static string Superincreasing(int[] arr) {
    int total = 0;
    foreach (int v in arr) { if (v <= total) return "false"; total += v; }
    return "true";
  }
}""",
        """public class Solution {
  public static String superincreasing(int[] arr) {
    int total = 0;
    for (int v : arr) { if (v <= total) return "false"; total += v; }
    return "true";
  }
}""")),

    q("hamming-distance", "Hamming Distance", EASY, [MATH, ALGO], "HammingDistance",
      "Have the function HammingDistance(a, b) take the a and b parameters being passed and return "
      "the number of positions where the two strings differ.",
      (["a", "b"], [STR, STR]),
      [c(["abc", "abd"], 1, INT), c(["abc", "abc"], 0, INT),
       c(["1011101", "1001001"], 2, INT), c(["z", "a"], 1, INT)],
      S("""def HammingDistance(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)""",
        """#include <string>
using namespace std;
int HammingDistance(string a, string b) {
    int n = 0;
    for (size_t i = 0; i < a.size() && i < b.size(); i++) if (a[i] != b[i]) n++;
    return n;
}""",
        """public class Program {
  public static int HammingDistance(string a, string b) {
    return a.Zip(b, (x, y) => x == y ? 0 : 1).Sum();
  }
}""",
        """public class Solution {
  public static int hammingDistance(String a, String b) {
    int n = 0;
    for (int i = 0; i < a.length() && i < b.length(); i++)
      if (a.charAt(i) != b.charAt(i)) n++;
    return n;
  }
}""")),

    q("rectangle-area", "Rectangle Area", EASY, [MATH, ALGO], "RectangleArea",
      "Have the function RectangleArea(array) take the array of three integers stored in array and "
      "return the area of the rectangle. The third number is the width and the first two are the "
      "length and height.",
      (["array"], ["array"]),
      [c([[4, 5, 8]],  32, INT), c([[2, 3, 4]],  8, INT),
       c([[1, 10, 1]],  1, INT)],
      S("""def RectangleArea(a):
    return a[0] * a[2]""",
        """int RectangleArea(vector<int> a) { return a[0] * a[2]; }""",
        """public class Program {
  public static int RectangleArea(int[] a) { return a[0] * a[2]; }
}""",
        """public class Solution {
  public static int rectangleArea(int[] a) { return a[0] * a[2]; }
}""")),

    q("other-products", "Other Products", EASY, [ALGO, MATH], "OtherProducts",
      "Have the function OtherProducts(array) take the array of numbers stored in array and return "
      "an array of the products of every other element in the array.",
      (["array"], ["array"]),
      [c([[1, 2, 3, 4]],  [24, 12, 8, 6], "array"),
       c([[1, 1]],  [1, 1], "array"), c([[1, 2, 3, 4, 5]],  [120, 60, 40, 30, 24], "array")],
      S("""def OtherProducts(a):
    total = 1
    for v in a:
        total *= v
    return [total // v if v else 0 for v in a]""",
        """#include <vector>
using namespace std;
vector<int> OtherProducts(vector<int> a) {
    long long total = 1;
    for (int v : a) total *= v;
    vector<int> out;
    for (int v : a) out.push_back(v == 0 ? 0 : (int)(total / v));
    return out;
}""",
        """public class Program {
  public static int[] OtherProducts(int[] a) {
    long total = 1;
    foreach (int v in a) total *= v;
    return a.Select(v => v == 0 ? 0 : (int)(total / v)).ToArray();
  }
}""",
        """public class Solution {
  public static int[] otherProducts(int[] a) {
    long total = 1;
    for (int v : a) total *= v;
    int[] out = new int[a.length];
    for (int i = 0; i < a.length; i++) out[i] = a[i] == 0 ? 0 : (int)(total / a[i]);
    return out;
  }
}""")),

    q("wave-sorting", "Wave Sorting", EASY, [ALGO], "WaveSorting",
      "Have the function WaveSorting(arr) take the array of numbers stored in arr and sort it into "
      "a wave pattern where arr[0] > arr[1] < arr[2] > arr[3] < ... (not perfect but close enough).",
      (["arr"], ["array"]),
      [c([[2, 1, 4, 3, 6]],  [6, 1, 4, 2, 3], "array"),
       c([[5, 6, 7, 8, 9]],  [9, 5, 8, 6, 7], "array")],
      S("""def WaveSorting(arr):
    a = sorted(arr)
    lo, hi, out = 0, len(a) - 1, []
    while lo <= hi:
        out.append(a[hi]); hi -= 1
        if lo <= hi:
            out.append(a[lo]); lo += 1
    return out""",
        """#include <vector>
#include <algorithm>
using namespace std;
vector<int> WaveSorting(vector<int> arr) {
    sort(arr.begin(), arr.end());
    vector<int> out;
    int lo = 0, hi = arr.size() - 1;
    while (lo <= hi) {
        out.push_back(arr[hi--]);
        if (lo <= hi) out.push_back(arr[lo++]);
    }
    return out;
}""",
        """public class Program {
  public static int[] WaveSorting(int[] arr) {
    var a = arr.OrderBy(x => x).ToList();
    var outv = new System.Collections.Generic.List<int>();
    int lo = 0, hi = a.Count - 1;
    while (lo <= hi) {
      outv.Add(a[hi--]);
      if (lo <= hi) outv.Add(a[lo++]);
    }
    return outv.ToArray();
  }
}""",
        """import java.util.*;
public class Solution {
  public static int[] waveSorting(int[] arr) {
    int[] a = arr.clone();
    Arrays.sort(a);
    int[] out = new int[a.length];
    int lo = 0, hi = a.length - 1, k = 0;
    while (lo <= hi) {
      out[k++] = a[hi--];
      if (lo <= hi) out[k++] = a[lo++];
    }
    return out;
  }
}""")),

    q("array-matching", "Array Matching", EASY, [ALGO, SEARCH], "ArrayMatching",
      "Have the function ArrayMatching(array) take the array of two strings stored in array and "
      "return a boolean true if the strings contain the same number of characters.",
      (["array"], ["array"]),
      [c([["hi", "hello"]],  "false", STR), c([["hey", "hello"]],  "false", STR),
       c([["hello", "hi"]],  "false", STR)],
      S("""def ArrayMatching(a):
    return "true" if len(a[0]) == len(a[1]) else "false\"""",
        """#include <vector>
#include <string>
using namespace std;
string ArrayMatching(vector<string> a) {
    return a[0].size() == a[1].size() ? "true" : "false";
}""",
        """public class Program {
  public static string ArrayMatching(string[] a) {
    return a[0].Length == a[1].Length ? "true" : "false";
  }
}""",
        """public class Solution {
  public static String arrayMatching(String[] a) {
    return a[0].length() == a[1].length() ? "true" : "false";
  }
}""")),

    q("even-pairs", "Even Pairs", EASY, [ALGO, SEARCH], "EvenPairs",
      "Have the function EvenPairs(arr) take the array of numbers stored in arr and return the total "
      "number of even integer pairs you can make from the array.",
      (["arr"], ["array"]),
      [c([[1, 2, 3, 4]],  4, INT), c([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],  25, INT),
       c([[1, 4, 6, 8]],  3, INT)],
      S("""def EvenPairs(arr):
    evens = sum(1 for v in arr if v % 2 == 0)
    odds = len(arr) - evens
    return evens * odds""",
        """#include <vector>
using namespace std;
int EvenPairs(vector<int> arr) {
    int e = 0;
    for (int v : arr)    if (v % 2 == 0) e++;
    int o = (int)arr.size() - e;
    return e * o;
}""",
        """public class Program {
  public static int EvenPairs(int[] arr) {
    int e = arr.Count(v => v % 2 == 0);
    int o = arr.Length - e;
    return e * o;
  }
}""",
        """public class Solution {
  public static int evenPairs(int[] arr) {
    int e = 0;
    for (int v : arr) if (v % 2 == 0) e++;
    int o = arr.length - e;
    return e * o;
  }
}""")),

    q("largest-pair", "Largest Pair", EASY, [ALGO, MATH], "LargestPair",
      "Have the function LargestPair(numbers, pair) take a comma-separated list of numbers and a "
      "comma-separated pair. Return true if the pair sums to exactly half of all the numbers.",
      (["numbers", "pair"], [STR, STR]),
      [c(["2,4,6", "3,3"], "true", STR),
       c(["1,2,3,4,5,6", "1,2"], "false", STR),
       c(["4,5,6", "1,1"], "false", STR)],
      S("""def LargestPair(numbers, pair):
    values = [int(v) for v in numbers.split(",")]
    total = sum(values)
    if total % 2 or (total // 2) not in values:
        return "false"
    parts = [int(p) for p in pair.split(",")]
    return "true" if parts[0] + parts[1] == total // 2 else "false\"""",
        """#include <vector>
#include <string>
#include <cstdlib>
using namespace std;
string LargestPair(string numbers, string pair) {
    vector<int> values;
    stringstream ss(numbers);
    string tok;
    while (getline(ss, tok, ',')) values.push_back(atoi(tok.c_str()));
    int total = 0;
    for (int v : values) total += v;
    if (total % 2) return "false";
    int half = total / 2;
    bool found = false;
    for (int v : values) if (v == half) found = true;
    if (!found) return "false";
    size_t comma = pair.find(',');
    int p = atoi(pair.substr(0, comma).c_str());
    int q = atoi(pair.substr(comma + 1).c_str());
    return (p + q == half) ? "true" : "false";
}""",
        """using System.Linq;
public class Program {
  public static string LargestPair(string numbers, string pair) {
    var values = numbers.Split(',').Select(int.Parse).ToArray();
    int total = values.Sum();
    if (total % 2 != 0) return "false";
    int half = total / 2;
    if (!values.Contains(half)) return "false";
    var parts = pair.Split(',').Select(int.Parse).ToArray();
    return parts[0] + parts[1] == half ? "true" : "false";
  }
}""",
        """public class Solution {
  public static String largestPair(String numbers, String pair) {
    int total = 0;
    boolean found = false;
    for (String v : numbers.split(",")) total += Integer.parseInt(v);
    if (total % 2 != 0) return "false";
    int half = total / 2;
    for (String v : numbers.split(",")) if (Integer.parseInt(v) == half) found = true;
    if (!found) return "false";
    String[] parts = pair.split(",");
    int sum = Integer.parseInt(parts[0]) + Integer.parseInt(parts[1]);
    return sum == half ? "true" : "false";
  }
}""")),

    q("nonrepeating-character", "Nonrepeating Character", EASY, [SEARCH, SM], "NonRepeatingCharacter",
      "Have the function NonRepeatingCharacter(str) take the str parameter being passed and return "
      "the index number of the first non-repeating character in the string.",
      (["str"], [STR]),
      [c(["swiss"], 1, INT), c(["aabbccdd"], -1, INT),
       c(["zxvcasdf"], 0, INT), c(["x"], 0, INT)],
      S("""def NonRepeatingCharacter(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1""",
        """#include <string>
#include <map>
using namespace std;
int NonRepeatingCharacter(string str) {
    map<char, int> counts;
    for (char c : str) counts[c]++;
    for (size_t i = 0; i < str.size(); i++) if (counts[str[i]] == 1) return (int)i;
    return -1;
}""",
        """public class Program {
  public static int NonRepeatingCharacter(string str) {
    var counts = str.GroupBy(c => c).ToDictionary(g => g.Key, g => g.Count());
    for (int i = 0; i < str.Length; i++) if (counts[str[i]] == 1) return i;
    return -1;
  }
}""",
        """import java.util.*;
public class Solution {
  public static int nonRepeatingCharacter(String str) {
    Map<Character, Integer> counts = new HashMap<>();
    for (char c : str.toCharArray()) counts.merge(c, 1, Integer::sum);
    for (int i = 0; i < str.length(); i++)
      if (counts.get(str.charAt(i)) == 1) return i;
    return -1;
  }
}""")),

    q("two-sum", "Two Sum", EASY, [SEARCH, ALGO], "TwoSum",
      "Have the function TwoSum(num, target) take the array of numbers stored in num and return the "
      "two numbers that add up to target, or the string not possible if no such pair exists.",
      (["num", "target"], ["array", INT]),
      [c([[7, 3, 2], 9],  [2, 7], "array"), c([[3, 2, 1], 3],  [1, 2], "array"),
       c([[1, 2, 3], 100],  "not possible", STR)],
      S("""def TwoSum(num, target):
    seen = set()
    for v in num:
        if target - v in seen:
            return [v, target - v]
        seen.add(v)
    return "not possible\"""",
        """#include <vector>
#include <string>
#include <map>
using namespace std;
CBResult TwoSum(vector<int> num, int target) {
    set<int> seen;
    for (int v : num) {
        if (seen.count(target - v)) return vector<int>{ v, target - v };
        seen.insert(v);
    }
    return string("not possible");
}""",
        """using System.Linq;
using System.Collections.Generic;
public class Program {
  public static object TwoSum(int[] num, int target) {
    var seen = new HashSet<int>();
    foreach (int v in num) {
      if (seen.Contains(target - v)) return new[] { v, target - v };
      seen.Add(v);
    }
    return "not possible";
  }
}""",
        """import java.util.*;
public class Solution {
  public static Object twoSum(int[] num, int target) {
    Set<Integer> seen = new HashSet<>();
    for (int v : num) {
      if (seen.contains(target - v)) return new int[]{ v, target - v };
      seen.add(v);
    }
    return "not possible";
  }
}""")),

    q("product-digits", "Product Digits", EASY, [MATH], "ProductDigits",
      "Have the function ProductDigits(num) take the num parameter being passed and return the "
      "product of its digits.",
      (["num"], [INT]),
      [c([39],  27, INT), c([2],  2, INT), c([22],  4, INT)],
      S("""def ProductDigits(n):
    product = 1
    while n > 0:
        product *= n % 10
        n //= 10
    return product""",
        """int ProductDigits(int num) {
    int p = 1;
    while (num > 0) { p *= num % 10; num /= 10; }
    return p;
}""",
        """public class Program {
  public static int ProductDigits(int num) {
    int p = 1;
    while (num > 0) { p *= num % 10; num /= 10; }
    return p;
  }
}""",
        """public class Solution {
  public static int productDigits(int num) {
    int p = 1;
    while (num > 0) { p *= num % 10; num /= 10; }
    return p;
  }
}""")),

    q("basic-roman-numerals", "Basic Roman Numerals", EASY, [SM, MATH], "RomanNumerals",
      "Have the function RomanNumerals(number) take the number parameter being passed and return "
      "the number as a Roman numeral.",
      (["number"], [INT]),
      [c([1],  "I", STR), c([4],  "IV", STR), c([5],  "V", STR),
       c([9],  "IX", STR), c([12],  "XII", STR), c([16],  "XVI", STR)],
      S("""def RomanNumerals(n):
    table = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),
             (50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
    out = ""
    for value, sym in table:
        while n >= value:
            out += sym
            n -= value
    return out""",
        """#include <string>
using namespace std;
string RomanNumerals(int number) {
    int values[] = {1000,900,500,400,100,90,50,40,10,9,5,4,1};
    const char* syms[] = {"M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"};
    string out;
    for (int i = 0; i < 13; i++)
        while (number >= values[i]) { out += syms[i]; number -= values[i]; }
    return out;
}""",
        """public class Program {
  public static string RomanNumerals(int number) {
    int[] v = {1000,900,500,400,100,90,50,40,10,9,5,4,1};
    string[] s = {"M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"};
    var sb = new System.Text.StringBuilder();
    for (int i = 0; i < 13; i++)
      while (number >= v[i]) { sb.Append(s[i]); number -= v[i]; }
    return sb.ToString();
  }
}""",
        """public class Solution {
  public static String romanNumerals(int number) {
    int[] v = {1000,900,500,400,100,90,50,40,10,9,5,4,1};
    String[] s = {"M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"};
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < 13; i++)
      while (number >= v[i]) { sb.append(s[i]); number -= v[i]; }
    return sb.toString();
  }
}""")),

    q("binary-reversal", "Binary Reversal", EASY, [MATH, ALGO], "BinaryReversal",
      "Have the function BinaryReversal(n) take the number parameter being passed and return the "
      "reverse of its binary representation as a decimal number.",
      (["n"], [INT]),
      [c([12],  3, INT), c([100],  19, INT), c([350],  245, INT), c([5],  5, INT)],
      S("""def BinaryReversal(n):
    out = 0
    while n > 0:
        out = out * 2 + (n % 2)
        n //= 2
    return out""",
        """int BinaryReversal(int n) {
    int out = 0;
    while (n > 0) { out = out * 2 + (n % 2); n /= 2; }
    return out;
}""",
        """public class Program {
  public static int BinaryReversal(int n) {
    int reversed = 0;
    while (n > 0) { reversed = reversed * 2 + (n % 2); n /= 2; }
    return reversed;
  }
}""",
        """public class Solution {
  public static int binaryReversal(int n) {
    int out = 0;
    while (n > 0) { out = out * 2 + (n % 2); n /= 2; }
    return out;
  }
}""")),

    q("ab-check", "AB Check", EASY, [SM, SEARCH], "ABCheck",
      "Have the function ABCheck(str) take the str parameter being passed and return the string true "
      "if the characters a and b occur the same number of times, otherwise return false.",
      (["str"], [STR]),
      [c(["aabbc"], "true", STR), c(["xyzabc"], "true", STR),
       c(["a"], "false", STR), c(["abba"], "true", STR)],
      S("""def ABCheck(s):
    return "true" if s.count("a") == s.count("b") else "false\"""",
        """#include <string>
using namespace std;
string ABCheck(string str) {
    int a = 0, b = 0;
    for (char c : str) { if (c == 'a') a++; else if (c == 'b') b++; }
    return a == b ? "true" : "false";
}""",
        """public class Program {
  public static string ABCheck(string str) {
    return str.Count(c => c == 'a') == str.Count(c => c == 'b') ? "true" : "false";
  }
}""",
        """public class Solution {
  public static String aBCheck(String str) {
    int a = 0, b = 0;
    for (char c : str.toCharArray()) { if (c == 'a') a++; else if (c == 'b') b++; }
    return a == b ? "true" : "false";
  }
}""")),

    q("bitwise-one", "Bitwise One", EASY, [MATH, ALGO], "BitwiseOne",
      "Have the function BitwiseOne(num) take the num parameter being passed and return the number "
      "of ones in the binary representation.",
      (["num"], [INT]),
      [c([10],  2, INT), c([1],  1, INT), c([7],  3, INT), c([0],  0, INT)],
      S("""def BitwiseOne(n):
    count = 0
    while n > 0:
        count += n % 2
        n //= 2
    return count""",
        """int BitwiseOne(int num) {
    int c = 0;
    while (num > 0) { c += num % 2; num /= 2; }
    return c;
}""",
        """public class Program {
  public static int BitwiseOne(int num) {
    int c = 0;
    while (num > 0) { c += num % 2; num /= 2; }
    return c;
  }
}""",
        """public class Solution {
  public static int bitwiseOne(int num) {
    int c = 0;
    while (num > 0) { c += num % 2; num /= 2; }
    return c;
  }
}""")),

    # ── Medium ─────────────────────────────────────────────────────────────
    q("simple-mode", "Simple Mode", MEDIUM, [ALGO, MATH], "SimpleMode",
      "Have the function SimpleMode(array) take the array of numbers stored in array and return the "
      "number that appears most often. If several appear equally often, return the smallest.",
      (["array"], ["array"]),
      [c([[2, 2, 1, 1, 1, 3, 3, 3, 3, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 0, INT),
       c([[2, 4, 6, 8, 10]],  2, INT)],
      S("""def SimpleMode(a):
    counts = {}
    for v in a:
        counts[v] = counts.get(v, 0) + 1
    best, best_n = None, -1
    for v in a:
        if counts[v] > best_n:
            best, best_n = v, counts[v]
    return best""",
        """#include <vector>
#include <map>
using namespace std;
int SimpleMode(vector<int> a) {
    map<int, int> counts;
    for (int v : a) counts[v]++;
    int best = a[0], best_n = 0;
    for (auto& kv : counts) if (kv.second > best_n) { best = kv.first; best_n = kv.second; }
    return best;
}""",
        """public class Program {
  public static int SimpleMode(int[] a) {
    return a.GroupBy(x => x).OrderByDescending(g => g.Count())
      .ThenBy(g => g.Key).First().Key;
  }
}""",
        """import java.util.*;
public class Solution {
  public static int simpleMode(int[] a) {
    Map<Integer, Integer> counts = new java.util.HashMap<>();
    for (int v : a) counts.merge(v, 1, Integer::sum);
    int best = 0, bestN = -1;
    for (Map.Entry<Integer, Integer> e : counts.entrySet())
      if (e.getValue() > bestN) { best = e.getKey(); bestN = e.getValue(); }
    return best;
  }
}""")),

    q("consecutive", "Consecutive", MEDIUM, [ALGO, SEARCH], "Consecutive",
      "Have the function Consecutive(array) take the array of numbers stored in array and return the "
      "number of sequences of consecutive integers it contains.",
      (["array"], ["array"]),
      [c([[5, 6, 7, 8, 9]],  1, INT), c([[5, 5, 6, 6, 8, 9]],  2, INT),
       c([[2, 1, 1]],  1, INT)],
      S("""def Consecutive(a):
    a = sorted(a)
    count = 0
    current = 1
    for i in range(1, len(a)):
        if a[i] == a[i-1] + 1:
            current += 1
        else:
            if current > 1:
                count += 1
            current = 1
    if current > 1:
        count += 1
    return count""",
        """#include <vector>
#include <algorithm>
using namespace std;
int Consecutive(vector<int> a) {
    sort(a.begin(), a.end());
    int count = 0, current = 1;
    for (size_t i = 1; i < a.size(); i++) {
        if (a[i] == a[i-1] + 1) current++;
        else { if (current > 1) count++; current = 1; }
    }
    if (current > 1) count++;
    return count;
}""",
        """public class Program {
  public static int Consecutive(int[] a) {
    var sorted = a.OrderBy(x => x).ToArray();
    int count = 0, current = 1;
    for (int i = 1; i < sorted.Length; i++) {
      if (sorted[i] == sorted[i-1] + 1) current++;
      else { if (current > 1) count++; current = 1; }
    }
    if (current > 1) count++;
    return count;
  }
}""",
        """import java.util.*;
public class Solution {
  public static int consecutive(int[] a) {
    int[] sorted = a.clone();
    Arrays.sort(sorted);
    int count = 0, current = 1;
    for (int i = 1; i < sorted.length; i++) {
      if (sorted[i] == sorted[i-1] + 1) current++;
      else { if (current > 1) count++; current = 1; }
    }
    if (current > 1) count++;
    return count;
  }
}""")),

    q("prime-time", "Prime Time", MEDIUM, [MATH, ALGO], "PrimeTime",
      "Have the function PrimeTime(num) take the num parameter being passed and return the number "
      "of prime numbers less than num.",
      (["num"], [INT]),
      [c([10],  4, INT), c([5],  2, INT), c([25],  9, INT), c([2],  0, INT)],
      S("""def PrimeTime(n):
    def is_prime(v):
        if v < 2:
            return False
        i = 2
        while i * i <= v:
            if v % i == 0:
                return False
            i += 1
        return True
    return sum(1 for v in range(0, n) if is_prime(v))""",
        """bool is_prime(int v) {
    if (v < 2) return false;
    for (int i = 2; i * i <= v; i++) if (v % i == 0) return false;
    return true;
}
int PrimeTime(int num) {
    int count = 0;
    for (int v = 0; v < num; v++) if (is_prime(v)) count++;
    return count;
}""",
        """public class Program {
  public static int PrimeTime(int num) {
    int count = 0;
    for (int v = 0; v < num; v++) {
      bool prime = v >= 2;
      for (int i = 2; prime && i * i <= v; i++) if (v % i == 0) prime = false;
      if (prime) count++;
    }
    return count;
  }
}""",
        """public class Solution {
  static boolean isPrime(int v) {
    if (v < 2) return false;
    for (int i = 2; i * i <= v; i++) if (v % i == 0) return false;
    return true;
  }
  public static int primeTime(int num) {
    int count = 0;
    for (int v = 0; v < num; v++) if (isPrime(v)) count++;
    return count;
  }
}""")),

    q("array-addition", "Array Addition", MEDIUM, [SEARCH, ALGO], "ArrayAddition",
      "Have the function ArrayAddition(array) take the array of strings stored in array and return "
      "the string formed by concatenating the two numbers whose sum is 0.",
      (["array"], ["array"]),
      [c([["7", "2", "8", "2", "4"]],  "not possible", STR),
       c([["1", "2", "3", "4"]],  "not possible", STR),
       c([["-1, -2, -3, 1, 3"]],  "-11", STR)],
      S("""def ArrayAddition(a):
    nums = [int(v) for v in a[0].split(",")]
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == 0:
                return str(nums[i]) + str(nums[j])
    return "not possible\"""",
        """#include <vector>
#include <string>
#include <sstream>
using namespace std;
string ArrayAddition(vector<string> a) {
    vector<int> nums;
    stringstream ss(a[0]);
    string tok;
    while (getline(ss, tok, ',')) nums.push_back(atoi(tok.c_str()));
    for (size_t i = 0; i < nums.size(); i++)
        for (size_t j = i+1; j < nums.size(); j++)
            if (nums[i] + nums[j] == 0)
                return to_string(nums[i]) + to_string(nums[j]);
    return "not possible";
}""",
        """using System.Linq;
public class Program {
  public static string ArrayAddition(string[] a) {
    var nums = a[0].Split(',').Select(int.Parse).ToArray();
    for (int i = 0; i < nums.Length; i++)
      for (int j = i+1; j < nums.Length; j++)
        if (nums[i] + nums[j] == 0) return nums[i].ToString() + nums[j].ToString();
    return "not possible";
  }
}""",
        """public class Solution {
  public static String arrayAddition(String[] a) {
    String[] parts = a[0].split(",");
    int[] nums = new int[parts.length];
    for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i].trim());
    for (int i = 0; i < nums.length; i++)
      for (int j = i+1; j < nums.length; j++)
        if (nums[i] + nums[j] == 0) return String.valueOf(nums[i]) + nums[j];
    return "not possible";
  }
}""")),

    q("caesar-cipher", "Caesar Cipher", MEDIUM, [SM], "CaesarCipher",
      "Have the function CaesarCipher(str, num) take the str and num parameters being passed and "
      "return a Caesar-encrypted version of the string.",
      (["str", "num"], [STR, INT]),
      [c(["middle-Outz", 2],  "okffng-Qwvb", STR),
       c(["abc", 1],  "bcd", STR), c(["abc", 26],  "abc", STR)],
      S("""def CaesarCipher(s, n):
    out = ""
    for ch in s:
        if ch.islower():
            out += chr((ord(ch) - ord('a') + n) % 26 + ord('a'))
        elif ch.isupper():
            out += chr((ord(ch) - ord('A') + n) % 26 + ord('A'))
        else:
            out += ch
    return out""",
        """#include <string>
#include <cctype>
using namespace std;
string CaesarCipher(string str, int num) {
    string out;
    for (char c : str) {
        if (islower((unsigned char)c)) out += char((c - 'a' + num) % 26 + 'a');
        else if (isupper((unsigned char)c)) out += char((c - 'A' + num) % 26 + 'A');
        else out += c;
    }
    return out;
}""",
        """public class Program {
  public static string CaesarCipher(string str, int num) {
    var sb = new System.Text.StringBuilder();
    foreach (char c in str) {
      if (char.IsLower(c)) sb.Append((char)(((c - 'a' + num) % 26) + 'a'));
      else if (char.IsUpper(c)) sb.Append((char)(((c - 'A' + num) % 26) + 'A'));
      else sb.Append(c);
    }
    return sb.ToString();
  }
}""",
        """public class Solution {
  public static String caesarCipher(String str, int num) {
    StringBuilder sb = new StringBuilder();
    for (char c : str.toCharArray()) {
      if (Character.isLowerCase(c)) sb.append((char)(((c - 'a' + num) % 26) + 'a'));
      else if (Character.isUpperCase(c)) sb.append((char)(((c - 'A' + num) % 26) + 'A'));
      else sb.append(c);
    }
    return sb.toString();
  }
}""")),

    q("bracket-matcher", "Bracket Matcher", MEDIUM, [SM, SEARCH], "BracketMatcher",
      "Have the function BracketMatcher(str) take the str parameter being passed and return true if "
      "all the brackets are matched, otherwise return false. Ignore all other characters.",
      (["str"], [STR]),
      [c(["(Hello (World)) )"], "false", STR), c(["[(Hello)]"], "true", STR),
       c(["(hello))"], "false", STR), c(["(hello]"], "false", STR)],
      S("""def BracketMatcher(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return "false"
    return "true" if not stack else "false\"""",
        """#include <string>
#include <stack>
using namespace std;
string BracketMatcher(string str) {
    stack<char> st;
    for (char c : str) {
        if (c=='(' || c=='[' || c=='{') st.push(c);
        else if (c==')' && !st.empty() && st.top()=='(') st.pop();
      else if (c==']' && !st.empty() && st.top()=='[') st.pop();
      else if (c=='}' && !st.empty() && st.top()=='{') st.pop();
      else if (c==')' || c==']' || c=='}') return "false";

    }
    return st.empty() ? "true" : "false";
}""",
        """using System.Collections.Generic;
public class Program {
  public static string BracketMatcher(string str) {
    var st = new Stack<char>();
    foreach (char c in str) {
      if (c=='(' || c=='[' || c=='{') st.Push(c);
      else if (c==')' || c==']' || c=='}') {
        char open = c==')' ? '(' : c==']' ? '[' : '{';
        if (st.Count == 0 || st.Pop() != open) return "false";
      }
    }
    return st.Count == 0 ? "true" : "false";
  }
}""",
        """import java.util.*;
public class Solution {
  public static String bracketMatcher(String str) {
    Deque<Character> st = new ArrayDeque<>();
    for (char c : str.toCharArray()) {
      if (c=='(' || c=='[' || c=='{') st.push(c);
      else if (c==')' || c==']' || c=='}') {
        char open = c==')' ? '(' : c==']' ? '[' : '{';
        if (st.isEmpty() || st.pop() != open) return "false";
      }
    }
    return st.isEmpty() ? "true" : "false";
  }
}""")),

    q("string-reduction", "String Reduction", MEDIUM, [SM, ALGO], "StringReduction",
      "Have the function StringReduction(str) take the str parameter being passed and return the "
      "shortest string that produces the same result when characters are repeatedly reduced in "
      "pairs to their alphabetical difference.",
      (["str"], [STR]),
      [c(["cededgedlos"], "o", STR), c(["abc"], "b", STR),
       c(["aaabbbcdd"], "b", STR)],
      S("""def StringReduction(s):
    stack = []
    for ch in s:
        if stack:
            d = abs(ord(stack.pop()) - ord(ch))
            stack.append(chr(ord('a') + d))
        else:
            stack.append(ch)
    return "".join(stack)""",
        """#include <string>
#include <stack>
#include <cstdlib>
using namespace std;
string StringReduction(string str) {
    string st;
    for (char c : str) {
        if (!st.empty()) {
            int d = abs(st.back() - c);
            st.pop_back();
            st += char('a' + d);
        } else st += c;
    }
    return st;
}""",
        """using System.Collections.Generic;
using System.Linq;
public class Program {
  public static string StringReduction(string str) {
    var st = new Stack<char>();
    foreach (char c in str) {
      if (st.Count > 0) {
        int d = Math.Abs(st.Pop() - c);
        st.Push((char)('a' + d));
      } else st.Push(c);
    }
    return new string(st.Reverse().ToArray());
  }
}""",
        """import java.util.*;
public class Solution {
  public static String stringReduction(String str) {
    Deque<Character> st = new ArrayDeque<>();
    for (char c : str.toCharArray()) {
      if (!st.isEmpty()) {
        int d = Math.abs(st.pop() - c);
        st.push((char)('a' + d));
      } else st.push(c);
    }
    StringBuilder sb = new StringBuilder();
    while (!st.isEmpty()) sb.append(st.pop());
    return sb.toString();
  }
}""")),

    q("coin-determiner", "Coin Determiner", MEDIUM, [MATH, ALGO], "CoinDeterminer",
      "Have the function CoinDeterminer(coins, amount) take the coins and amount parameters being "
      "passed and return the fewest number of coins needed to make up that amount.",
      (["coins", "amount"], ["array", INT]),
      [c([[1, 5, 10, 25], 30], 2, INT),
       c([[1, 5, 10, 25], 20], 2, INT),
       c([[5, 10], 3],  -1, INT)],
      S("""def CoinDeterminer(coins, amount):
    dp = [0] + [float('inf')] * amount
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a:
                dp[a] = min(dp[a], dp[a-coin] + 1)
    return -1 if dp[amount] == float('inf') else dp[amount]""",
        """#include <vector>
#include <algorithm>
using namespace std;
int CoinDeterminer(vector<int> coins, int amount) {
    const int INF = 1e9;
    vector<int> dp(amount + 1, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int coin : coins)
            if (coin <= a) dp[a] = min(dp[a], dp[a-coin] + 1);
    return dp[amount] == INF ? -1 : dp[amount];
}""",
        """public class Program {
  public static int CoinDeterminer(int[] coins, int amount) {
    int INF = int.MaxValue / 2;
    var dp = new int[amount + 1];
    for (int i = 1; i <= amount; i++) dp[i] = INF;
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
      foreach (int coin in coins)
        if (coin <= a) dp[a] = Math.Min(dp[a], dp[a-coin] + 1);
    return dp[amount] >= INF ? -1 : dp[amount];
  }
}""",
        """import java.util.*;
public class Solution {
  public static int coinDeterminer(int[] coins, int amount) {
    int INF = Integer.MAX_VALUE / 2;
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
      for (int coin : coins)
        if (coin <= a) dp[a] = Math.min(dp[a], dp[a-coin] + 1);
    return dp[amount] >= INF ? -1 : dp[amount];
  }
}""")),

    q("longest-increasing-sequence", "Longest Increasing Sequence", EASY, [ALGO], "LongestIncreasingSequence",
      "Have the function LongestIncreasingSequence(arr) take the array of numbers stored in arr and "
      "return the length of the longest increasing subsequence.",
      (["arr"], ["array"]),
      [c([[1, 2, 3, 4]],  4, INT), c([[3, 2, 1, 4]],  2, INT),
       c([[10, 22, 5, 75, 65, 80]],  4, INT)],
      S("""def LongestIncreasingSequence(a):
    if not a:
        return 0
    best = [1] * len(a)
    for i in range(1, len(a)):
        for j in range(i):
            if a[j] < a[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best)""",
        """#include <vector>
#include <algorithm>
using namespace std;
int LongestIncreasingSequence(vector<int> a) {
    if (a.empty()) return 0;
    vector<int> best(a.size(), 1);
    int out = 1;
    for (size_t i = 1; i < a.size(); i++) {
        for (size_t j = 0; j < i; j++)
            if (a[j] < a[i]) best[i] = max(best[i], best[j] + 1);
        out = max(out, best[i]);
    }
    return out;
}""",
        """using System.Linq;
public class Program {
  public static int LongestIncreasingSequence(int[] a) {
    if (a.Length == 0) return 0;
    var best = new int[a.Length];
    for (int i = 0; i < a.Length; i++) {
      best[i] = 1;
      for (int j = 0; j < i; j++) if (a[j] < a[i]) best[i] = Math.Max(best[i], best[j] + 1);
    }
    return best.Max();
  }
}""",
        """import java.util.*;
public class Solution {
  public static int longestIncreasingSequence(int[] a) {
    if (a.length == 0) return 0;
    int[] best = new int[a.length];
    Arrays.fill(best, 1);
    int longest = 1;
    for (int i = 1; i < a.length; i++) {
      for (int j = 0; j < i; j++) if (a[j] < a[i]) best[i] = Math.max(best[i], best[j] + 1);
      longest = Math.max(longest, best[i]);
    }
    return longest;
  }
}""")),

    q("three-five-multiples", "ThreeFive Multiples", MEDIUM, [MATH, ALGO], "ThreeFiveMultiples",
      "Have the function ThreeFiveMultiples(start, limit) take the start and limit parameters being "
      "passed and return the sum of all the multiples of 3 or 5 between them.",
      (["start", "limit"], [INT, INT]),
      [c([1, 20],  98, INT), c([5, 10],  30, INT), c([3, 5],  8, INT)],
      S("""def ThreeFiveMultiples(start, limit):
    total = 0
    for n in range(start, limit + 1):
        if n % 3 == 0 or n % 5 == 0:
            total += n
    return total""",
        """int ThreeFiveMultiples(int start, int limit) {
    int total = 0;
    for (int n = start; n <= limit; n++)
        if (n % 3 == 0 || n % 5 == 0) total += n;
    return total;
}""",
        """public class Program {
  public static int ThreeFiveMultiples(int start, int limit) {
    int total = 0;
    for (int n = start; n <= limit; n++)
      if (n % 3 == 0 || n % 5 == 0) total += n;
    return total;
  }
}""",
        """public class Solution {
  public static int threeFiveMultiples(int start, int limit) {
    int total = 0;
    for (int n = start; n <= limit; n++)
      if (n % 3 == 0 || n % 5 == 0) total += n;
    return total;
  }
}""")),

    q("letter-count", "Letter Count", MEDIUM, [SM, SEARCH], "LetterCount",
      "Have the function LetterCount(arr, n) take the array of strings stored in arr and return the "
      "number of strings that contain exactly n characters.",      (["arr", "n"], ["array", INT]),
      [c([["Hello", "hillo", "x", "bun"], 3], "1", STR),
       c([["hello", "hi", "bun"], 2], "1", STR),
       c([["a", "bb", "ccc"], 1], "1", STR)],
      S("""def LetterCount(arr, n):
    return str(sum(1 for s in arr if len(s) == n))""",
        """#include <vector>
#include <string>
using namespace std;
string LetterCount(vector<string> arr, int n) {
    int count = 0;
    for (auto& s : arr) if ((int)s.size() == n) count++;
    return to_string(count);
}""",
        """public class Program {
  public static string LetterCount(string[] arr, int n) {
    return arr.Count(s => s.Length == n).ToString();
  }
}""",
        """public class Solution {
  public static String letterCount(String[] arr, int n) {
    int count = 0;
    for (String s : arr) if (s.length() == n) count++;
    return String.valueOf(count);
  }
}""")),

    q("counting-minutes", "Counting Minutes", MEDIUM, [MATH, ALGO], "CountingMinutes",
      "Have the function CountingMinutes(array) take the array of time strings stored in array and "
      "return the minutes between each consecutive pair.",
      (["array"], ["array"]),
      [c([["10:00", "10:15", "10:30", "10:45"]], [15, 15, 15], "array"),
       c([["09:00", "09:20", "11:00"]], [20, 100], "array")],
      S("""def CountingMinutes(a):
    to_min = lambda t: int(t[:2]) * 60 + int(t[3:])
    return [to_min(a[i+1]) - to_min(a[i]) for i in range(len(a)-1)]""",
        """#include <vector>
#include <string>
using namespace std;
static int to_min(const string& t) {
    return (t[0]-'0')*600 + (t[1]-'0')*60 + (t[3]-'0')*10 + (t[4]-'0');
}
vector<int> CountingMinutes(vector<string> a) {
    vector<int> out;
    for (size_t i = 0; i + 1 < a.size(); i++)
        out.push_back(to_min(a[i+1]) - to_min(a[i]));
    return out;
}""",
        """public class Program {
  public static int[] CountingMinutes(string[] a) {
    int Min(string t) => int.Parse(t.Substring(0,2)) * 60 + int.Parse(t.Substring(3,2));
    var outv = new System.Collections.Generic.List<int>();
    for (int i = 0; i + 1 < a.Length; i++) outv.Add(Min(a[i+1]) - Min(a[i]));
    return outv.ToArray();
  }
}""",
        """public class Solution {
  static int toMin(String t) {
    return Integer.parseInt(t.substring(0,2)) * 60 + Integer.parseInt(t.substring(3,5));
  }
  public static int[] countingMinutes(String[] a) {
    int[] out = new int[Math.max(0, a.length - 1)];
    for (int i = 0; i + 1 < a.length; i++) out[i] = toMin(a[i+1]) - toMin(a[i]);
    return out;
  }
}"""),
),
]


def slugify(title):
    keep = "".join(ch.lower() if ch.isalnum() else "-" for ch in title)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main() -> int:
    with open(CORE) as fh:
        existing = json.load(fh)["questions"]

    by_id = {question["id"]: question for question in existing}
    for question in QUESTIONS:
        by_id[question["id"]] = question

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from rust_solutions import attach

    attach(list(by_id.values()))

    order = {EASY: 0, MEDIUM: 1, "hard": 2}
    merged = sorted(
        by_id.values(),
        key=lambda question: (order.get(question["tier"], 3), question["title"].lower()),
    )

    # The patterns are assigned centrally, here and in the other two builders,
    # so the catalogue is correct whichever of them ran last.
    from patterns import apply as apply_patterns
    from retier import retier as retier_question

    apply_patterns(merged)

    # Tiering runs here too. It used to be a separate step that the build
    # instructions forgot, so building the catalogue silently reverted every
    # Grind 75 question to the old "stretch" tier and 68 questions fell out of
    # the sidebar. It is idempotent, which is what makes this safe to repeat.
    for question in merged:
        retier_question(question)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump({"questions": merged}, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    easy = sum(1 for question in merged if question["tier"] == EASY)
    medium = sum(1 for question in merged if question["tier"] == MEDIUM)
    print(f"wrote {len(merged)} questions  ({easy} easy, {medium} medium)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
