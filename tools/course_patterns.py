#!/usr/bin/env python3
"""The pattern half of the course, modules 2 to 13.

Kept in its own file because it is the part of the course that earns the
reading time, and because it should not be disturbed by edits to the primer or
to the assembly in build_course.py.

Each module takes one technique and says three things about it: when it
applies, why it works, and where it breaks. Every principle carries a `uses`
list naming the questions in the catalogue that use the thing it teaches, and
build_course.py refuses to write a link to a question that is not there. That
list is the point of the half. A technique you have read about and a technique
you have used on four questions are different things, and only the second one
arrives at an interview.

The material is written from two public study guides, neither of them copied:
grind75bot.com/theory for the per-technique shape, and the Tech Interview
Handbook study cheatsheet for the topic ordering and the general advice about
clarifying assumptions and validating input.
"""

from __future__ import annotations

PATTERNS: list[dict] = [
    {
        "id": "m10-searching-sorted",
        "title": "10. Searching a Sorted Sequence",
        "subtitle": "Half the array, over and over, until one element is left.",
        "minutes": 22,
        "drills": ["g-binary-search", "g-search-rotated", "g-first-bad-version",
                   "search-insert-position"],
        "principles": [
            {
                "heading": "Binary search is an interval, not a loop",
                "body": (
                    "The mistake that costs the most time is trying to memorise a "
                    "template and then adapt it. Write down what your two variables "
                    "mean first, and let the loop follow from that.\n\n"
                    "The whole algorithm is one claim: inside the interval you are "
                    "holding, the answer is either at one end or the interval is "
                    "half correct. Everything else is bookkeeping.\n\n"
                    "Here is the version where left and right both point at real "
                    "elements, so the loop condition is unambiguous:\n\n"
                    "  left = 0; right = n - 1\n"
                    "  while left <= right:\n"
                    "      mid = left + (right - left) / 2\n"
                    "      if a[mid] == target: return mid\n"
                    "      if a[mid] < target: left = mid + 1\n"
                    "      else: right = mid - 1\n\n"
                    "The alternative convention, where right is one past the end, "
                    "runs while left < right and computes mid as left + (right - "
                    "left) / 2. That version never computes left + right, which is "
                    "the overflow trap in C++ and Java. Pick one convention and "
                    "write it the same way every time. Mixing them is how you get "
                    "an infinite loop that passes four cases out of five."
                ),
                "check": "Can you say what left and right mean, in one sentence, "
                         "without looking at the code?",
                "uses": ["g-binary-search", "search-insert-position", "g-first-bad-version"],
            },
            {
                "heading": "Off by one, by construction",
                "body": (
                    "The off-by-one error is not a carelessness problem. It comes "
                    "from a loop whose bounds you chose without deciding who owns "
                    "the boundary case.\n\n"
                    "Write the loop with the condition already implying the answer. "
                    "A search that returns left when the loop ends is a search that "
                    "never evaluates the element at left, so the answer it hands "
                    "back is a position rather than a hit. If you want first index "
                    "at or after the target, that is a different loop with a "
                    "different return, and it is worth writing separately rather "
                    "than flag-switching one function.\n\n"
                    "The test that catches it: run the smallest input the prompt "
                    "allows. A single element that is the target, and a single "
                    "element that is not, exercise both sides of the boundary."
                ),
                "check": "Does your loop have a case where it never looks at the "
                         "element it returns?",
                "uses": ["g-binary-search", "g-first-bad-version"],
            },
            {
                "heading": "Monotonicity, not sorting",
                "body": (
                    "Binary search needs a claim that survives every halving. In a "
                    "plain sorted array that is the ordering. In a rotated array the "
                    "ordering is broken, so the claim has to be about one half at a "
                    "time.\n\n"
                    "The move that makes it fall out: at every step, at least one of "
                    "the two halves around mid is still sorted. Decide whether the "
                    "target sits in the sorted half, and if it does, check which end "
                    "of that half the target would be in.\n\n"
                    "The same shape handles a sorted array of booleans, which is what "
                    "first bad version is: the predicate is monotonic even though the "
                    "values are not. Search for the first position where the "
                    "predicate flips rather than for the value itself, and the "
                    "problem stops being about versions and starts being about "
                    "binary search."
                ),
                "check": "For a rotated array, which half is sorted, and how do you "
                         "know at the moment you look?",
                "uses": ["g-search-rotated", "g-first-bad-version"],
            },
        ],
    },
    {
        "id": "m11-two-pointers",
        "title": "11. Two Pointers",
        "subtitle": "Two indices walking one sequence, replacing a nested loop.",
        "minutes": 20,
        "drills": ["g-valid-palindrome", "g-three-sum", "lc-container-water",
                   "contains-duplicate"],
        "principles": [
            {
                "heading": "Decide which way each finger points",
                "body": (
                    "Two pointers is one technique with three arrangements, and the "
                    "arrangement is chosen by what the problem asks for.\n\n"
                    "Converging: the answer involves both ends and the window between "
                    "them narrows, so one index goes up while the other goes down. "
                    "Valid Palindrome and 3Sum are this shape.\n\n"
                    "Bounded: you want the widest gap that still satisfies something, "
                    "so one index holds a limit and the other probes toward it. "
                    "Container With Most Water works this way, and the reasoning is "
                    "worth internalising because it generalises: if the shorter wall "
                    "cannot be improved by moving the taller one, discard the taller "
                    "one and record the width you just measured.\n\n"
                    "Chasing: one index runs forward over a sorted list looking for a "
                    "second, slower pointer that has to stay ahead of it. Merging two "
                    "sorted lists is the plain case."
                ),
                "check": "For each pointer, can you name what it represents and which "
                         "direction it is allowed to move?",
                "uses": ["g-valid-palindrome", "g-three-sum", "lc-container-water"],
            },
            {
                "heading": "The nested loop you are removing",
                "body": (
                    "Before reaching for two pointers, notice the shape you are "
                    "replacing. A double loop over a sequence is usually asking a "
                    "membership question, and membership questions are answered by a "
                    "set or a map in one pass.\n\n"
                    "So there are three tools for the same problem, and picking the "
                    "wrong one is the usual reason a solution times out. A hash set "
                    "if order does not matter and you only need to know that something "
                    "was there. Sorting first if you need the order but not the "
                    "original positions. Two pointers if the sequence is already "
                    "sorted and the answer is about the relationship between two "
                    "positions.\n\n"
                    "Valid Anagram is the middle case. The answer is about a "
                    "collection, so counting works; sorting also works and is easier "
                    "to prove right, at the cost of the sort."
                ),
                "check": "Would a set answer this more simply, and does the problem "
                         "forbid it?",
                "uses": ["g-valid-palindrome", "g-three-sum"],
            },
            {
                "heading": "Order is information you have to keep",
                "body": (
                    "A map throws away position, and usually that is fine. Sometimes "
                    "it is the whole problem.\n\n"
                    "When the answer depends on where something was found rather than "
                    "that it was found, you have to carry the index with the value. "
                    "Two Sum is the small version: remembering the index of the "
                    "number you saw is what turns a membership question into an "
                    "answer about positions.\n\n"
                    "Product Except Self is the same idea without a second pass. A "
                    "running product from the left, a running product from the right, "
                    "and the answer at each position is the product of the two, which "
                    "leaves the division out entirely. The prefix-product version is "
                    "the easier one to get right under time pressure; the division "
                    "version is shorter and needs the zero case handled."
                ),
                "check": "If the question asked where rather than whether, is your "
                         "data structure still holding the answer?",
                "uses": ["two-sum", "g-product-except-self"],
            },
        ],
    },
    {
        "id": "m12-sliding-window",
        "title": "12. Sliding Window",
        "subtitle": "A range with two forward-only ends, and a running answer.",
        "minutes": 18,
        "drills": ["g-longest-unique-substring", "g-min-window-substring",
                   "g-find-anagrams", "g-longest-palindromic-substring"],
        "principles": [
            {
                "heading": "Shrink the window until it is valid again",
                "body": (
                    "A sliding window is a nested loop with the inner one forbidden "
                    "from going backwards. That single constraint is what turns "
                    "checking every subarray into a linear pass.\n\n"
                    "The pattern has three parts, and keeping them in this order is "
                    "what makes it work. Expand the right edge until the window "
                    "violates whatever the problem forbids. Then move the left edge "
                    "forward until it satisfies the condition again. Record the "
                    "answer at the first moment it is valid, because every later "
                    "window with the same right edge is the same length or shorter.\n\n"
                    "The question that decides whether you can use it at all: does "
                    "adding an element ever make a previously invalid window valid? "
                    "For a no-duplicates window, once a character repeats, no amount "
                    "of extending right fixes it. That is the property the technique "
                    "rests on."
                ),
                "check": "Does the window only ever move forward? If the left edge "
                         "can go back, you want a different technique.",
                "uses": ["g-longest-unique-substring", "g-min-window-substring"],
            },
            {
                "heading": "A fixed-size window is the easy case",
                "body": (
                    "Not every sliding window needs two moving ends. When the length "
                    "is fixed, both ends advance together and there is no shrink step "
                    "at all.\n\n"
                    "Find All Anagrams in a String is this. Every window of length n "
                    "slides one position at a time, and you compare it against the "
                    "target. The comparison is where the care goes: two character "
                    "counts are equal, or a sorted copy of each is equal.\n\n"
                    "The rolling count is better than sorting. Keep a count for the "
                    "window and a count for the target, and on each slide decrement "
                    "what left and increment what entered. Count how many characters "
                    "are still matching, and when that reaches zero the window is an "
                    "anagram. The whole pass is linear and uses constant extra space, "
                    "which is what the harder version of the question asks for."
                ),
                "check": "For a fixed-length window, what is the invariant that says "
                         "the current window is an anagram?",
                "uses": ["g-find-anagrams"],
            },
            {
                "heading": "Palindromes, from the middle out",
                "body": (
                    "The longest palindromic substring is a window that grows rather "
                    "than one that slides, and it is worth doing alongside the "
                    "sliding-window questions because it is the same instinct pointed "
                    "the other way.\n\n"
                    "Every odd palindrome has a centre, and every even palindrome "
                    "sits between two. So for each index, expand outward while the "
                    "characters match, and keep the longest you have found. That is "
                    "O(n squared) in the worst case, which is the honest answer for "
                    "the constraint the prompt gives.\n\n"
                    "The linear version, Manacher's algorithm, exists, and it is one "
                    "of the few places where knowing it is worth more than deriving "
                    "it. A palindrome radius table lets each expansion reuse the last "
                    "one, because the mirror of a known palindrome is a known "
                    "palindrome. Do the simple version first; come back to this when "
                    "the constraints get large enough to force your hand."
                ),
                "check": "For a palindrome, what is the one quantity that decides "
                         "whether to keep expanding?",
                "uses": ["g-longest-palindromic-substring", "g-longest-palindrome",
                         "g-valid-palindrome"],
            },
        ],
    },
    {
        "id": "m13-hash-structures",
        "title": "13. Hash Maps and Sets",
        "subtitle": "Pay memory to buy time, and be deliberate about the key.",
        "minutes": 20,
        "drills": ["g-ransom-note", "g-accounts-merge", "g-majority-element",
                   "single-number"],
        "principles": [
            {
                "heading": "The key is the whole design",
                "body": (
                    "A hash map is fast because it hands you a value from a key in "
                    "constant time. Every question using one is really a question "
                    "about what the key should be, and getting that wrong is why the "
                    "answer comes back empty.\n\n"
                    "Three keys cover most of what you will meet. The element itself, "
                    "when the value is a count or a position. A tuple of two elements, "
                    "when the key is a pair such as a coordinate or an edge. A "
                    "frequency signature, when you want to compare collections "
                    "without sorting them, which is what Find All Anagrams does and "
                    "what Accounts Merge does for a group of addresses.\n\n"
                    "The signature version is worth practising because it generalises: "
                    "if two collections should be considered equal, sort them or count "
                    "them into a fixed shape, and compare the shapes."
                ),
                "check": "Say your key out loud. Would two different inputs that you "
                         "want treated as the same produce it?",
                "uses": ["g-find-anagrams", "g-accounts-merge", "g-ransom-note"],
            },
            {
                "heading": "Counting beats comparing",
                "body": (
                    "When the question is whether two things match, counting into a "
                    "map is usually shorter than any comparison loop, and it runs in "
                    "one pass over each.\n\n"
                    "The pattern is always the same. Count one side up. Walk the other "
                    "side, decrementing as you go. If any decrement goes below zero, "
                    "you can stop immediately, because the counts never recover. That "
                    "early exit is what makes Ransom Note fast, and it is easy to "
                    "leave out.\n\n"
                    "Two details that cause wrong answers more often than the logic "
                    "does. Leaving a leftover count means one string had characters "
                    "the other did not, which is a mismatch even when nothing went "
                    "negative. And the character set matters: an array of 26 works "
                    "for lowercase letters and silently fails on anything else."
                ),
                "check": "After your loop, is a leftover count possible, and does that "
                         "count as a failure?",
                "uses": ["g-ransom-note", "valid-anagram", "g-find-anagrams"],
            },
            {
                "heading": "In a group, the element is special",
                "body": (
                    "Some questions do not need a map. They need the observation that "
                    "a majority element appears more than half the time, which "
                    "means the answer exists wherever you happen to look.\n\n"
                    "So count as you go and reset whenever the count hits zero. The "
                    "element standing at the end is the majority, and it did not "
                    "matter which elements you discarded in pairs because each discard "
                    "removed one of the majority and one of something else.\n\n"
                    "Single Number is the same idea with bitwise operators and no "
                    "counting. XOR is its own inverse, so every pair of equal values "
                    "cancels and only the unpaired one is left. Hamming Distance is "
                    "the same operation, counted rather than collapsed, which is a "
                    "good reminder that one operator often serves both."
                ),
                "check": "Does discarding in pairs preserve the property you are "
                         "trying to find?",
                "uses": ["g-majority-element", "single-number", "hamming-distance"],
            },
        ],
    },
    {
        "id": "m14-stacks",
        "title": "14. Stacks",
        "subtitle": "Last in, first out, which is what nesting and matching want.",
        "minutes": 17,
        "drills": ["g-valid-parentheses", "bracket-matcher", "g-evaluate-rpn",
                   "g-largest-rectangle"],
        "principles": [
            {
                "heading": "A stack is the right answer when things nest",
                "body": (
                    "The test for reaching for a stack is whether the order of "
                    "opening and closing has to match. Brackets, tags, and "
                    "expressions all share that shape, and a stack handles them "
                    "without any bookkeeping about positions.\n\n"
                    "Push on open, pop on close, and at the end the stack must be "
                    "empty. The two failure modes are worth naming because they feel "
                    "identical: popping from an empty stack, which means a closer "
                    "arrived with nothing open, and finishing with something left on "
                    "the stack, which means an opener never closed. Both are wrong, "
                    "and a solution that checks only one will pass on inputs that "
                    "happen to be balanced.\n\n"
                    "When the brackets come with several kinds, a plain stack of "
                    "characters still works. Compare against the expected closer "
                    "rather than matching kinds to kinds."
                ),
                "check": "What is on your stack at the moment the input ends, and what "
                         "does that tell you?",
                "uses": ["g-valid-parentheses", "bracket-matcher"],
            },
            {
                "heading": "A stack evaluates postfix for free",
                "body": (
                    "Reverse Polish notation looks like it needs a parser. It does "
                    "not, because the postfix ordering already encodes the grouping: "
                    "an operator arrives after both of its operands, which is exactly "
                    "when a stack is ready to combine them.\n\n"
                    "Push every number. On an operator, pop twice, apply, and push "
                    "the result. At the end the one thing left is the answer. There "
                    "is no precedence table and no parenthesis handling, which is the "
                    "part people expect and do not need.\n\n"
                    "Division needs one extra thought. Integer division truncates "
                    "toward zero, and because the divisor is the second pop, pushing "
                    "in the order the tokens appear matters. Basic Calculator on a "
                    "real infix string is a different problem and genuinely does "
                    "need more than this."
                ),
                "check": "When you pop two values, which one is the left operand?",
                "uses": ["g-evaluate-rpn", "g-basic-calculator"],
            },
            {
                "heading": "A stack that refuses to go down",
                "body": (
                    "Sometimes the useful stack is one where you never pop a smaller "
                    "value than the one below it. Popping while the top is smaller "
                    "than the current element is a monotonic stack, and it finds the "
                    "answer in one pass where a nested loop would take quadratic "
                    "time.\n\n"
                    "The reasoning: once you have seen a bar, any shorter bar to its "
                    "right can never be limited by it, so its height is settled and "
                    "you can retire it. The stack holds the bars whose limits are "
                    "still open, in decreasing order, and the top is always the next "
                    "one to settle.\n\n"
                    "When a bar is popped, the new top is the nearest bar to the left "
                    "that is shorter than it, which is the left edge of the widest "
                    "rectangle that bar can serve. The current index is the right "
                    "edge. The width is the distance between the two edges, minus "
                    "one. That is the whole algorithm, and it is a good exercise "
                    "because the invariant is the entire difficulty."
                ),
                "check": "When you pop an element, what do the new top and the current "
                         "index each represent?",
                "uses": ["g-largest-rectangle"],
            },
        ],
    },
    {
        "id": "m15-linked-lists",
        "title": "15. Linked Lists",
        "subtitle": "Nodes point forward. Every operation is a rewire.",
        "minutes": 16,
        "drills": ["g-merge-two-sorted-lists", "g-reverse-linked-list",
                   "g-middle-linked-list", "g-add-binary"],
        "principles": [
            {
                "heading": "Draw the pointers before you move them",
                "body": (
                    "A linked list has no indexing, so every question about one is a "
                    "question about which node holds which pointer. Write the two or "
                    "three rewires as a diagram, then translate.\n\n"
                    "Reversing is the clearest case. One node is detached at a time: "
                    "save its next, point it back, and advance. Three lines, and the "
                    "reason it is hard is that all three must happen before any of "
                    "them can be re-read. That dependency is invisible in a one-line "
                    "description.\n\n"
                    "The harness here hands you a list as an array with optional "
                    "holes, and returns one the same way, so a null terminates a "
                    "list and a gap does not occur. Where the real interview uses a "
                    "node class, the pointer work is identical; only the syntax is "
                    "different."
                ),
                "check": "Have you saved every pointer you are about to overwrite, "
                         "before overwriting any of them?",
                "uses": ["g-reverse-linked-list", "g-merge-two-sorted-lists"],
            },
            {
                "heading": "The slow and fast pointers",
                "body": (
                    "One pointer cannot ask a question about the whole list, because "
                    "reaching the end loses whatever the pointer held. Two pointers "
                    "at different speeds can.\n\n"
                    "Run one at twice the speed. If there is a cycle, the fast pointer "
                    "catches the slow one; if there is not, the fast one reaches null "
                    "and the slow one is left standing in the middle. Finding the "
                    "middle is therefore the same code as detecting a cycle, and "
                    "Middle of the Linked List is the easy half of that.\n\n"
                    "The same trick finds the kth node from the end, with no list "
                    "length and no recursion: start one pointer k nodes ahead, then "
                    "walk both until the ahead one falls off the end."
                ),
                "check": "If the fast pointer reaches the end first, where is the slow "
                         "one, and why?",
                "uses": ["g-middle-linked-list", "g-merge-two-sorted-lists"],
            },
            {
                "heading": "Merging needs one decision, made once per element",
                "body": (
                    "A merge is the textbook two-pointer chase. At every step you "
                    "have two candidates and you take the smaller, then advance only "
                    "that one list.\n\n"
                    "The bookkeeping that goes wrong is losing track of which list "
                    "produced the value you just appended. Attach the node from the "
                    "list you advanced, not the other one. Ties go to either list, "
                    "so pick one and be consistent; that is exactly the kind of "
                    "unstated convention a prompt's examples settle for you.\n\n"
                    "Merging k lists is the same idea with a heap, because picking "
                    "the smallest of k heads by hand is k comparisons per element. A "
                    "priority queue of the heads brings that down to log k, and the "
                    "result is that the code looks nothing like the two-list version "
                    "while doing the same work."
                ),
                "check": "After appending a node, can you still tell which list it "
                         "came from?",
                "uses": ["g-merge-two-sorted-lists", "g-merge-k-sorted"],
            },
        ],
    },
    {
        "id": "m16-trees",
        "title": "16. Trees",
        "subtitle": "Recurse to the bottom, then let the return value travel up.",
        "minutes": 26,
        "drills": ["g-invert-binary-tree", "g-maximum-depth-binary-tree",
                   "g-balanced-binary-tree", "g-lca-binary-tree", "g-kth-smallest"],
        "principles": [
            {
                "heading": "Most tree questions have one shape",
                "body": (
                    "For a tree, either the answer is about a node and its children "
                    "locally, in which case recurse and combine, or it is about the "
                    "whole shape, in which case recurse and keep a running value.\n\n"
                    "Invert a Binary Tree is the pure form: swap the children, return "
                    "the node, ask the children to do the same. Maximum Depth adds a "
                    "little: the depth is one more than the deeper side, so the "
                    "return value has to carry something up. Balanced Binary Tree "
                    "compares the two returned depths.\n\n"
                    "The three questions that catch people are all about the return "
                    "value rather than the traversal. A function that returns nothing "
                    "cannot tell its parent anything, so it has to return the node, "
                    "the subtree, or a number. Decide which before you write the "
                    "first line."
                ),
                "check": "What does your recursive call have to return for its parent "
                         "to do anything with it?",
                "uses": ["g-invert-binary-tree", "g-maximum-depth-binary-tree",
                         "g-balanced-binary-tree", "g-diameter-binary-tree"],
            },
            {
                "heading": "A running answer beats a returned one",
                "body": (
                    "When the question is about the largest, smallest, or most "
                    "extreme thing anywhere in the tree, the answer does not live at "
                    "any single node, so returning a value upward does not help.\n\n"
                    "Keep it outside the recursion instead. Visit every node, compare "
                    "it against the running best, and update. This is the difference "
                    "between a function that can answer Diameter of a Binary Tree and "
                    "one that cannot, and it is the same pattern as the running "
                    "product in Product Except Self.\n\n"
                    "The related choice is how to carry the running value. An "
                    "attribute on the object works in languages that have objects, "
                    "and in a function-per-question harness it is usually a list or a "
                    "dictionary you pass in, or a value returned as a pair. In Rust "
                    "the borrow checker will push you toward the second, which is a "
                    "good outcome."
                ),
                "check": "Does the answer live at a node, or across the whole tree? "
                         "That decides whether you return or accumulate.",
                "uses": ["g-diameter-binary-tree", "g-kth-smallest",
                         "g-right-side-view"],
            },
            {
                "heading": "The BST order is a promise about the whole subtree",
                "body": (
                    "A binary search tree constrains more than the edges. Everything "
                    "in a left subtree is smaller than the node, and everything in a "
                    "right subtree is larger, so a bound travels down with the "
                    "recursion.\n\n"
                    "That is why Validate Binary Tree passes a range down rather than "
                    "comparing each node to its parent. Comparing to the parent "
                    "accepts a tree where a node is in the right subtree of its parent "
                    "but smaller than an ancestor further up, which is not a search "
                    "tree at all. It is the single most common tree bug.\n\n"
                    "The same bound makes two questions easy. Finding the kth smallest "
                    "is a ranked traversal: go left for a smaller rank, go right for a "
                    "smaller one than you were asked for. Finding the lowest common "
                    "ancestor is three cases: the node is an ancestor of itself, one "
                    "answer came from the left branch and the other from the right, or "
                    "both came from the same side and you keep descending."
                ),
                "check": "Does your bound come from the root, or only from the parent?",
                "uses": ["g-validate-bst", "g-lca-bst", "g-kth-smallest",
                         "g-lca-binary-tree"],
            },
        ],
    },
    {
        "id": "m17-graph-traversal",
        "title": "17. Graphs and Traversal",
        "subtitle": "Depth-first for structure, breadth-first for distance.",
        "minutes": 24,
        "drills": ["g-number-of-islands", "g-course-schedule", "g-ladder-length",
                   "g-flood-fill"],
        "principles": [
            {
                "heading": "Mark on the way in, not on the way out",
                "body": (
                    "The line between a working traversal and an infinite one is a "
                    "single line placed at the right moment. Mark a node visited when "
                    "you first reach it, before you recurse into its neighbours.\n\n"
                    "Marking on the way out looks equivalent and is not, because a "
                    "node with two neighbours in the same region gets visited twice "
                    "before the first visit finishes. Cycles make it worse. Number of "
                    "Islands and Flood Fill both need the mark, and both fail in the "
                    "same way when it is misplaced.\n\n"
                    "For a grid, the visited set and the recursion are the same thing: "
                    "flip the cell as you enter it, and the question of whether you "
                    "have been there is answered by the grid itself. That trick keeps "
                    "the extra space constant, which is the constraint that matters in "
                    "the harder versions."
                ),
                "check": "Is there a moment where you are visiting a node twice before "
                         "anything has marked it?",
                "uses": ["g-number-of-islands", "g-flood-fill", "g-word-search"],
            },
            {
                "heading": "Breadth-first is the one that counts distance",
                "body": (
                    "Depth-first follows one path as far as it goes. Breadth-first "
                    "visits everything one step away, then everything two steps away, "
                    "so the first time it reaches a node is by the shortest path.\n\n"
                    "That is the whole reason to choose it. Any question whose answer "
                    "involves how many moves, how many edges, or how many layers turns "
                    "into a breadth-first search, and the answer is the distance "
                    "recorded when you first reach the target. Rotting Oranges is this "
                    "with a time attached to each wave.\n\n"
                    "The implementation is a queue, and the one thing to get right is "
                    "fixing the size of the current level before you start adding the "
                    "next one. If you let the queue grow while you iterate over it, "
                    "the level boundaries are lost and every distance comes out as "
                    "one."
                ),
                "check": "What is the size of the current level, and when did you "
                         "record it?",
                "uses": ["g-rotting-oranges", "g-level-order-traversal",
                         "g-min-height-trees", "g-zero-one-matrix"],
            },
            {
                "heading": "A cycle and a prerequisite problem are the same question",
                "body": (
                    "Course Schedule looks like a scheduling problem and is a graph "
                    "problem. Each course is a node, each prerequisite is an edge, and "
                    "the question is whether a course can ever be taken, which is "
                    "whether the graph has a cycle in it.\n\n"
                    "So run a traversal and count the nodes you finish. A depth-first "
                    "search that returns early on a node it is already inside has "
                    "found a cycle. Be careful to clean up the in-progress state when "
                    "a node finishes, or every node after the first back edge looks "
                    "like a cycle and the answer is always no.\n\n"
                    "The other way to ask it is a topological order. Repeatedly take "
                    "a node with no unsatisfied prerequisites, remove it, and repeat. "
                    "If you take all of them, there was no cycle. That framing is "
                    "easier to get right and slower to write."
                ),
                "check": "When a node finishes, did you clear its in-progress state?",
                "uses": ["g-course-schedule", "g-ladder-length"],
            },
        ],
    },
    {
        "id": "m18-backtracking",
        "title": "18. Backtracking and Recursion",
        "subtitle": "Build a candidate, abandon it the moment it cannot work.",
        "minutes": 22,
        "drills": ["g-permutations", "g-subsets", "g-combination-sum",
                   "g-letter-combinations"],
        "principles": [
            {
                "heading": "A recursion that is allowed to fail",
                "body": (
                    "Ordinary recursion explores a fixed answer. Backtracking "
                    "explores a space of candidates, and every branch may turn out to "
                    "be a dead end, which is the normal case rather than an "
                    "exception.\n\n"
                    "The shape is always the same four steps. Choose the next element. "
                    "Test whether the partial answer can still work, and return "
                    "immediately if it cannot. Recurse. Then undo the choice before "
                    "trying the next one, because the state you changed is shared "
                    "with every branch that comes after.\n\n"
                    "The undo is the part that is easy to leave out and impossible to "
                    "notice, since a missing undo often still produces the right "
                    "answer for the first case and wrong ones for the rest. If your "
                    "output is subtly missing elements, this is why."
                ),
                "check": "Does every branch restore the state it changed?",
                "uses": ["g-permutations", "g-subsets", "g-letter-combinations"],
            },
            {
                "heading": "Decide what makes two answers the same",
                "body": (
                    "Permutations, combinations and subsets differ only in what they "
                    "forbid, and the forbidding is one line each.\n\n"
                    "A permutation uses every element exactly once, so recurse over "
                    "the elements not yet used and track that with a used array. A "
                    "combination uses each at most once, in order, so the candidates "
                    "available at each step are only those after the last one you "
                    "picked. A subset is a combination of every length including zero, "
                    "so it is the same loop with a record at every depth rather than "
                    "only at the end.\n\n"
                    "Combination Sum adds a limit, because you may reuse a value until "
                    "the sum stops being small enough. So the same index recurses "
                    "rather than moving on. Getting the reuse rule right is the "
                    "entire difference between that and a plain combination sum."
                ),
                "check": "What is the one rule that keeps this answer from being a "
                         "duplicate of another?",
                "uses": ["g-permutations", "g-subsets", "g-combination-sum",
                         "g-letter-combinations"],
            },
            {
                "heading": "A search on a grid is recursion with a budget",
                "body": (
                    "Word Search looks like a string problem and is a graph search "
                    "with a rule. Each starting cell is a candidate, and from there "
                    "you recurse to the four neighbours, using the next character of "
                    "the word each time.\n\n"
                    "Two things make it work. The cell you move into is blanked before "
                    "you recurse and restored after, which stops the search reusing a "
                    "letter, and a match of the last character returns immediately "
                    "rather than recursing into an empty word. Without the restore "
                    "the same cell stays blanked and later searches from the same row "
                    "fail.\n\n"
                    "The complexity is four to the power of the word length times the "
                    "grid size, which is fine for the constraint the prompt gives and "
                    "a reason to prune in a harder version. Pruning means refusing to "
                    "start a position that cannot work, by checking the first "
                    "character before recursing at all."
                ),
                "check": "Do you restore the cell after a failed branch?",
                "uses": ["g-word-search", "g-permutations", "g-combination-sum"],
            },
        ],
    },
    {
        "id": "m19-dynamic-programming",
        "title": "19. Dynamic Programming",
        "subtitle": "Find the recurrence, then stop computing it twice.",
        "minutes": 24,
        "drills": ["g-climbing-stairs", "g-coin-change", "g-unique-paths",
                   "g-word-break"],
        "principles": [
            {
                "heading": "Name the state before writing the code",
                "body": (
                    "The hard part of dynamic programming is the sentence you have "
                    "to finish: the answer to this subproblem is a function of "
                    "these things. Once that sentence is written, the code follows.\n\n"
                    "Climbing Stairs is the smallest honest example. The answer for "
                    "n stairs is the answer for n-1 plus the answer for n-2, because "
                    "the last move was either one step or two. Written that way, the "
                    "recursion is obvious and the problem is only about not calling "
                    "it a hundred times.\n\n"
                    "The failure mode is picking a state that is too coarse. If your "
                    "state is just the position, you will find yourself needing to "
                    "know something about how you got there, and the fix is to widen "
                    "the state until it is enough. Widening is the skill; the "
                    "looping after that is bookkeeping."
                ),
                "check": "Finish this sentence: the answer for this subproblem is a "
                         "function of exactly these things, because.",
                "uses": ["g-climbing-stairs", "g-unique-paths", "g-longest-palindrome",
                         "lc-decode-ways"],
            },
            {
                "heading": "Top-down or bottom-up, and why you would pick",
                "body": (
                    "Both fill the same table. Top-down starts from the real input "
                    "and recurses, memoising what it has computed. Bottom-up builds "
                    "the table in order and reads off the answer.\n\n"
                    "Bottom-up wins when you know the states in advance, because it "
                    "does no redundant work and the loop order makes the dependencies "
                    "obvious. Top-down wins when most states are unreachable, because "
                    "it never visits them, and it is easier to write when the "
                    "recurrence is awkward to sequence.\n\n"
                    "Coin Change is bottom-up and almost mandatory, because the "
                    "amount runs upward and the subproblems are smaller amounts. Word "
                    "Break reads well top-down over positions, with a question at each "
                    "position of whether the prefix before it can be broken. Both are "
                    "fine. Pick based on the shape, not on habit."
                ),
                "check": "Can you write the loop order that guarantees every "
                         "dependency is already filled in?",
                "uses": ["g-coin-change", "g-word-break", "g-climbing-stairs"],
            },
            {
                "heading": "An unreachable state is a real answer",
                "body": (
                    "Recurrences for money and reachability have states that cannot "
                    "happen. Treating those as zero is the whole question.\n\n"
                    "For Coin Change, ask what it means for the amount to be "
                    "unreachable, and use a sentinel larger than any legitimate "
                    "amount rather than a negative number that arithmetic will walk "
                    "back into range. Then the final answer has to be a comparison "
                    "against that sentinel, because returning a large number for an "
                    "unreachable amount is not the number the prompt asked for.\n\n"
                    "Unique Paths is a grid version of the same thing, where the "
                    "boundaries are the states you cannot arrive at. Filling them "
                    "with one rather than zero is what stops the answer coming out "
                    "zero for a one-by-one grid."
                ),
                "check": "Which states are impossible, and what value are you putting "
                         "in them?",
                "uses": ["g-coin-change", "g-unique-paths", "g-word-break"],
            },
        ],
    },
    {
        # Placed after DP deliberately: greedy is a commitment, and you only
        # make it once you can state the exchange argument.
        "id": "m20-heaps-greedy",
        "title": "20. Heaps and Greedy Choices",
        "subtitle": "Keep only what matters, and take the best option in front of you.",
        "minutes": 21,
        "drills": ["g-k-closest-points", "g-max-profit-jobs", "g-task-scheduler",
                   "g-sort-colors"],
        "principles": [
            {
                "heading": "Greedy is a proof, not a preference",
                "body": (
                    "A greedy solution takes the option that looks best right now and "
                    "never revisits it. That is only correct when you can say why the "
                    "choice cannot cost you anything later.\n\n"
                    "Maximum Profit in Job Scheduling is the clean case. Sort by "
                    "finish time, then for each job take it if it starts after the "
                    "last one you took. The argument is that any optimal schedule can "
                    "be rearranged to agree with this one on the earliest-finishing "
                    "job, because swapping it in frees at least as much time for "
                    "everything after. That rearrangement is the proof, and you need "
                    "it, because the intuition alone is not enough to trust.\n\n"
                    "Best Time to Buy and Sell Stock is greedy in a single pass and "
                    "needs no data structure: track the lowest price seen so far and "
                    "the best difference between it and today's price."
                ),
                "check": "Can you state the exchange argument, not just the intuition?",
                "uses": ["g-max-profit-jobs", "g-best-time-to-trade", "lc-candy",
                         "g-task-scheduler"],
            },
            {
                "heading": "A heap is a promise about which element comes next",
                "body": (
                    "You need a heap when the question is repeatedly asking for the "
                    "largest, or the smallest, or the middle, of a collection that is "
                    "still growing. Sorting does not work, because sorting gives you "
                    "an order for the collection you have rather than a way to ask "
                    "about the collection you will have.\n\n"
                    "So push each new element and pop the one you no longer need. K "
                    "Closest Points to Origin keeps every point in a heap of the size "
                    "you want, which is how it stays linear instead of sorting the "
                    "whole set. Merging k Sorted Lists keeps the current head of each "
                    "list and pops the smallest.\n\n"
                    "The distinction that catches people: a heap is a partial order, "
                    "not a sorted list. You can only ask for the extreme, never for "
                    "the second smallest. If the question needs a full order, sort."
                ),
                "check": "Do you need the extreme element, or all of them in order?",
                "uses": ["g-k-closest-points", "g-merge-k-sorted", "g-kth-smallest",
                         "g-max-profit-jobs"],
            },
            {
                "heading": "Counting beats ordering when the keys are small",
                "body": (
                    "A third option sits between sorting and a heap, and it is the "
                    "fastest one whenever it applies: count into a small array and "
                    "walk the counts.\n\n"
                    "Sort Colors is three values, so a count of each size plus two "
                    "passes places every element. That is linear, and it is stable, "
                    "which a comparison sort would not be at that cost. Task Scheduler "
                    "is the same idea where the key is a frequency: the answer is "
                    "driven by the most frequent task and the gap it needs.\n\n"
                    "The general shape is worth recognising because it comes up "
                    "constantly. Any question that says the values come from a small "
                    "range is a counting question, and a counting solution beats a "
                    "sorting one on both time and clarity."
                ),
                "check": "Are the values a small fixed range, and is a count array "
                         "smaller than the input?",
                "uses": ["g-sort-colors", "g-task-scheduler", "g-merge-intervals",
                         "g-insert-interval"],
            },
        ],
    },
]
