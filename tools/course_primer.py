#!/usr/bin/env python3
"""The primer: one module on reading a question, plus the recognition module.

The course used to open with nine modules of reading advice, debugging advice
and per-language trivia, 149 minutes of it. None of those nine linked to a
question, because none of them was a technique: they were things worth knowing
that do not attach to a particular problem. The other half of the course, the
pattern modules, linked to 92 questions between them, and that is the difference
that mattered.

So the advice is compressed into a single module here, cut down to the parts
that stop a correct answer from scoring zero, and the recognition module is
added at the head of the pattern half because twelve techniques with no way to
choose between them is a glossary rather than a course.

The language trivia (per-language range semantics, the lambda cheat sheet, the
string traps in each language) is not in the course at all. It is reference
material: worth having, not worth reading in order, and nobody learns a range
convention by being told to. It lives in REFERENCE.md and the primer points at
it.
"""

from __future__ import annotations

PRIMER: list[dict] = [
    {
        "id": "p1-read-the-question",
        "title": "1. Read the Question",
        "subtitle": "Six principles. Everything else in the course assumes these.",
        "minutes": 20,
        "part": "essentials",
        "partTitle": "Essentials",
        "drills": ["ab-check", "time-convert", "letter-changes", "vowel-count",
                   "counting-minutes-i", "swap-case"],
        "principles": [
            {
                "heading": "The return type is part of the question",
                "body": (
                    "Grading here compares the exact value and its type. A "
                    "logically perfect answer scores zero if the type is wrong, "
                    "and it is the most common way to fail.\n\n"
                    "Read the sentence that says what to return, and copy it "
                    "exactly:\n\n"
                    "  'return the string true'  ->  return \"true\"   (a string)\n"
                    "  'return true'            ->  return true      (a boolean)\n"
                    "  'return 1 or 0'           ->  return 1         (an int)\n\n"
                    "If the prompt puts true in quotes it is a string. If it does "
                    "not, it is probably a boolean. When the wording is ambiguous "
                    "the examples are the contract, and the examples are never "
                    "ambiguous about the type.\n\n"
                    "The same rule covers formatting. A correct number in the "
                    "wrong shape is a wrong answer: '1:30' and not '90 minutes', "
                    "'3w2g' and not 'wwwgg'."
                ),
                "check": "Does my return value have the same type and the same "
                         "shape as the examples show?",
                "uses": ["ab-check", "check-nums", "time-convert", "ex-oh",
                         "basic-roman-numerals", "dash-insert"],
            },
            {
                "heading": "The examples are the specification",
                "body": (
                    "Examples are not sample data to sanity check against. They "
                    "are where the prompt's vagueness gets resolved, and they "
                    "answer three questions the wording leaves open.\n\n"
                    "Type, as above. Format, in the sense of exactly how a value "
                    "is spelled. And boundaries: if an example includes the empty "
                    "string or a single element, that case is being tested. If no "
                    "example does, it is probably out of scope.\n\n"
                    "Constraints in the prompt are the same kind of information. "
                    "'the string will not be empty' has saved you a check. '0 "
                    "will not be entered' has told you not to guard the division. "
                    "'do not count y as a vowel' has fixed your vowel set to "
                    "aeiou. Being able to say why you are not handling a case is "
                    "a correct answer, not an omission."
                ),
                "check": "Which constraints can I rely on, and does my solution "
                         "actually rely only on those?",
                "uses": ["string-reduction", "overlapping-ranges", "changing-sequence",
                         "second-greatlow", "run-length"],
            },
            {
                "heading": "Rewrite the paragraph as a numbered list",
                "body": (
                    "Do not code from the paragraph. It mixes the rules with the "
                    "prose, and the rules are the part you need.\n\n"
                    "Letter Changes says: shift each letter, then capitalise the "
                    "vowels. Written as steps:\n\n"
                    "  1. For each character\n"
                    "  2.   if it is a letter, replace it with the next one "
                    "(z wraps to a)\n"
                    "  3.   if that NEW letter is a vowel, uppercase it\n"
                    "  4. Join the result\n\n"
                    "Now you are transcribing a list rather than solving a "
                    "paragraph. Transcription is easy, and the order of steps two "
                    "and three is the whole question, which is much harder to see "
                    "while you are reading prose."
                ),
                "check": "Do I have a numbered list before I have any code?",
                "uses": ["letter-changes", "caesar-cipher", "run-length",
                         "letter-count"],
            },
            {
                "heading": "Name the shape, then trace one by hand",
                "body": (
                    "Almost every question hands you a string, a list or a "
                    "number, and the shape decides your first move. You cannot do "
                    "arithmetic on a list, and in most languages you cannot "
                    "assign into a string.\n\n"
                    "Then trace the algorithm on paper before you write it. Two "
                    "elements is enough to surface index and wrap-around bugs. "
                    "Letter Changes on 'zebra' gives z->a, e->f, b->c, r->s, a->b, "
                    "so 'afcsb', and then the vowels of the new string are "
                    "uppercased to 'Afcsb'. Notice the vowel test happens after "
                    "the shift. A trace you have not done by hand is a guess.\n\n"
                    "While you are there, decide the empty case on purpose. "
                    "Splitting an empty string gives one empty word, not zero. "
                    "Most of the surprises in these questions are in the case "
                    "where there is nothing to iterate over."
                ),
                "check": "Can I name the input's shape in one word, and what does "
                         "my function return for empty input?",
                "uses": ["word-count", "string-reduction", "letter-changes",
                         "longest-word", "array-addition"],
            },
            {
                "heading": "One pass with a named accumulator",
                "body": (
                    "The instinct on a new question is to loop, and inside the "
                    "loop to loop again. Ask instead what you need to remember "
                    "as you go.\n\n"
                    "Counting vowels is one pass and a counter. Finding a "
                    "duplicate is one pass and a set. Summing is one pass and a "
                    "total. Almost every count, find or check question in this "
                    "catalogue is a single pass with some state carried through "
                    "it, and the nested version is usually why it times out.\n\n"
                    "Name that state. best, total, count, result, seen. When you "
                    "are stuck, pick the word the question itself uses, 'the "
                    "longest', 'how many', 'the first duplicate', and make that "
                    "the variable name. Half of these questions write themselves "
                    "once the name is right."
                ),
                "check": "Does my solution have a loop inside a loop, and could it "
                         "be one loop?",
                "uses": ["vowel-count", "letter-count-i", "longest-word",
                         "hamming-distance", "contains-duplicate"],
            },
            {
                "heading": "The three bugs that survive review",
                "body": (
                    "Most wrong answers on questions that should have worked are "
                    "one of three things.\n\n"
                    "An index off by one, which comes from a loop whose bounds you "
                    "chose without deciding who owns the boundary case. Off by one "
                    "means a legitimate case falls off the end of your loop, and "
                    "the empty input is where it shows.\n\n"
                    "State declared inside the loop, which resets every iteration "
                    "when it should carry. This is the quiet one, because the "
                    "first case passes and the second does not.\n\n"
                    "And a string you meant to modify. Strings are immutable in "
                    "all five languages here, so every edit is a rebuild. Building "
                    "in a loop without joining at the end throws away most of "
                    "what you wrote.\n\n"
                    "When an answer fails, do not rewrite it. Read the whole error "
                    "first, the first line names the language, the line number and "
                    "the kind of fault, and the answer is usually in it. Then "
                    "narrow rather than guess: halve the input, find the smallest "
                    "case that still fails, and look at that one.\n\n"
                    "The per-language details, range conventions and the rest, are "
                    "reference rather than lesson and live in REFERENCE.md."
                ),
                "check": "If my answer failed, have I read the whole error and "
                         "found the smallest input that still fails?",
                "uses": ["counting-minutes-i", "mean-mode", "swap-case",
                         "letter-capitalize", "alphabet-soup", "second-greatlow"],
            },
        ],
    },
]


RECOGNITION: list[dict] = [
    {
        "id": "m10-recognising",
        "title": "2. Recognising the Pattern",
        "subtitle": "How to look at a prompt and land on the right technique.",
        "minutes": 16,
        "part": "patterns",
        "partTitle": "Patterns",
        "drills": ["g-valid-parentheses", "g-permutations", "g-climbing-stairs",
                   "g-number-of-islands", "two-sum"],
        "principles": [
            {
                "heading": "Read the answer, not the input",
                "body": (
                    "The input usually tells you what kind of data you have. It is "
                    "the answer that tells you the technique, and the two are "
                    "routinely different.\n\n"
                    "A list of numbers looks the same whether the answer is the "
                    "pair that sums to a target, or the longest run without a "
                    "repeat, or the number of ways to reach the end. Only the "
                    "second one is a sliding window. So read the sentence that "
                    "says what to return, and ask what kind of thing that answer "
                    "is.\n\n"
                    "A window is a stretch of the input. A count is a number. A "
                    "path is a sequence of moves. An arrangement is a set of "
                    "choices. Once you can say which of those you are being asked "
                    "for, the technique is usually one or two away."
                ),
                "check": "Before choosing a technique, have I said what kind of "
                         "thing the ANSWER is?",
                "uses": ["two-sum", "g-longest-unique-substring", "g-unique-paths",
                         "g-permutations", "g-climbing-stairs"],
            },
            {
                "heading": "Three questions, in order",
                "body": (
                    "When a prompt does not announce its technique, ask these in "
                    "this order and stop at the first yes.\n\n"
                    "Does the input nest, match, or open and close? Stacks, and "
                    "Valid Parentheses, Evaluate Reverse Polish Notation and Basic "
                    "Calculator are all this.\n\n"
                    "Is the answer about how far, or how many steps? Breadth-first "
                    "traversal, and with it Rotting Oranges, Minimum Height Trees "
                    "and 01 Matrix.\n\n"
                    "Do I need to remember where I saw something, or that I saw it "
                    "at all? A hash map, and with it Two Sum, Valid Anagram, "
                    "Product Except Self and Accounts Merge.\n\n"
                    "Is the answer about a contiguous stretch of the input? A "
                    "sliding window. Is the input sorted, and am I looking for a "
                    "boundary? Binary search. If none of those fit, it is a tree, "
                    "a graph, a recursion or a table, and the shape of the input "
                    "tells you which."
                ),
                "check": "Which of the three questions did the prompt answer yes "
                         "to first?",
                "uses": ["g-valid-parentheses", "g-evaluate-rpn", "g-rotting-oranges",
                         "g-min-height-trees", "two-sum", "g-binary-search",
                         "g-invert-binary-tree", "g-course-schedule"],
            },
            {
                "heading": "Write the slow version, then find the waste",
                "body": (
                    "Very few prompts hand you the technique. More often you work "
                    "it out backwards from a version that is obviously correct and "
                    "obviously too slow.\n\n"
                    "Try every pair of elements, which is a nested loop. Then ask "
                    "which half of that work is repeated, and 3Sum becomes a sort "
                    "and a scan. Try every subset, which is exponential, and then "
                    "ask which choices you would make again, and Word Break "
                    "becomes a table. Try every path in a grid, and then ask whether "
                    "the answer to a cell is the sum of two answers you already "
                    "have.\n\n"
                    "The step you keep is a recurrence, and once you have written "
                    "it down the technique follows from the shape of it: if it "
                    "runs forwards it is a table, if it has to be undone on the "
                    "way back up it is backtracking, and if the answer is the "
                    "running best of something you have already seen it is a heap."
                ),
                "check": "Can I name the one step my brute force repeats, and why "
                         "the technique removes it?",
                "uses": ["g-three-sum", "g-word-break", "g-unique-paths",
                         "g-combination-sum", "g-k-closest-points"],
            },
            {
                "heading": "When two patterns fit, take the simpler one",
                "body": (
                    "Several techniques often solve the same question. That is "
                    "normal, and it is not a reason to pick the more impressive "
                    "one.\n\n"
                    "Longest Substring Without Repeating Characters has a "
                    "monotonic-stack solution and a sliding-window solution. The "
                    "window is shorter, uses less space, and is easier to check by "
                    "hand. Word Break has a backtracking answer and a table-driven "
                    "one, and the table is the one that finishes. 3Sum can be a "
                    "hash map per element or a sort and a scan, and the second is "
                    "both shorter and the one the constraints are written for.\n\n"
                    "Under time pressure the technique that is worth the most is "
                    "the one you can actually finish. Reach for the clever answer "
                    "when the simple one is too slow, not before."
                ),
                "check": "Is the technique I am about to use one I could write "
                         "correctly first time?",
                "uses": ["g-longest-unique-substring", "g-word-break", "g-three-sum",
                         "g-valid-palindrome", "g-largest-rectangle"],
            },
        ],
    },
]
