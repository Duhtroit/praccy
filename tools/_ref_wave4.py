#!/usr/bin/env python3
"""Reference implementations for Grind 75 wave 4, used to compute the
expectations rather than recalling them from memory. Wave 3 produced seven wrong
answers that way; this file is the fix.

Run with: python3 tools/_ref_wave4.py
"""

from __future__ import annotations


def is_valid_bst(root):
    def walk(node, low, high):
        if node >= len(root) or root[node] is None:
            return True
        v = root[node]
        if not (low < v < high):
            return False
        return walk(2 * node + 1, low, v) and walk(2 * node + 2, v, high)
    return walk(0, float("-inf"), float("inf"))


def num_islands(grid):
    if not grid or not grid[0]:
        return 0
    R, C = len(grid), len(grid[0])

    def sink(r, c, ch):
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] != ch:
            return
        grid[r][c] = "0"
        sink(r + 1, c, ch)
        sink(r - 1, c, ch)
        sink(r, c + 1, ch)
        sink(r, c - 1, ch)

    n = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "1":
                n += 1
                sink(r, c, "1")
    return n


def oranges_rotting(grid):
    """A queue of the rotten, one minute per level.

    Two in-place variants were tried first and both were wrong: marking spoiled
    oranges with a third value and never turning them back into rotten ones
    stops the wave after a single minute, and turning them back but counting
    the minute before they can spread again overcounts by one per round. The
    queue has neither problem, because the level a cell was enqueued at *is*
    the minute it rotted.
    """
    from collections import deque

    rows, columns = len(grid), len(grid[0])
    pending = deque()
    fresh = 0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] == 2:
                pending.append((row, column))
            elif grid[row][column] == 1:
                fresh += 1
    minutes = 0
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
    while pending and fresh:
        minutes += 1
        for _ in range(len(pending)):
            row, column = pending.popleft()
            for row_step, column_step in steps:
                next_row, next_column = row + row_step, column + column_step
                if not (0 <= next_row < rows and 0 <= next_column < columns):
                    continue
                if grid[next_row][next_column] == 1:
                    grid[next_row][next_column] = 2
                    fresh -= 1
                    pending.append((next_row, next_column))
    return -1 if fresh else minutes


def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def combination_sum(candidates, target):
    out = []
    ordered = sorted(candidates)

    def rec(start, left, current):
        if left == 0:
            out.append(list(current))
            return
        for i in range(start, len(ordered)):
            if ordered[i] > left:
                break
            current.append(ordered[i])
            rec(i, left - ordered[i], current)
            current.pop()

    rec(0, target, [])
    return out


def permute(nums):
    out = []

    def rec(current, rest):
        if not rest:
            out.append(list(current))
            return
        for i in range(len(rest)):
            rec(current + [rest[i]], rest[:i] + rest[i + 1:])

    rec([], list(nums))
    return out


def merge_intervals(intervals):
    ordered = sorted([list(x) for x in intervals])
    out = []
    for start, end in ordered:
        if out and start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out


def lca_tree(root, p, q):
    """The general case, NOT the BST walk of LeetCode 235.

    There is no ordering here, so a node does not tell you which way to go.
    Both branches have to be searched, and the answer is whichever branch comes
    back having found something; a branch that finds both of them has just
    found the answer itself.
    """

    def find(node):
        if node >= len(root) or root[node] is None:
            return None
        if root[node] == p or root[node] == q:
            return root[node]
        left = find(2 * node + 1)
        right = find(2 * node + 2)
        if left is not None and right is not None:
            # Both values turned up below this node, on opposite sides, so this
            # is the first node that is an ancestor of both. Returning `left`
            # here instead would give the leftmost hit, not the ancestor.
            return root[node]
        return left if left is not None else right

    hit = find(0)
    return -1 if hit is None else hit


def accounts_merge(accounts):
    owner = {}
    for row in accounts:
        for email in row[1:]:
            if email not in owner:
                owner[email] = row[0]
    groups = {}
    for email, name in owner.items():
        groups.setdefault(name, []).append(email)
    return sorted([name] + sorted(emails) for name, emails in groups.items())


def sort_colors(nums):
    out = list(nums)
    lo, mid, hi = 0, 0, len(out) - 1
    while mid <= hi:
        if out[mid] == 0:
            out[lo], out[mid] = out[mid], out[lo]
            lo += 1
            mid += 1
        elif out[mid] == 2:
            out[mid], out[hi] = out[hi], out[mid]
            hi -= 1
        else:
            mid += 1
    return out


def show(label, cases, fn):
    """`cases` entries are either a single argument or a tuple of arguments.

    Grid questions take a list of rows and mutate it, so each case is copied
    before it is run -- otherwise the second call sees the first call's flood.
    """
    print("== " + label + " ==")
    for case in cases:
        args = case if isinstance(case, tuple) else (case,)
        shown = list(args)
        args = tuple([r[:] for r in a] if isinstance(a, list) and a
                     and isinstance(a[0], list) else a for a in args)
        print("  ", shown, "->", fn(*args))
    print()


if __name__ == "__main__":
    show("39 Validate BST", [
        [2, 1, 3], [5, 1, 4, None, None, 3, 6], [10, 5, 15, None, None, 6, 20],
        [2, 2, 2], [1], [], [3, 1, 5, None, None, 2, 4],
    ], is_valid_bst)

    show("40 Number of Islands", [
        [["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"],
         ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]],
        [["1", "1", "0"], ["0", "1", "0"], ["0", "0", "1"]],
        [["0", "0"], ["0", "0"]], [["1"]], [[]],
    ], num_islands)

    show("41 Rotting Oranges", [
        [[2, 1, 1], [1, 1, 0], [0, 1, 1]],
        [[2, 1, 1], [0, 1, 1], [1, 0, 1]],
        [[0, 2]], [[0]], [[1]], [[2]], [[0, 0]],
    ], oranges_rotting)

    show("42 Search Rotated", [
        ([4, 5, 6, 7, 0, 1, 2], 0), ([4, 5, 6, 7, 0, 1, 2], 3), ([4, 5, 6, 7, 0, 1, 2], 2),
        ([1], 0), ([], 5), ([1, 3], 3), ([3, 1], 1), ([5, 1, 3], 3),
    ], search_rotated)

    show("43 Combination Sum", [
        ([2, 3, 6, 7], 7), ([2, 3, 5], 8), ([2], 1), ([2], 0), ([1], 1), ([], 3),
        ([8, 4], 3),
    ], combination_sum)

    show("44 Permutations", [
        [1, 2, 3], [1], [0], [], [3, 1],
    ], permute)

    show("45 Merge Intervals", [
        [[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 4], [4, 5]], [[1, 4], [0, 4]],
        [[1, 4], [2, 3]], [], [[1, 4], [4, 4]], [[1, 5], [2, 3], [3, 7], [4, 8]],
    ], merge_intervals)

    show("46 LCA Binary Tree", [
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1),
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4),
        ([1, 2], 1, 2), ([1, 2], 2, 1), ([1], 1, 1), ([], 1, 1),
        ([2, 1, 3], 1, 3),
    ], lca_tree)

    show("48 Accounts Merge", [
        [["John", "j1@m.co", "j2@m.co"], ["John", "j3@m.co", "j4@m.co"], ["Mary", "m1@m.co"]],
        [["Gabe", "G0@e.com"], ["Kevin", "Kevin0@e.com", "Kevin1@e.com"],
         ["Ethan", "E0@e.com"], ["Hanzo", "H0@e.com", "H1@e.com"]],
        [["a", "b@c"], ["a", "b@c"], ["a", "d@c"]],
        [["x", "p@q"], ["y", "r@q"]],
        [["z", "only@one"]],
    ], accounts_merge)

    show("49 Sort Colors", [
        [2, 0, 2, 1, 1, 0], [2, 0, 1], [0], [1], [2], [], [2, 2, 0, 0, 1, 1],
    ], sort_colors)
