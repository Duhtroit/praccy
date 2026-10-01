#!/usr/bin/env python3
"""Rust reference solutions, keyed by question id.

The other four languages keep their solutions inline in the `S(...)` call next
to the question, which reads well for one language and turns into a wall for
five. Rust is therefore held here instead: one file, one entry per question,
and the builders fail loudly if an id is missing rather than shipping a
question with no Rust.

The expected shape of every entry is the LeetCode one:

    impl Solution {
        pub fn snake_case_name(args) -> ReturnType { ... }
    }

`cbp/adapters.py::_rust_method` derives the method name from the question's
Coderbyte function name, so `ABCheck` is `ab_check`.
"""

from __future__ import annotations

RUST = {}

RUST["ab-check"] = r'''
impl Solution {
    pub fn ab_check(str: &str) -> String {
        let a = str.chars().filter(|c| *c == 'a').count();
        let b = str.chars().filter(|c| *c == 'b').count();
        if a == b { "true".to_string() } else { "false".to_string() }
    }
}
'''

RUST["additive-persistence"] = r'''
impl Solution {
    pub fn additive_persistence(num: i64) -> i64 {
        let mut n = num;
        let mut steps = 0;
        while n >= 10 {
            n = n.to_string().bytes().map(|b| (b - b'0') as i64).sum();
            steps += 1;
        }
        steps
    }
}
'''

RUST["alphabet-soup"] = r'''
impl Solution {
    pub fn alphabet_soup(str: &str) -> String {
        let mut letters: Vec<char> = str.chars().collect();
        letters.sort_unstable();
        letters.into_iter().collect()
    }
}
'''

RUST["arith-geo"] = r'''
impl Solution {
    pub fn arith_geo(arr: Vec<i64>) -> CBResult {
        if arr.len() < 3 {
            return CBResult::Str("none".to_string());
        }
        let step = arr[1] - arr[0];
        if arr.windows(2).all(|w| w[1] - w[0] == step) {
            return CBResult::Str("Arithmetic".to_string());
        }
        if arr[0] != 0 && arr[1] % arr[0] == 0 {
            let ratio = arr[1] / arr[0];
            if ratio != 0 && arr.windows(2).all(|w| w[1] == w[0] * ratio) {
                return CBResult::Str("Geometric".to_string());
            }
        }
        CBResult::Int(-1)
    }
}
'''

RUST["arith-geo-ii"] = r'''
impl Solution {
    pub fn arith_geo_ii(arr: Vec<i64>) -> CBResult {
        if arr.len() < 3 {
            return CBResult::Str("none".to_string());
        }
        let step = arr[1] - arr[0];
        if arr.windows(2).all(|w| w[1] - w[0] == step) {
            return CBResult::Str("Arithmetic".to_string());
        }
        if arr[0] != 0 && arr[1] % arr[0] == 0 {
            let ratio = arr[1] / arr[0];
            if ratio != 0 && arr.windows(2).all(|w| w[1] == w[0] * ratio) {
                return CBResult::Str("Geometric".to_string());
            }
        }
        CBResult::Int(-1)
    }
}
'''

RUST["changing-sequence"] = r'''
impl Solution {
    pub fn changing_sequence(num: i64) -> i64 {
        let mut n = num;
        let mut steps = 0i64;
        while n != 1 {
            n = if n % 2 == 0 { n / 2 } else { n - 1 };
            steps += 1;
        }
        steps
    }
}
'''

RUST["array-addition"] = r'''
impl Solution {
    pub fn array_addition(array: Vec<String>) -> String {
        // Coderbyte hands over one comma-separated string per array slot, so
        // the numbers have to be parsed out before anything else happens.
        let nums: Vec<i64> = array
            .iter()
            .flat_map(|chunk| chunk.split(','))
            .filter_map(|part| part.trim().parse().ok())
            .collect();
        for i in 0..nums.len() {
            for j in (i + 1)..nums.len() {
                if nums[i] + nums[j] == 0 {
                    return format!("{}{}", nums[i], nums[j]);
                }
            }
        }
        "not possible".to_string()
    }
}
'''

RUST["array-addition-i"] = r'''
impl Solution {
    pub fn array_addition_i(arr: Vec<i64>) -> i64 {
        let mut best = i64::MIN;
        for i in 0..arr.len() {
            for j in (i + 1)..arr.len() {
                best = best.max(arr[i] + arr[j]);
            }
        }
        best
    }
}
'''

RUST["array-matching"] = r'''
impl Solution {
    pub fn array_matching(array: Vec<String>) -> String {
        if array.len() < 2 || array[0].chars().count() != array[1].chars().count() {
            return "false".to_string();
        }
        "true".to_string()
    }
}
'''

RUST["basic-roman-numerals"] = r'''
impl Solution {
    pub fn roman_numerals(number: i64) -> String {
        // The subtractive pairs (IV, IX, XL, ...) are what make this more than
        // a lookup table: without them 4 would come out as IIII.
        const TABLE: [(i64, &str); 13] = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
        ];
        let mut n = number;
        let mut out = String::new();
        for (value, symbol) in TABLE {
            while n >= value {
                out.push_str(symbol);
                n -= value;
            }
        }
        out
    }
}
'''

RUST["binary-reversal"] = r'''
impl Solution {
    pub fn binary_reversal(n: i64) -> i64 {
        let mut n = n;
        let mut out = 0i64;
        while n > 0 {
            out = out * 2 + (n & 1);
            n >>= 1;
        }
        out
    }
}
'''

RUST["bitwise-one"] = r'''
impl Solution {
    pub fn bitwise_one(num: i64) -> i64 {
        num.count_ones() as i64
    }
}
'''

RUST["best-time-to-trade"] = r'''
impl Solution {
    pub fn max_profit(arr: Vec<i64>) -> i64 {
        // One pass: remember the cheapest day seen so far and the best profit
        // any later day could have produced from it.
        let mut cheapest = i64::MAX;
        let mut best = 0i64;
        for price in arr {
            cheapest = cheapest.min(price);
            best = best.max(price - cheapest);
        }
        best
    }
}
'''

RUST["bracket-matcher"] = r'''
impl Solution {
    pub fn bracket_matcher(str: &str) -> String {
        let mut stack: Vec<char> = Vec::new();
        for ch in str.chars() {
            match ch {
                '(' | '[' | '{' => stack.push(ch),
                ')' => if stack.pop() != Some('(') { return "false".to_string() },
                ']' => if stack.pop() != Some('[') { return "false".to_string() },
                '}' => if stack.pop() != Some('{') { return "false".to_string() },
                _ => {}
            }
        }
        if stack.is_empty() { "true".to_string() } else { "false".to_string() }
    }
}
'''

RUST["caesar-cipher"] = r'''
impl Solution {
    pub fn caesar_cipher(str: &str, num: i64) -> String {
        let shift = ((num % 26) + 26) % 26;
        str.chars()
            .map(|c| {
                let base = if c.is_ascii_uppercase() { b'A' } else { b'a' };
                if c.is_ascii_alphabetic() {
                    let offset = (c as u8 - base) as i64;
                    (base + ((offset + shift) % 26) as u8) as char
                } else {
                    c
                }
            })
            .collect()
    }
}
'''

RUST["lc-candy"] = r'''
impl Solution {
    pub fn candy(ratings: Vec<i64>) -> i64 {
        let n = ratings.len();
        if n == 0 {
            return 0;
        }
        let mut candies = vec![1i64; n];
        // Left to right, then right to left. Each pass can only push a rating
        // up, and doing them in opposite directions is what keeps the total
        // minimal.
        for i in 1..n {
            if ratings[i] > ratings[i - 1] {
                candies[i] = candies[i - 1] + 1;
            }
        }
        for i in (0..n - 1).rev() {
            if ratings[i] > ratings[i + 1] && candies[i] <= candies[i + 1] {
                candies[i] = candies[i + 1] + 1;
            }
        }
        candies.iter().sum()
    }
}
'''

RUST["check-nums"] = r'''
impl Solution {
    pub fn check_nums(arr: Vec<i64>) -> String {
        if arr.iter().all(|n| *n > 0) { "true".to_string() } else { "false".to_string() }
    }
}
'''

RUST["coin-determiner"] = r'''
impl Solution {
    pub fn coin_determiner(coins: Vec<i64>, amount: i64) -> i64 {
        if amount < 0 {
            return -1;
        }
        // Bottom-up dynamic programming beats the greedy choice here: greedy
        // is only correct for canonical coin systems like US currency, and
        // nothing in the prompt promises that.
        let mut best = vec![i64::MAX; (amount + 1) as usize];
        best[0] = 0;
        for value in 1..=amount {
            for coin in &coins {
                if *coin <= value && best[(value - coin) as usize] != i64::MAX {
                    let candidate = best[(value - coin) as usize] + 1;
                    if candidate < best[value as usize] {
                        best[value as usize] = candidate;
                    }
                }
            }
        }
        if best[amount as usize] == i64::MAX { -1 } else { best[amount as usize] }
    }
}
'''

RUST["consecutive"] = r'''
impl Solution {
    pub fn consecutive(array: Vec<i64>) -> i64 {
        // Sort, then count maximal runs of unbroken integers. Duplicates are
        // collapsed first so [5,5,6,6] is one run rather than four.
        let mut values = array;
        values.sort_unstable();
        values.dedup();
        let mut runs = 0i64;
        let mut run = 1i64;
        for i in 1..values.len() {
            if values[i] == values[i - 1] + 1 {
                run += 1;
            } else {
                if run > 1 { runs += 1; }
                run = 1;
            }
        }
        if run > 1 { runs += 1; }
        runs
    }
}
'''

RUST["contains-duplicate"] = r'''
impl Solution {
    pub fn contains_duplicate(arr: Vec<i64>) -> String {
        use std::collections::HashSet;
        let mut seen = HashSet::new();
        for n in arr {
            if !seen.insert(n) {
                return "true".to_string();
            }
        }
        "false".to_string()
    }
}
'''

RUST["counting-minutes"] = r'''
impl Solution {
    pub fn counting_minutes(array: Vec<String>) -> Vec<i64> {
        let to_minutes = |stamp: &str| -> i64 {
            let (h, m) = stamp.split_once(':').unwrap_or((stamp, "0"));
            h.trim().parse::<i64>().unwrap_or(0) * 60 + m.trim().parse::<i64>().unwrap_or(0)
        };
        array.windows(2)
            .map(|pair| to_minutes(&pair[1]) - to_minutes(&pair[0]))
            .collect()
    }
}
'''

RUST["counting-minutes-i"] = r'''
impl Solution {
    pub fn counting_minutes_i(str: &str) -> Vec<i64> {
        let to_minutes = |stamp: &str| -> i64 {
            let (h, m) = stamp.split_once(':').unwrap_or((stamp, "0"));
            h.trim().parse::<i64>().unwrap_or(0) * 60 + m.trim().parse::<i64>().unwrap_or(0)
        };
        let stamps: Vec<&str> = str.split_whitespace().collect();
        stamps
            .windows(2)
            .map(|pair| to_minutes(pair[1]) - to_minutes(pair[0]))
            .collect()
    }
}
'''

RUST["dash-insert"] = r'''
impl Solution {
    pub fn dash_insert(str: &str) -> String {
        // One dash per *pair* of digits, not one per boundary, so "13579"
        // becomes "1-35-79" rather than "1-3-5-7-9".
        let mut out = String::new();
        for (i, ch) in str.chars().enumerate() {
            if i > 0 && i % 2 == 1 && ch.is_ascii_digit() && str.as_bytes()[i - 1].is_ascii_digit() {
                out.push('-');
            }
            out.push(ch);
        }
        out
    }
}
'''

RUST["lc-decode-ways"] = r'''
impl Solution {
    pub fn decode_ways(str: &str) -> i64 {
        let digits: Vec<i64> = str.bytes().map(|b| (b - b'0') as i64).collect();
        if digits.first() == Some(&0) {
            return 0;
        }
        // ways[i] counts the decodings of the first i digits, so the answer
        // only ever depends on the last two.
        let mut prev_two = 1i64;
        let mut prev_one = 1i64;
        for i in 1..digits.len() {
            let mut ways = 0;
            if digits[i] != 0 {
                ways += prev_one;
            }
            let two_digit = digits[i - 1] * 10 + digits[i];
            if two_digit >= 10 && two_digit <= 26 {
                ways += prev_two;
            }
            prev_two = prev_one;
            prev_one = ways;
        }
        prev_one
    }
}
'''

RUST["division-stringified"] = r'''
impl Solution {
    pub fn division_stringified(number: i64) -> String {
        // The hour is left unpadded; only minutes and seconds are fixed width.
        format!("{}:{:02}:{:02}", number / 3600, (number % 3600) / 60, number % 60)
    }
}
'''

RUST["even-pairs"] = r'''
impl Solution {
    pub fn even_pairs(arr: Vec<i64>) -> i64 {
        // Every even/odd pairing is valid and every even/even or odd/odd
        // pairing is not, so the count is a plain product.
        let evens = arr.iter().filter(|n| **n % 2 == 0).count() as i64;
        let odds = arr.len() as i64 - evens;
        evens * odds
    }
}
'''

RUST["ex-oh"] = r'''
impl Solution {
    pub fn ex_oh(str: &str) -> String {
        let x = str.chars().filter(|c| *c == 'x').count();
        let o = str.chars().filter(|c| *c == 'o').count();
        if x == o { "true".to_string() } else { "false".to_string() }
    }
}
'''

RUST["first-factorial"] = r'''
impl Solution {
    pub fn first_factorial(num: i64) -> i64 {
        (1..=num).product()
    }
}
'''

RUST["lc-first-missing-positive"] = r'''
impl Solution {
    pub fn first_missing(arr: Vec<i64>) -> i64 {
        let n = arr.len();
        let mut values = arr;
        // Park each value v in 1..=n at index v-1. Afterwards the first index
        // holding a value that is not i+1 names the answer, in O(n) with no
        // extra array.
        for i in 0..n {
            loop {
                let v = values[i];
                if v < 1 || v > n as i64 || values[(v - 1) as usize] == v {
                    break;
                }
                let target = (v - 1) as usize;
                values.swap(i, target);
            }
        }
        for i in 0..n {
            if values[i] != (i as i64) + 1 {
                return i as i64 + 1;
            }
        }
        n as i64 + 1
    }
}
'''

RUST["first-reverse"] = r'''
impl Solution {
    pub fn first_reverse(str: &str) -> String {
        str.chars().rev().collect()
    }
}
'''

RUST["hamming-distance"] = r'''
impl Solution {
    pub fn hamming_distance(a: &str, b: &str) -> i64 {
        a.chars().zip(b.chars()).filter(|(x, y)| x != y).count() as i64
    }
}
'''

RUST["house-robber"] = r'''
impl Solution {
    pub fn robber(arr: Vec<i64>) -> i64 {
        // Robbing house i means house i-1 is off limits, so each answer is the
        // better of "rob this one" and "skip it and take the best so far".
        let (mut skip, mut take) = (0i64, 0i64);
        for amount in arr {
            let next_take = skip + amount;
            skip = take.max(skip);
            take = next_take;
        }
        take.max(skip)
    }
}
'''

RUST["valid-palindrome-ii"] = r'''
impl Solution {
    pub fn is_palindrome_ii(str: &str) -> String {
        let chars: Vec<char> = str.chars().filter(|c| c.is_alphanumeric()).collect();
        let palindrome = |slice: &[char]| slice.iter().eq(slice.iter().rev());
        let (mut left, mut right) = (0usize, chars.len().saturating_sub(1));
        while left < right {
            if chars[left] != chars[right] {
                // The first mismatch has to be the single character we are
                // allowed to delete, so try deleting either side.
                let without_left = &chars[left + 1..=right];
                let without_right = &chars[left..right];
                if palindrome(without_left) || palindrome(without_right) {
                    return "true".to_string();
                }
                return "false".to_string();
            }
            left += 1;
            right -= 1;
        }
        "true".to_string()
    }
}
'''

RUST["largest-pair"] = r'''
impl Solution {
    pub fn largest_pair(numbers: &str, pair: &str) -> String {
        let values: Vec<i64> = numbers
            .split(',')
            .filter_map(|part| part.trim().parse().ok())
            .collect();
        let total: i64 = values.iter().sum();
        if total % 2 != 0 {
            return "false".to_string();
        }
        let half = total / 2;
        let parts: Vec<i64> = pair
            .split(',')
            .filter_map(|part| part.trim().parse().ok())
            .collect();
        if parts.len() == 2 && parts[0] + parts[1] == half {
            "true".to_string()
        } else {
            "false".to_string()
        }
    }
}
'''

RUST["letter-capitalize"] = r'''
impl Solution {
    pub fn letter_capitalize(str: &str) -> String {
        let mut out = String::new();
        for (i, ch) in str.chars().enumerate() {
            if i == 0 || str.as_bytes()[i - 1] == b' ' {
                out.extend(ch.to_uppercase());
            } else {
                out.push(ch);
            }
        }
        out
    }
}
'''

RUST["letter-changes"] = r'''
impl Solution {
    pub fn letter_changes(str: &str) -> String {
        str.chars()
            .map(|c| {
                if !c.is_ascii_alphabetic() {
                    return c;
                }
                // Shift first, then capitalise, in that order. Doing it the
                // other way round would capitalise the vowels you started with
                // instead of the ones you shifted into.
                let base = if c.is_ascii_uppercase() { b'A' } else { b'a' };
                let shifted = (base + ((c as u8 - base + 1) % 26) as u8) as char;
                if "aeiou".contains(shifted) {
                    shifted.to_ascii_uppercase()
                } else {
                    shifted
                }
            })
            .collect()
    }
}
'''

RUST["letter-count"] = r'''
impl Solution {
    pub fn letter_count(arr: Vec<String>, n: i64) -> String {
        arr.iter()
            .filter(|word| word.chars().count() as i64 == n)
            .count()
            .to_string()
    }
}
'''

RUST["letter-count-i"] = r'''
impl Solution {
    pub fn letter_count_i(str: &str) -> String {
        use std::collections::HashMap;
        let mut counts: HashMap<char, i32> = HashMap::new();
        for ch in str.chars() {
            *counts.entry(ch).or_insert(0) += 1;
        }
        let mut singles: Vec<char> = counts
            .into_iter()
            .filter(|(_, count)| *count == 1)
            .map(|(ch, _)| ch)
            .collect();
        singles.sort_unstable();
        singles.into_iter().collect()
    }
}
'''

RUST["longest-common-prefix"] = r'''
impl Solution {
    pub fn longest_common_prefix(arr: Vec<String>) -> String {
        let Some(first) = arr.first() else { return String::new() };
        let first = first.as_str();
        // Shortest string bounds the search, so start there and give up the
        // moment one candidate stops matching.
        for (i, ch) in first.chars().enumerate() {
            if arr.iter().any(|word| !word.is_char_boundary(i) || word.chars().nth(i) != Some(ch)) {
                return first[..i].to_string();
            }
        }
        first.to_string()
    }
}
'''

RUST["longest-increasing-sequence"] = r'''
impl Solution {
    pub fn longest_increasing_sequence(arr: Vec<i64>) -> i64 {
        // tails[k] is the smallest possible tail of an increasing run of
        // length k+1, so the answer is just how far the array is.
        let mut tails: Vec<i64> = Vec::new();
        for value in arr {
            let at = tails.partition_point(|t| *t < value);
            if at == tails.len() {
                tails.push(value);
            } else {
                tails[at] = value;
            }
        }
        tails.len() as i64
    }
}
'''

RUST["longest-repeating-char"] = r'''
impl Solution {
    pub fn longest_repeating_run(str: &str) -> i64 {
        let mut best = 0i64;
        let mut run = 0i64;
        let mut previous: Option<char> = None;
        for ch in str.chars() {
            run = if Some(ch) == previous { run + 1 } else { 1 };
            best = best.max(run);
            previous = Some(ch);
        }
        best
    }
}
'''

RUST["longest-word"] = r'''
impl Solution {
    pub fn longest_word(sen: &str) -> String {
        let mut best = String::new();
        for raw in sen.split_whitespace() {
            let word: String = raw.chars().filter(|c| c.is_alphanumeric()).collect();
            // Strictly greater keeps the earliest word on a tie, which is
            // what the prompt asks for.
            if word.chars().count() > best.chars().count() {
                best = word;
            }
        }
        best
    }
}
'''

RUST["maximum-subarray"] = r'''
impl Solution {
    pub fn max_subarray(arr: Vec<i64>) -> i64 {
        // Kadane: the best run ending at each position, or that element alone.
        let mut best = arr.first().copied().unwrap_or(0);
        let mut running = best;
        for value in arr.iter().skip(1) {
            running = (*value).max(running + value);
            best = best.max(running);
        }
        best
    }
}
'''

RUST["lc-container-water"] = r'''
impl Solution {
    pub fn max_area(heights: Vec<i64>) -> i64 {
        let (mut left, mut right) = (0i64, heights.len() as i64 - 1);
        let mut best = 0i64;
        while left < right {
            let width = right - left;
            let area = width * heights[left as usize].min(heights[right as usize]);
            best = best.max(area);
            // Moving the taller wall in can only lose area, so always move the
            // shorter one -- that is what keeps this linear.
            if heights[left as usize] < heights[right as usize] {
                left += 1;
            } else {
                right -= 1;
            }
        }
        best
    }
}
'''

RUST["mean-mode"] = r'''
impl Solution {
    pub fn mean_mode(arr: Vec<i64>) -> i64 {
        use std::collections::HashMap;
        let mut counts: HashMap<i64, i64> = HashMap::new();
        for n in &arr {
            *counts.entry(*n).or_insert(0) += 1;
        }
        // Highest count wins; smallest value breaks the tie.
        counts
            .into_iter()
            .max_by_key(|(value, count)| (*count, -value))
            .map(|(value, _)| value)
            .unwrap_or(0)
    }
}
'''

RUST["lc-median-two-sorted"] = r'''
impl Solution {
    pub fn median_two_sorted(a: Vec<i64>, b: Vec<i64>) -> f64 {
        // Merging is O(n); concatenating and sorting would be O(n log n) and
        // would throw away the one property the input guarantees.
        let (mut i, mut j) = (0usize, 0usize);
        let mut merged: Vec<i64> = Vec::with_capacity(a.len() + b.len());
        while i < a.len() && j < b.len() {
            if a[i] <= b[j] {
                merged.push(a[i]);
                i += 1;
            } else {
                merged.push(b[j]);
                j += 1;
            }
        }
        merged.extend_from_slice(&a[i..]);
        merged.extend_from_slice(&b[j..]);

        let n = merged.len();
        if n == 0 {
            return 0.0;
        }
        if n % 2 == 1 {
            merged[n / 2] as f64
        } else {
            (merged[n / 2 - 1] + merged[n / 2]) as f64 / 2.0
        }
    }
}
'''

RUST["missing-number"] = r'''
impl Solution {
    pub fn missing_number(arr: Vec<i64>) -> i64 {
        // 0 + 1 + ... + n is the full set, so the gap is the difference.
        let n = arr.len() as i64;
        n * (n + 1) / 2 - arr.iter().sum::<i64>()
    }
}
'''

RUST["multiplicative-persistence"] = r'''
impl Solution {
    pub fn multiplicative_persistence(n: i64) -> i64 {
        let mut n = n;
        let mut steps = 0;
        while n >= 10 {
            n = n.to_string().bytes().map(|b| (b - b'0') as i64).product();
            steps += 1;
        }
        steps
    }
}
'''

RUST["nonrepeating-character"] = r'''
impl Solution {
    pub fn non_repeating_character(str: &str) -> i64 {
        use std::collections::HashMap;
        let chars: Vec<char> = str.chars().collect();
        let mut counts: HashMap<char, i64> = HashMap::new();
        for ch in &chars {
            *counts.entry(*ch).or_insert(0) += 1;
        }
        for (index, ch) in chars.iter().enumerate() {
            if counts[ch] == 1 {
                return index as i64;
            }
        }
        -1
    }
}
'''

RUST["number-addition"] = r'''
impl Solution {
    pub fn number_addition(num: i64) -> i64 {
        num.to_string().bytes().map(|b| (b - b'0') as i64).sum()
    }
}
'''

RUST["off-line-minimum"] = r'''
impl Solution {
    pub fn off_line_minimum(arr: Vec<i64>) -> i64 {
        let mut candidate = 1i64;
        for n in arr {
            if n == candidate {
                candidate += 1;
            }
        }
        candidate
    }
}
'''

RUST["other-products"] = r'''
impl Solution {
    pub fn other_products(array: Vec<i64>) -> Vec<i64> {
        let mut prefix = vec![1i64; array.len()];
        for i in 1..array.len() {
            prefix[i] = prefix[i - 1] * array[i - 1];
        }
        let mut suffix = 1i64;
        for i in (0..array.len()).rev() {
            prefix[i] *= suffix;
            suffix *= array[i];
        }
        prefix
    }
}
'''

RUST["overlapping-ranges"] = r'''
impl Solution {
    pub fn overlapping_ranges(array: Vec<String>) -> String {
        let parse = |range: &str| -> (i64, i64) {
            let (a, b) = range.split_once('-').unwrap_or((range, range));
            (
                a.trim().parse().unwrap_or(0),
                b.trim().parse().unwrap_or(0),
            )
        };
        if array.len() < 2 {
            return "false".to_string();
        }
        let (a_start, a_end) = parse(&array[0]);
        let (b_start, b_end) = parse(&array[1]);
        // Closed intervals, so touching at a single point counts.
        if a_start <= b_end && b_start <= a_end {
            "true".to_string()
        } else {
            "false".to_string()
        }
    }
}
'''

RUST["palindrome"] = r'''
impl Solution {
    pub fn palindrome(str: &str) -> String {
        let chars: Vec<char> = str.chars().collect();
        if chars.iter().eq(chars.iter().rev()) {
            "true".to_string()
        } else {
            "false".to_string()
        }
    }
}
'''

RUST["palindrome-two"] = r'''
impl Solution {
    pub fn palindrome_two(str: &str) -> String {
        // Punctuation and spacing are noise, so they are dropped before the
        // comparison rather than being allowed to fail it.
        let cleaned: String = str
            .chars()
            .filter(|c| c.is_alphanumeric())
            .flat_map(|c| c.to_lowercase())
            .collect();
        if cleaned.chars().eq(cleaned.chars().rev()) {
            "true".to_string()
        } else {
            "false".to_string()
        }
    }
}
'''

RUST["plus-one"] = r'''
impl Solution {
    pub fn plus_one(arr: Vec<i64>) -> Vec<i64> {
        let mut digits = arr;
        for i in (0..digits.len()).rev() {
            if digits[i] < 9 {
                digits[i] += 1;
                return digits;
            }
            digits[i] = 0;
        }
        digits.insert(0, 1);
        digits
    }
}
'''

RUST["powers-of-two"] = r'''
impl Solution {
    pub fn powers_of_two(num: i64) -> i64 {
        // 1 counts as zero divisions: it is already the destination.
        let mut n = num;
        let mut count = 0i64;
        while n > 1 {
            n /= 2;
            count += 1;
        }
        count
    }
}
'''

RUST["prime-time"] = r'''
impl Solution {
    pub fn prime_time(num: i64) -> i64 {
        let is_prime = |n: i64| -> bool {
            if n < 2 { return false; }
            (2..=(n as f64).sqrt() as i64).all(|d| n % d != 0)
        };
        (2..num).filter(|n| is_prime(*n)).count() as i64
    }
}
'''

RUST["product-digits"] = r'''
impl Solution {
    pub fn product_digits(num: i64) -> i64 {
        num.to_string().bytes().map(|b| (b - b'0') as i64).product()
    }
}
'''

RUST["product-except-self"] = r'''
impl Solution {
    pub fn product_except_self(arr: Vec<i64>) -> Vec<i64> {
        // Two sweeps instead of division: one fills in everything to the left,
        // the other multiplies in everything to the right. Division was ruled
        // out by the prompt, and it would also break on the zero cases.
        let n = arr.len();
        let mut out = vec![1i64; n];
        for i in 1..n {
            out[i] = out[i - 1] * arr[i - 1];
        }
        let mut suffix = 1i64;
        for i in (0..n).rev() {
            out[i] *= suffix;
            suffix *= arr[i];
        }
        out
    }
}
'''

RUST["rectangle-area"] = r'''
impl Solution {
    pub fn rectangle_area(array: Vec<i64>) -> i64 {
        if array.len() < 3 {
            return 0;
        }
        array[0] * array[2]
    }
}
'''

RUST["reverse-words"] = r'''
impl Solution {
    pub fn reverse_words(str: &str) -> String {
        str.split_whitespace().rev().collect::<Vec<_>>().join(" ")
    }
}
'''

RUST["run-length"] = r'''
impl Solution {
    pub fn run_length(str: &str) -> String {
        let mut out = String::new();
        let mut previous: Option<char> = None;
        let mut run = 0usize;
        for ch in str.chars() {
            if Some(ch) == previous {
                run += 1;
            } else {
                if let Some(p) = previous {
                    out.push_str(&run.to_string());
                    out.push(p);
                }
                previous = Some(ch);
                run = 1;
            }
        }
        if let Some(p) = previous {
            out.push_str(&run.to_string());
            out.push(p);
        }
        out
    }
}
'''

RUST["search-insert-position"] = r'''
impl Solution {
    pub fn search_insert(arr: Vec<i64>, target: i64) -> i64 {
        // Lower bound: the first index whose value is >= target, which is
        // also the insert position when the target is absent.
        let mut low = 0i64;
        let mut high = arr.len() as i64;
        while low < high {
            let mid = low + (high - low) / 2;
            if arr[mid as usize] < target {
                low = mid + 1;
            } else {
                high = mid;
            }
        }
        low
    }
}
'''

RUST["lc-search-rotated"] = r'''
impl Solution {
    pub fn search_rotated(arr: Vec<i64>, target: i64) -> i64 {
        let (mut low, mut high) = (0i64, arr.len() as i64 - 1);
        while low <= high {
            let mid = low + (high - low) / 2;
            if arr[mid as usize] == target {
                return mid;
            }
            if arr[low as usize] <= arr[mid as usize] {
                // Left half is sorted, so it is the only place the target can be.
                if arr[low as usize] <= target && target < arr[mid as usize] {
                    high = mid - 1;
                } else {
                    low = mid + 1;
                }
            } else if arr[mid as usize] < target && target <= arr[high as usize] {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        -1
    }
}
'''

RUST["second-greatlow"] = r'''
impl Solution {
    pub fn second_great_low(arr: Vec<i64>) -> i64 {
        let mut values: Vec<i64> = arr.clone();
        values.sort_unstable();
        values.dedup();
        if values.len() < 2 {
            return -1;
        }
        values[1]
    }
}
'''

RUST["simple-adding"] = r'''
impl Solution {
    pub fn simple_adding(arr: Vec<i64>) -> i64 {
        arr.iter().sum()
    }
}
'''

RUST["simple-mode"] = r'''
impl Solution {
    pub fn simple_mode(array: Vec<i64>) -> i64 {
        use std::collections::HashMap;
        let mut counts: HashMap<i64, i64> = HashMap::new();
        for n in &array {
            *counts.entry(*n).or_insert(0) += 1;
        }
        counts
            .into_iter()
            .max_by_key(|(value, count)| (*count, -value))
            .map(|(value, _)| value)
            .unwrap_or(0)
    }
}
'''

RUST["simple-symbols"] = r'''
impl Solution {
    pub fn simple_symbols(str: &str) -> String {
        let chars: Vec<char> = str.chars().collect();
        for (i, ch) in chars.iter().enumerate() {
            if ch.is_alphabetic()
                && (i == 0 || chars[i - 1] != '+' || i + 1 >= chars.len() || chars[i + 1] != '+')
            {
                return "false".to_string();
            }
        }
        "true".to_string()
    }
}
'''

RUST["single-number"] = r'''
impl Solution {
    pub fn single_number(arr: Vec<i64>) -> i64 {
        // x ^ x == 0, so every pair cancels and the odd one out survives.
        arr.iter().fold(0i64, |acc, n| acc ^ n)
    }
}
'''

RUST["string-reduction"] = r'''
impl Solution {
    pub fn string_reduction(str: &str) -> String {
        // Reducing left to right and keeping a stack avoids re-reducing the
        // whole string after every step, which is what the naive pairwise
        // version costs.
        let mut stack: Vec<char> = Vec::new();
        for ch in str.chars() {
            if let Some(top) = stack.pop() {
                let difference = (top as u8).abs_diff(ch as u8);
                stack.push((b'a' + difference) as char);
            } else {
                stack.push(ch);
            }
        }
        stack.into_iter().collect()
    }
}
'''

RUST["string-scramble"] = r'''
impl Solution {
    pub fn string_scramble(str1: &str, str2: &str) -> String {
        use std::collections::HashMap;
        if str2.chars().count() > str1.chars().count() {
            return "false".to_string();
        }
        let mut available: HashMap<char, i64> = HashMap::new();
        for ch in str1.chars() {
            *available.entry(ch).or_insert(0) += 1;
        }
        for ch in str2.chars() {
            match available.get_mut(&ch) {
                Some(count) if *count > 0 => *count -= 1,
                _ => return "false".to_string(),
            }
        }
        "true".to_string()
    }
}
'''

RUST["lc-subarray-sum-k"] = r'''
impl Solution {
    pub fn subarray_sum_k(arr: Vec<i64>, k: i64) -> i64 {
        use std::collections::HashMap;
        // Count prefixes seen so far, seeded with 0 so a subarray starting at
        // index 0 is found. A second identical prefix is what makes a zero-sum
        // subarray, which is why the counts -- not just the keys -- matter.
        let mut seen: HashMap<i64, i64> = HashMap::new();
        seen.insert(0, 1);
        let mut sum = 0i64;
        let mut count = 0i64;
        for value in arr {
            sum += value;
            // Every earlier prefix that sits k below the current one closes a
            // subarray summing to k.
            count += seen.get(&(sum - k)).copied().unwrap_or(0);
            *seen.entry(sum).or_insert(0) += 1;
        }
        count
    }
}
'''

RUST["superincreasing"] = r'''
impl Solution {
    pub fn superincreasing(arr: Vec<i64>) -> String {
        let mut running = 0i64;
        for value in &arr {
            if *value <= running {
                return "false".to_string();
            }
            running += value;
        }
        "true".to_string()
    }
}
'''

RUST["swap-case"] = r'''
impl Solution {
    pub fn swap_case(str: &str) -> String {
        str.chars()
            .map(|c| {
                if c.is_uppercase() {
                    c.to_lowercase().next().unwrap_or(c)
                } else if c.is_lowercase() {
                    c.to_uppercase().next().unwrap_or(c)
                } else {
                    c
                }
            })
            .collect()
    }
}
'''

RUST["third-greatest"] = r'''
impl Solution {
    pub fn third_greatest(arr: Vec<i64>) -> i64 {
        let mut values = arr;
        values.sort_unstable();
        values.dedup();
        if values.len() < 3 {
            return -1;
        }
        values[values.len() - 3]
    }
}
'''

RUST["three-five-multiples"] = r'''
impl Solution {
    pub fn three_five_multiples(start: i64, limit: i64) -> i64 {
        (start..=limit)
            .filter(|n| n % 3 == 0 || n % 5 == 0)
            .sum()
    }
}
'''

RUST["time-convert"] = r'''
impl Solution {
    pub fn time_convert(num: i64) -> String {
        format!("{}:{:02}", num / 60, num % 60)
    }
}
'''

RUST["lc-trapping-rain-water"] = r'''
impl Solution {
    pub fn trap(heights: Vec<i64>) -> i64 {
        if heights.is_empty() {
            return 0;
        }
        // Two pointers, keeping a running max on each side. Each index is
        // visited once, so this is linear even though it looks like it might
        // not be.
        let (mut left, mut right) = (0usize, heights.len() - 1);
        let (mut left_max, mut right_max) = (0i64, 0i64);
        let mut water = 0i64;
        while left <= right {
            if heights[left] <= heights[right] {
                left_max = left_max.max(heights[left]);
                water += left_max - heights[left];
                left += 1;
            } else {
                right_max = right_max.max(heights[right]);
                water += right_max - heights[right];
                right -= 1;
            }
        }
        water
    }
}
'''

RUST["two-sum"] = r'''
impl Solution {
    pub fn two_sum(num: Vec<i64>, target: i64) -> CBResult {
        use std::collections::HashSet;
        // One pass over the values, returning the pair itself rather than two
        // indices, which is what Coderbyte asks for here.
        let mut seen: HashSet<i64> = HashSet::new();
        for value in &num {
            if seen.contains(&(target - value)) {
                return CBResult::Arr(vec![*value, target - value]);
            }
            seen.insert(*value);
        }
        CBResult::Str("not possible".to_string())
    }
}
'''

RUST["valid-anagram"] = r'''
impl Solution {
    pub fn is_anagram(str1: &str, str2: &str) -> String {
        use std::collections::HashMap;
        if str1.chars().count() != str2.chars().count() {
            return "false".to_string();
        }
        let mut counts: HashMap<char, i32> = HashMap::new();
        for ch in str1.chars() {
            *counts.entry(ch).or_insert(0) += 1;
        }
        for ch in str2.chars() {
            match counts.get_mut(&ch) {
                Some(count) => *count -= 1,
                None => return "false".to_string(),
            }
        }
        "true".to_string()
    }
}
'''

RUST["vowel-count"] = r'''
impl Solution {
    pub fn vowel_count(str: &str) -> i64 {
        str.chars()
            .filter(|c| "aeiou".contains(*c))
            .count() as i64
    }
}
'''

RUST["wave-sorting"] = r'''
impl Solution {
    pub fn wave_sorting(arr: Vec<i64>) -> Vec<i64> {
        let mut values = arr;
        values.sort_unstable();
        // Largest, smallest, second largest, second smallest. That alternation
        // is exactly the a[0] > a[1] < a[2] > ... shape.
        let (mut lo, mut hi) = (0usize, values.len().saturating_sub(1));
        let mut out = Vec::with_capacity(values.len());
        while lo <= hi {
            out.push(values[hi]);
            hi = hi.wrapping_sub(1);
            if lo <= hi {
                out.push(values[lo]);
                lo += 1;
            }
        }
        out
    }
}
'''

RUST["word-count"] = r'''
impl Solution {
    pub fn word_count(str: &str) -> String {
        str.split_whitespace().count().to_string()
    }
}
'''


# ── Grind 75, wave 1 ─────────────────────────────────────────────────────

RUST["g-valid-parentheses"] = r"""
impl Solution {
    pub fn valid_parentheses(s: &str) -> bool {
        let mut stack: Vec<char> = Vec::new();
        for ch in s.chars() {
            match ch {
                '(' | '[' | '{' => stack.push(ch),
                ')' | ']' | '}' => {
                    let want = match ch {
                        ')' => '(',
                        ']' => '[',
                        _ => '{',
                    };
                    if stack.pop() != Some(want) {
                        return false;
                    }
                }
                _ => {}
            }
        }
        stack.is_empty()
    }
}
"""

RUST["g-merge-two-sorted-lists"] = r"""
impl Solution {
    pub fn merge_two_sorted_lists(a: Vec<i64>, b: Vec<i64>) -> Vec<i64> {
        let mut out: Vec<i64> = Vec::with_capacity(a.len() + b.len());
        let (mut i, mut j) = (0usize, 0usize);
        while i < a.len() && j < b.len() {
            if a[i] <= b[j] {
                out.push(a[i]);
                i += 1;
            } else {
                out.push(b[j]);
                j += 1;
            }
        }
        out.extend_from_slice(&a[i..]);
        out.extend_from_slice(&b[j..]);
        out
    }
}
"""

RUST["g-best-time-to-trade"] = r"""
impl Solution {
    pub fn best_time_to_buy_and_sell_stock(prices: Vec<i64>) -> i64 {
        let mut best = 0i64;
        let mut low = 0i64;
        for (i, &price) in prices.iter().enumerate() {
            if i == 0 || price < low {
                low = price;
            } else if price - low > best {
                best = price - low;
            }
        }
        best
    }
}
"""

RUST["g-valid-palindrome"] = r"""
impl Solution {
    pub fn valid_palindrome(s: &str) -> bool {
        let clean: Vec<char> = s
            .chars()
            .filter(|c| c.is_alphanumeric())
            .map(|c| c.to_ascii_lowercase())
            .collect();
        clean.iter().zip(clean.iter().rev()).all(|(a, b)| a == b)
    }
}
"""

RUST["g-invert-binary-tree"] = r"""
impl Solution {
    pub fn invert_binary_tree(root: Vec<Option<i64>>) -> Vec<Option<i64>> {
        // A swap can move a value to an index past the end of the input, so the
        // array is widened first. Two children per node, one more level, is
        // enough for every swap the original tree can ask for.
        let size = root.len();
        let mut tree = vec![None; 2 * size + 1];
        for (i, value) in root.iter().enumerate() {
            tree[i] = *value;
        }
        for p in 0..size {
            if tree[p].is_none() {
                continue;
            }
            let left = 2 * p + 1;
            let right = left + 1;
            let left_value = tree[left];
            let right_value = tree[right];
            tree[left] = right_value;
            tree[right] = left_value;
        }
        while tree.last() == Some(&None) {
            tree.pop();
        }
        tree
    }
}
"""

RUST["g-binary-search"] = r"""
impl Solution {
    pub fn binary_search(nums: Vec<i64>, target: i64) -> i64 {
        let (mut low, mut high) = (0i64, nums.len() as i64 - 1);
        while low <= high {
            let mid = low + (high - low) / 2;
            if nums[mid as usize] == target {
                return mid;
            }
            if nums[mid as usize] < target {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        -1
    }
}
"""

RUST["g-flood-fill"] = r"""
impl Solution {
    pub fn flood_fill(mut image: Vec<Vec<i64>>, sr: i64, sc: i64, color: i64) -> Vec<Vec<i64>> {
        if image.is_empty() || image[0].is_empty() {
            return image;
        }
        let start = image[sr as usize][sc as usize];
        if start == color {
            return image;
        }
        let mut stack: Vec<(i64, i64)> = vec![(sr, sc)];
        while let Some((row, column)) = stack.pop() {
            if row < 0 || row >= image.len() as i64 {
                continue;
            }
            if column < 0 || column >= image[row as usize].len() as i64 {
                continue;
            }
            if image[row as usize][column as usize] != start {
                continue;
            }
            image[row as usize][column as usize] = color;
            stack.push((row + 1, column));
            stack.push((row - 1, column));
            stack.push((row, column + 1));
            stack.push((row, column - 1));
        }
        image
    }
}
"""

RUST["g-lca-bst"] = r"""
impl Solution {
    pub fn lowest_common_ancestor_bst(root: Vec<Option<i64>>, p: i64, q: i64) -> i64 {
        let mut node = 0usize;
        while node < root.len() {
            match root[node] {
                None => break,
                Some(value) => {
                    if p < value && q < value {
                        node = 2 * node + 1;
                    } else if p > value && q > value {
                        node = 2 * node + 2;
                    } else {
                        return value;
                    }
                }
            }
        }
        -1
    }
}
"""

RUST["g-balanced-binary-tree"] = r"""
impl Solution {
    fn height(tree: &[Option<i64>], node: usize) -> i64 {
        // 0 for an absent subtree and 1 for a leaf, so -1 can mean only
        // "unbalanced" and the empty tree is not mistaken for one.
        if node >= tree.len() || tree[node].is_none() {
            return 0;
        }
        let left = Solution::height(tree, 2 * node + 1);
        let right = Solution::height(tree, 2 * node + 2);
        if left < 0 || right < 0 || (left - right).abs() > 1 {
            return -1;
        }
        if left > right { left + 1 } else { right + 1 }
    }

    pub fn is_balanced(root: Vec<Option<i64>>) -> bool {
        Solution::height(&root, 0) >= 0
    }
}
"""


# ── Grind 75, wave 2 ─────────────────────────────────────────────────────

RUST["g-first-bad-version"] = r"""
impl Solution {
    pub fn first_bad_version(versions: Vec<i64>) -> i64 {
        let (mut low, mut high) = (0i64, versions.len() as i64);
        while low < high {
            let mid = low + (high - low) / 2;
            if versions[mid as usize] == 0 {
                low = mid + 1;
            } else {
                high = mid;
            }
        }
        if low < versions.len() as i64 { low } else { -1 }
    }
}
"""

RUST["g-ransom-note"] = r"""
impl Solution {
    pub fn can_construct_note(magazine: &str, note: &str) -> bool {
        use std::collections::HashMap;
        let mut counts: HashMap<char, i64> = HashMap::new();
        for ch in magazine.chars() {
            *counts.entry(ch).or_insert(0) += 1;
        }
        for ch in note.chars() {
            match counts.get_mut(&ch) {
                Some(left) if *left > 0 => *left -= 1,
                _ => return false,
            }
        }
        true
    }
}
"""

RUST["g-climbing-stairs"] = r"""
impl Solution {
    pub fn climb_stairs(n: i64) -> i64 {
        let (mut previous, mut current) = (1i64, 1i64);
        for _ in 0..n {
            let next = previous + current;
            previous = current;
            current = next;
        }
        previous
    }
}
"""

RUST["g-longest-palindrome"] = r"""
impl Solution {
    pub fn longest_palindrome(s: &str) -> i64 {
        use std::collections::HashMap;
        let mut counts: HashMap<char, i64> = HashMap::new();
        for ch in s.chars() {
            *counts.entry(ch).or_insert(0) += 1;
        }
        let length: i64 = counts.values().map(|&n| n - n % 2).sum();
        if length < s.chars().count() as i64 { length + 1 } else { length }
    }
}
"""

RUST["g-reverse-linked-list"] = r"""
impl Solution {
    pub fn reverse_linked_list(head: Vec<i64>) -> Vec<i64> {
        let mut out: Vec<i64> = Vec::with_capacity(head.len());
        for value in head {
            out.insert(0, value);
        }
        out
    }
}
"""

RUST["g-majority-element"] = r"""
impl Solution {
    pub fn majority_element(nums: Vec<i64>) -> i64 {
        let mut candidate = 0i64;
        let mut count = 0i64;
        for value in nums {
            if count == 0 {
                candidate = value;
            }
            count += if value == candidate { 1 } else { -1 };
        }
        candidate
    }
}
"""

RUST["g-add-binary"] = r"""
impl Solution {
    pub fn add_binary(a: &str, b: &str) -> String {
        let left: Vec<char> = a.chars().collect();
        let right: Vec<char> = b.chars().collect();
        let (mut i, mut j, mut carry) = (left.len() as i64 - 1, right.len() as i64 - 1, 0i64);
        let mut digits: Vec<char> = Vec::new();
        while i >= 0 || j >= 0 || carry != 0 {
            let mut total = carry;
            if i >= 0 {
                total += left[i as usize].to_digit(10).unwrap_or(0) as i64;
                i -= 1;
            }
            if j >= 0 {
                total += right[j as usize].to_digit(10).unwrap_or(0) as i64;
                j -= 1;
            }
            digits.push(char::from_digit((total % 2) as u32, 10).unwrap_or('0'));
            carry = total / 2;
        }
        if digits.is_empty() {
            return "0".to_string();
        }
        digits.reverse();
        digits.into_iter().collect()
    }
}
"""

RUST["g-diameter-binary-tree"] = r"""
impl Solution {
    // `best` travels as an argument rather than living in a cell, because Rust
    // will not let a closure borrow itself. The recursive shape is otherwise
    // the same as the other languages'.
    fn depth(tree: &[Option<i64>], node: usize, best: &mut i64) -> i64 {
        if node >= tree.len() || tree[node].is_none() {
            return 0;
        }
        let left = Solution::depth(tree, 2 * node + 1, best);
        let right = Solution::depth(tree, 2 * node + 2, best);
        if left + right > *best {
            *best = left + right;
        }
        if left > right { left + 1 } else { right + 1 }
    }

    pub fn diameter_of_binary_tree(root: Vec<Option<i64>>) -> i64 {
        let mut best = 0i64;
        Solution::depth(&root, 0, &mut best);
        best
    }
}
"""

RUST["g-middle-linked-list"] = r"""
impl Solution {
    pub fn middle_of_linked_list(head: Vec<i64>) -> i64 {
        if head.is_empty() {
            return -1;
        }
        let (mut slow, mut fast) = (0usize, 0usize);
        while fast + 1 < head.len() {
            slow += 1;
            fast += 2;
        }
        head[slow]
    }
}
"""

RUST["g-maximum-depth-binary-tree"] = r"""
impl Solution {
    fn depth(tree: &[Option<i64>], node: usize) -> i64 {
        if node >= tree.len() || tree[node].is_none() {
            return 0;
        }
        let left = Solution::depth(tree, 2 * node + 1);
        let right = Solution::depth(tree, 2 * node + 2);
        if left > right { left + 1 } else { right + 1 }
    }

    pub fn max_depth_of_binary_tree(root: Vec<Option<i64>>) -> i64 {
        Solution::depth(&root, 0)
    }
}
"""


RUST["g-insert-interval"] = r"""
impl Solution {
    pub fn insert_interval(
        intervals: Vec<Vec<i64>>,
        new_interval: Vec<Vec<i64>>,
    ) -> Vec<Vec<i64>> {
        let mut out: Vec<Vec<i64>> = Vec::new();
        let mut i = 0usize;
        let n = intervals.len();
        let mut start = new_interval[0][0];
        let mut end = new_interval[0][1];
        while i < n && intervals[i][1] < start {
            out.push(intervals[i].clone());
            i += 1;
        }
        while i < n && intervals[i][0] <= end {
            if intervals[i][0] < start { start = intervals[i][0]; }
            if intervals[i][1] > end { end = intervals[i][1]; }
            i += 1;
        }
        out.push(vec![start, end]);
        while i < n {
            out.push(intervals[i].clone());
            i += 1;
        }
        out
    }
}
"""

RUST["g-zero-one-matrix"] = r"""
impl Solution {
    pub fn zero_one_matrix(matrix: Vec<Vec<i64>>) -> Vec<Vec<i64>> {
        if matrix.is_empty() || matrix[0].is_empty() {
            return matrix;
        }
        let rows = matrix.len();
        let columns = matrix[0].len();
        let mut distance: Vec<Vec<i64>> = vec![vec![-1; columns]; rows];
        let mut pending: Vec<(usize, usize)> = Vec::new();
        for row in 0..rows {
            for column in 0..columns {
                if matrix[row][column] == 0 {
                    distance[row][column] = 0;
                    pending.push((row, column));
                }
            }
        }
        let steps: [(i64, i64); 4] = [(1, 0), (-1, 0), (0, 1), (0, -1)];
        let mut head = 0usize;
        while head < pending.len() {
            let (row, column) = pending[head];
            head += 1;
            for (row_step, column_step) in steps {
                let next_row = row as i64 + row_step;
                let next_column = column as i64 + column_step;
                if next_row < 0 || next_row >= rows as i64 {
                    continue;
                }
                if next_column < 0 || next_column >= columns as i64 {
                    continue;
                }
                let (r, c) = (next_row as usize, next_column as usize);
                if distance[r][c] != -1 {
                    continue;
                }
                distance[r][c] = distance[row][column] + 1;
                pending.push((r, c));
            }
        }
        distance
    }
}
"""

RUST["g-k-closest-points"] = r"""
impl Solution {
    pub fn k_closest_points_to_origin(points: Vec<Vec<i64>>, k: i64) -> Vec<Vec<i64>> {
        let mut ordered = points;
        ordered.sort_by(|a, b| {
            let da = a[0] * a[0] + a[1] * a[1];
            let db = b[0] * b[0] + b[1] * b[1];
            da.cmp(&db).then(a[0].cmp(&b[0])).then(a[1].cmp(&b[1]))
        });
        let keep = if k < 0 { 0 } else if k as usize > ordered.len() {
            ordered.len()
        } else {
            k as usize
        };
        ordered.truncate(keep);
        ordered
    }
}
"""

RUST["g-longest-unique-substring"] = r"""
impl Solution {
    pub fn length_of_longest_substring(s: &str) -> i64 {
        // 256 slots rather than a HashMap: the key is a byte, and a byte has
        // a small fixed range, so the table is both faster and clearer here.
        let mut last_seen = [usize::MAX; 256];
        let bytes = s.as_bytes();
        let mut start = 0usize;
        let mut best = 0i64;
        for (index, byte) in bytes.iter().enumerate() {
            let ch = *byte as usize;
            if last_seen[ch] != usize::MAX && last_seen[ch] >= start {
                start = last_seen[ch] + 1;
            }
            last_seen[ch] = index;
            let width = (index - start + 1) as i64;
            if width > best {
                best = width;
            }
        }
        best
    }
}
"""

RUST["g-three-sum"] = r"""
impl Solution {
    pub fn three_sum(nums: Vec<i64>) -> Vec<Vec<i64>> {
        let mut ordered = nums;
        ordered.sort_unstable();
        let size = ordered.len();
        let mut out: Vec<Vec<i64>> = Vec::new();
        for first in 0..size {
            if first > 0 && ordered[first] == ordered[first - 1] {
                continue;
            }
            let mut left = first + 1;
            let mut right = size - 1;
            while left < right {
                let total = ordered[first] + ordered[left] + ordered[right];
                if total < 0 {
                    left += 1;
                } else if total > 0 {
                    right -= 1;
                } else {
                    out.push(vec![ordered[first], ordered[left], ordered[right]]);
                    left += 1;
                    right -= 1;
                    while left <= right && ordered[left] == ordered[left - 1] {
                        left += 1;
                    }
                    while left <= right && ordered[right] == ordered[right + 1] {
                        right -= 1;
                    }
                }
            }
        }
        out
    }
}
"""

RUST["g-level-order-traversal"] = r"""
impl Solution {
    pub fn binary_tree_level_order_traversal(root: Vec<Option<i64>>) -> Vec<Vec<i64>> {
        let mut out: Vec<Vec<i64>> = Vec::new();
        if root.is_empty() {
            return out;
        }
        let mut level: Vec<usize> = vec![0];
        while !level.is_empty() {
            let mut values: Vec<i64> = Vec::new();
            let mut next_level: Vec<usize> = Vec::new();
            for node in level {
                if node >= root.len() || root[node].is_none() {
                    continue;
                }
                values.push(root[node].unwrap());
                next_level.push(2 * node + 1);
                next_level.push(2 * node + 2);
            }
            if values.is_empty() {
                break;
            }
            out.push(values);
            level = next_level;
        }
        out
    }
}
"""

RUST["g-evaluate-rpn"] = r"""
impl Solution {
    pub fn evaluate_reverse_polish_notation(tokens: Vec<String>) -> i64 {
        let mut stack: Vec<i64> = Vec::new();
        for token in tokens {
            if token != "+" && token != "-" && token != "*" && token != "/" {
                stack.push(token.parse::<i64>().unwrap());
                continue;
            }
            let right = stack.pop().unwrap();
            let left = stack.pop().unwrap();
            if token == "+" {
                stack.push(left + right);
            } else if token == "-" {
                stack.push(left - right);
            } else if token == "*" {
                stack.push(left * right);
            } else {
                // Rust's `/` truncates towards zero, which is what the question
                // asks for, so there is no sign handling to do here.
                stack.push(left / right);
            }
        }
        stack[0]
    }
}
"""

RUST["g-course-schedule"] = r"""
impl Solution {
    // `state` and `path` travel as arguments for the same reason `best` does in
    // the tree questions: a closure cannot borrow itself to recurse.
    fn walk(
        start: usize,
        outgoing: &[Vec<usize>],
        state: &mut Vec<i64>,
        path: &mut Vec<(usize, usize)>,
    ) -> bool {
        let mut course = start;
        // Finishing one node is not finishing the search. The path has to unwind
        // all the way back to `start` before this returns true, because every
        // node left behind still marked as in-progress would later look like a
        // cycle when the next branch reaches it.
        while !path.is_empty() {
            let edge = path.last().unwrap().1;
            if edge == outgoing[course].len() {
                state[course] = 2;
                path.pop();
                course = match path.last() {
                    Some((node, _)) => *node,
                    None => break,
                };
                continue;
            }
            path.last_mut().unwrap().1 = edge + 1;
            let next = outgoing[course][edge];
            if state[next] == 1 {
                return false;
            }
            if state[next] == 0 {
                state[next] = 1;
                path.push((next, 0));
                course = next;
            }
        }
        true
    }

    pub fn course_schedule(course_count: i64, prerequisites: Vec<Vec<i64>>) -> bool {
        let count = course_count.max(0) as usize;
        let mut outgoing: Vec<Vec<usize>> = vec![Vec::new(); count];
        for pair in prerequisites {
            let course = pair[0];
            let needed = pair[1];
            if needed < 0 || needed as usize >= count || course < 0 || course as usize >= count {
                continue;
            }
            outgoing[needed as usize].push(course as usize);
        }
        // 0 = not looked at, 1 = on the current path, 2 = finished.
        let mut state: Vec<i64> = vec![0; count];
        for start in 0..count {
            if state[start] != 0 {
                continue;
            }
            let mut path: Vec<(usize, usize)> = vec![(start, 0)];
            state[start] = 1;
            if !Solution::walk(start, &outgoing, &mut state, &mut path) {
                return false;
            }
        }
        true
    }
}
"""

RUST["g-coin-change"] = r"""
impl Solution {
    pub fn coin_change(coins: Vec<i64>, amount: i64) -> i64 {
        if amount < 0 {
            return -1;
        }
        let amount = amount as usize;
        let unreachable = amount as i64 + 1;
        let mut best: Vec<i64> = vec![unreachable; amount + 1];
        best[0] = 0;
        for value in 1..=amount {
            for coin in &coins {
                let coin = *coin;
                if coin >= 1 && coin as usize <= value {
                    let candidate = best[value - coin as usize] + 1;
                    if candidate < best[value] {
                        best[value] = candidate;
                    }
                }
            }
        }
        if best[amount] > amount as i64 { -1 } else { best[amount] }
    }
}
"""

RUST["g-product-except-self"] = r"""
impl Solution {
    pub fn product_of_array_except_self(nums: Vec<i64>) -> Vec<i64> {
        let size = nums.len();
        let mut out: Vec<i64> = vec![1; size];
        let mut running = 1i64;
        for index in 0..size {
            out[index] = running;
            running *= nums[index];
        }
        running = 1;
        for index in (0..size).rev() {
            out[index] *= running;
            running *= nums[index];
        }
        out
    }
}
"""


RUST["g-validate-bst"] = r"""
impl Solution {
    fn walk(tree: &[Option<i64>], node: usize, low: i64, high: i64) -> bool {
        if node >= tree.len() || tree[node].is_none() {
            return true;
        }
        let value = tree[node].unwrap();
        if value <= low || value >= high {
            return false;
        }
        Solution::walk(tree, 2 * node + 1, low, value)
            && Solution::walk(tree, 2 * node + 2, value, high)
    }

    pub fn is_valid_bst(root: Vec<Option<i64>>) -> bool {
        Solution::walk(&root, 0, i64::MIN, i64::MAX)
    }
}
"""

RUST["g-number-of-islands"] = r"""
impl Solution {
    fn sink(grid: &mut Vec<Vec<String>>, row: i64, column: i64, rows: i64, columns: i64) {
        if row < 0 || row >= rows || column < 0 || column >= columns {
            return;
        }
        let here = row as usize;
        let across = column as usize;
        if grid[here][across] != "1" {
            return;
        }
        grid[here][across] = "0".to_string();
        Solution::sink(grid, row + 1, column, rows, columns);
        Solution::sink(grid, row - 1, column, rows, columns);
        Solution::sink(grid, row, column + 1, rows, columns);
        Solution::sink(grid, row, column - 1, rows, columns);
    }

    pub fn number_of_islands(mut grid: Vec<Vec<String>>) -> i64 {
        if grid.is_empty() || grid[0].is_empty() {
            return 0;
        }
        let rows = grid.len() as i64;
        let columns = grid[0].len() as i64;
        let mut islands = 0i64;
        for row in 0..rows {
            for column in 0..columns {
                if grid[row as usize][column as usize] == "1" {
                    islands += 1;
                    Solution::sink(&mut grid, row, column, rows, columns);
                }
            }
        }
        islands
    }
}
"""

RUST["g-rotting-oranges"] = r"""
impl Solution {
    pub fn rotting_oranges(mut grid: Vec<Vec<i64>>) -> i64 {
        let rows = grid.len() as i64;
        let columns = grid[0].len() as i64;
        let mut pending: std::collections::VecDeque<(i64, i64)> =
            std::collections::VecDeque::new();
        let mut fresh = 0i64;
        for row in 0..rows {
            for column in 0..columns {
                let value = grid[row as usize][column as usize];
                if value == 2 {
                    pending.push_back((row, column));
                } else if value == 1 {
                    fresh += 1;
                }
            }
        }
        let steps: [(i64, i64); 4] = [(1, 0), (-1, 0), (0, 1), (0, -1)];
        let mut minutes = 0i64;
        while !pending.is_empty() && fresh > 0 {
            minutes += 1;
            // The level is fixed before any spreading: a cell queued during
            // this minute must not spread until the next one.
            let level = pending.len();
            for _ in 0..level {
                let (row, column) = pending.pop_front().unwrap();
                for (row_step, column_step) in steps {
                    let next_row = row + row_step;
                    let next_column = column + column_step;
                    if next_row < 0 || next_row >= rows || next_column < 0
                        || next_column >= columns
                    {
                        continue;
                    }
                    if grid[next_row as usize][next_column as usize] == 1 {
                        grid[next_row as usize][next_column as usize] = 2;
                        fresh -= 1;
                        pending.push_back((next_row, next_column));
                    }
                }
            }
        }
        if fresh > 0 { -1 } else { minutes }
    }
}
"""

RUST["g-search-rotated"] = r"""
impl Solution {
    pub fn search_in_rotated_sorted_array(nums: Vec<i64>, target: i64) -> i64 {
        let mut low = 0i64;
        let mut high = nums.len() as i64 - 1;
        while low <= high {
            let mid = low + (high - low) / 2;
            if nums[mid as usize] == target {
                return mid;
            }
            if nums[low as usize] <= nums[mid as usize] {
                if nums[low as usize] <= target && target < nums[mid as usize] {
                    high = mid - 1;
                } else {
                    low = mid + 1;
                }
            } else if nums[mid as usize] < target && target <= nums[high as usize] {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        -1
    }
}
"""

RUST["g-combination-sum"] = r"""
impl Solution {
    fn build(
        ordered: &[i64],
        start: usize,
        left: i64,
        current: &mut Vec<i64>,
        out: &mut Vec<Vec<i64>>,
    ) {
        if left == 0 {
            out.push(current.clone());
            return;
        }
        for index in start..ordered.len() {
            if ordered[index] > left {
                break;
            }
            current.push(ordered[index]);
            // The same index again, not the next one: a candidate is reusable.
            Solution::build(ordered, index, left - ordered[index], current, out);
            current.pop();
        }
    }

    pub fn combination_sum(candidates: Vec<i64>, target: i64) -> Vec<Vec<i64>> {
        let mut ordered = candidates;
        ordered.sort_unstable();
        let mut out: Vec<Vec<i64>> = Vec::new();
        let mut current: Vec<i64> = Vec::new();
        Solution::build(&ordered, 0, target, &mut current, &mut out);
        out
    }
}
"""

RUST["g-permutations"] = r"""
impl Solution {
    fn build(current: &mut Vec<i64>, rest: &[i64], out: &mut Vec<Vec<i64>>) {
        if rest.is_empty() {
            out.push(current.clone());
            return;
        }
        for index in 0..rest.len() {
            current.push(rest[index]);
            let next: Vec<i64> = rest
                .iter()
                .enumerate()
                .filter(|(k, _)| *k != index)
                .map(|(_, value)| *value)
                .collect();
            Solution::build(current, &next, out);
            current.pop();
        }
    }

    pub fn permute(nums: Vec<i64>) -> Vec<Vec<i64>> {
        let mut out: Vec<Vec<i64>> = Vec::new();
        let mut current: Vec<i64> = Vec::new();
        Solution::build(&mut current, &nums, &mut out);
        out
    }
}
"""

RUST["g-merge-intervals"] = r"""
impl Solution {
    pub fn merge_intervals(intervals: Vec<Vec<i64>>) -> Vec<Vec<i64>> {
        let mut ordered = intervals;
        ordered.sort();
        let mut out: Vec<Vec<i64>> = Vec::new();
        for interval in ordered {
            match out.last_mut() {
                Some(last) if interval[0] <= last[1] => {
                    if interval[1] > last[1] {
                        last[1] = interval[1];
                    }
                }
                _ => out.push(interval),
            }
        }
        out
    }
}
"""

RUST["g-lca-binary-tree"] = r"""
impl Solution {
    // The general binary tree, not the BST: there is no ordering to steer by,
    // so both branches are searched and the first node whose two subtrees each
    // hold one of the two values is the answer.
    fn find(tree: &[Option<i64>], node: usize, p: i64, q: i64) -> Option<i64> {
        if node >= tree.len() || tree[node].is_none() {
            return None;
        }
        let value = tree[node].unwrap();
        if value == p || value == q {
            return Some(value);
        }
        let left = Solution::find(tree, 2 * node + 1, p, q);
        let right = Solution::find(tree, 2 * node + 2, p, q);
        match (left, right) {
            (Some(_), Some(_)) => Some(value),
            (Some(found), None) => Some(found),
            (None, Some(found)) => Some(found),
            (None, None) => None,
        }
    }

    pub fn lowest_common_ancestor_binary_tree(root: Vec<Option<i64>>, p: i64, q: i64) -> i64 {
        Solution::find(&root, 0, p, q).unwrap_or(-1)
    }
}
"""

RUST["g-accounts-merge"] = r"""
impl Solution {
    pub fn accounts_merge(accounts: Vec<Vec<String>>) -> Vec<Vec<String>> {
        use std::collections::BTreeMap;
        // First sighting of an address decides the name it belongs to.
        let mut owner: BTreeMap<String, String> = BTreeMap::new();
        for row in &accounts {
            for address in row.iter().skip(1) {
                owner.entry(address.clone()).or_insert_with(|| row[0].clone());
            }
        }
        let mut groups: BTreeMap<String, Vec<String>> = BTreeMap::new();
        for (address, name) in owner {
            groups.entry(name).or_default().push(address);
        }
        groups
            .into_iter()
            .map(|(name, mut addresses)| {
                addresses.sort();
                let mut row = vec![name];
                row.extend(addresses);
                row
            })
            .collect()
    }
}
"""

RUST["g-sort-colors"] = r"""
impl Solution {
    pub fn sort_colors(nums: Vec<i64>) -> Vec<i64> {
        let mut out = nums;
        let mut low = 0usize;
        let mut middle = 0usize;
        // usize throughout: `middle` indexes the vector, and comparing it
        // against a signed high is a type error rather than a coercion.
        let mut high = out.len() as isize - 1;
        while (middle as isize) <= high {
            if out[middle] == 0 {
                out.swap(low, middle);
                low += 1;
                middle += 1;
            } else if out[middle] == 2 {
                out.swap(middle, high as usize);
                high -= 1;
                // The middle cursor stays put: whatever was swapped in from the
                // back has not been looked at yet.
            } else {
                middle += 1;
            }
        }
        out
    }
}
"""


# --- Grind 75, wave 5 -------------------------------------------------------
#
# Written against tools/_ref_wave56.py, so the behaviour here is pinned to the
# same file the expectations came from. Two things Rust makes fussier than the
# other four languages below.
#
# String arguments arrive as `&str`, so a character test is a byte compare and
# an index walk is over bytes. Every test case in this wave is ASCII, which is
# what makes the byte arithmetic safe; `chars()` would be the fix for a
# non-ASCII case and would change every index.
#
# A `matrix` return is `Vec<Vec<i64>>` and a `strarray` return is
# `Vec<String>`. Neither is the enum the harness prints through, so a question
# whose contract is a list returns that type directly and the generated main
# calls the matching emitter.

RUST["g-word-break"] = r"""
impl Solution {
    pub fn word_break(str: &str, words: Vec<String>) -> bool {
        let dictionary: std::collections::HashSet<&str> =
            words.iter().map(|w| w.as_str()).collect();
        let n = str.len();
        let mut reach = vec![false; n + 1];
        reach[0] = true;
        for end in 1..=n {
            for start in 0..end {
                // str[start..end] is a byte slice, valid here because every
                // test case is ASCII.
                if reach[start] && dictionary.contains(&str[start..end]) {
                    reach[end] = true;
                    break;
                }
            }
        }
        reach[n]
    }
}
"""

RUST["g-can-partition"] = r"""
impl Solution {
    pub fn can_partition(nums: Vec<i64>) -> bool {
        let total: i64 = nums.iter().sum();
        if total % 2 != 0 {
            return false;
        }
        let half = total / 2;
        let mut possible = vec![false; (half + 1) as usize];
        possible[0] = true;
        for value in &nums {
            if *value > half {
                continue;
            }
            // Descending, or one number pays for itself twice.
            let mut target = half;
            while target >= *value {
                if possible[(target - value) as usize] {
                    possible[target as usize] = true;
                }
                target -= 1;
            }
        }
        possible[half as usize]
    }
}
"""

RUST["g-atoi"] = r"""
impl Solution {
    pub fn atoi(str: &str) -> i64 {
        const INT_MAX: i64 = 2147483647;
        const INT_MIN: i64 = -2147483648;
        let bytes = str.as_bytes();
        let n = bytes.len();
        let mut index = 0usize;
        while index < n && bytes[index] == b' ' {
            index += 1;
        }
        let mut sign: i64 = 1;
        if index < n && (bytes[index] == b'+' || bytes[index] == b'-') {
            if bytes[index] == b'-' {
                sign = -1;
            }
            index += 1;
        }
        // i64, so an eleven digit number does not overflow before the clamp.
        let mut value: i64 = 0;
        let mut digits = 0usize;
        while index < n && bytes[index].is_ascii_digit() {
            value = value * 10 + (bytes[index] - b'0') as i64;
            digits += 1;
            index += 1;
        }
        if digits == 0 {
            return 0;
        }
        (sign * value).clamp(INT_MIN, INT_MAX)
    }
}
"""

RUST["g-spiral-matrix"] = r"""
impl Solution {
    pub fn spiral_matrix(matrix: Vec<Vec<i64>>) -> Vec<i64> {
        let mut out: Vec<i64> = Vec::new();
        if matrix.is_empty() || matrix[0].is_empty() {
            return out;
        }
        // All four bounds are isize, not usize: the right and bottom pointers
        // are each decremented once more than the loop needs, and on a single
        // row or column that passes zero. Unsigned arithmetic wraps round to a
        // huge number there and the next indexing step panics.
        let mut top = 0isize;
        let mut bottom = matrix.len() as isize - 1;
        let mut left = 0isize;
        let mut right = matrix[0].len() as isize - 1;
        while top <= bottom && left <= right {
            for column in left..=right {
                out.push(matrix[top as usize][column as usize]);
            }
            top += 1;
            for row in top..=bottom {
                out.push(matrix[row as usize][right as usize]);
            }
            right -= 1;
            // Only walk the last two sides if there is still a ring to walk.
            if top <= bottom {
                let mut column = right;
                while column >= left {
                    out.push(matrix[bottom as usize][column as usize]);
                    column -= 1;
                }
                bottom -= 1;
            }
            if left <= right {
                let mut row = bottom;
                while row >= top {
                    out.push(matrix[row as usize][left as usize]);
                    row -= 1;
                }
                left += 1;
            }
        }
        out
    }
}
"""

RUST["g-subsets"] = r"""
impl Solution {
    pub fn subsets(nums: Vec<i64>) -> Vec<Vec<i64>> {
        let mut out: Vec<Vec<i64>> = vec![Vec::new()];
        for value in &nums {
            // Snapshot the length: only the subsets that existed before this
            // value are extended.
            let before = out.len();
            for i in 0..before {
                let mut extended = out[i].clone();
                extended.push(*value);
                out.push(extended);
            }
        }
        out
    }
}
"""

RUST["g-right-side-view"] = r"""
impl Solution {
    pub fn right_side_view(root: Vec<Option<i64>>) -> Vec<i64> {
        let mut out: Vec<i64> = Vec::new();
        if root.is_empty() {
            return out;
        }
        let mut level: Vec<usize> = vec![0];
        while !level.is_empty() {
            // Children were appended left first, so the back of the level is
            // the rightmost node of it.
            if let Some(value) = root[level[level.len() - 1]] {
                out.push(value);
            }
            let mut next_level: Vec<usize> = Vec::new();
            for node in &level {
                for child in [2 * node + 1, 2 * node + 2] {
                    if child < root.len() && root[child].is_some() {
                        next_level.push(child);
                    }
                }
            }
            level = next_level;
        }
        out
    }
}
"""

RUST["g-longest-palindromic-substring"] = r"""
impl Solution {
    pub fn longest_palindromic_substring(str: &str) -> String {
        let bytes = str.as_bytes();
        let n = bytes.len();
        let mut best_start = 0usize;
        let mut best_length = 0usize;
        for centre in 0..n {
            // Offset 0 is a one character middle, offset 1 is the gap after
            // it. Missing the second costs every even length palindrome.
            for offset in 0..2usize {
                let mut low = centre as isize;
                let mut high = (centre + offset) as isize;
                while low >= 0 && (high as usize) < n && bytes[low as usize] == bytes[high as usize] {
                    // Strictly greater, so the leftmost of two equals wins.
                    if high as usize - low as usize + 1 > best_length {
                        best_start = low as usize;
                        best_length = high as usize - low as usize + 1;
                    }
                    low -= 1;
                    high += 1;
                }
            }
        }
        str[best_start..best_start + best_length].to_string()
    }
}
"""

RUST["g-unique-paths"] = r"""
impl Solution {
    pub fn unique_paths(rows: i64, columns: i64) -> i64 {
        if rows <= 0 || columns <= 0 {
            return 0;
        }
        let width = columns as usize;
        // One row of running totals; the first row of the grid is all ones.
        let mut row: Vec<i64> = vec![1; width];
        for _ in 1..rows {
            for column in 1..width {
                row[column] += row[column - 1];
            }
        }
        row[width - 1]
    }
}
"""

RUST["g-build-tree"] = r"""
// A struct, not a type alias: a type alias cannot be recursive, and a tree
// whose children are trees is the definition of recursive.
#[derive(Clone)]
struct Node {
    value: i64,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

fn build(preorder: &[i64], inorder: &[i64]) -> Option<Box<Node>> {
    if preorder.is_empty() {
        return None;
    }
    let root = preorder[0];
    let pivot = inorder.iter().position(|&v| v == root).unwrap();
    Some(Box::new(Node {
        value: root,
        left: build(&preorder[1..1 + pivot], &inorder[..pivot]),
        right: build(&preorder[1 + pivot..], &inorder[pivot + 1..]),
    }))
}

fn encode(node: &Option<Box<Node>>, index: usize, out: &mut Vec<Option<i64>>) {
    while out.len() <= index {
        out.push(None);
    }
    if let Some(inner) = node {
        out[index] = Some(inner.value);
        encode(&inner.left, 2 * index + 1, out);
        encode(&inner.right, 2 * index + 2, out);
    }
}

impl Solution {
    pub fn build_tree_from_traversals(preorder: Vec<i64>, inorder: Vec<i64>) -> Vec<Option<i64>> {
        // The first preorder value is the root, and its position in the
        // inorder list is the length of the left subtree -- which is where the
        // preorder list splits as well.
        let root = build(&preorder, &inorder);
        if root.is_none() {
            return Vec::new();
        }
        let mut out: Vec<Option<i64>> = Vec::new();
        encode(&root, 0, &mut out);
        while out.last() == Some(&None) {
            out.pop();
        }
        out
    }
}
"""

RUST["g-letter-combinations"] = r"""
impl Solution {
    pub fn letter_combinations(digits: &str) -> Vec<String> {
        let keys: [(&str, &str); 8] = [
            ("2", "abc"), ("3", "def"), ("4", "ghi"), ("5", "jkl"),
            ("6", "mno"), ("7", "pqrs"), ("8", "tuv"), ("9", "wxyz"),
        ];
        if digits.is_empty() {
            return Vec::new();
        }
        let mut letters: Vec<&str> = Vec::new();
        for digit in digits.chars() {
            match keys.iter().find(|(k, _)| *k == digit.to_string()) {
                Some((_, letters_for_key)) => letters.push(letters_for_key),
                // A digit that is not a key has no combinations at all.
                None => return Vec::new(),
            }
        }
        let mut out: Vec<String> = vec![String::new()];
        for key in letters {
            let mut next: Vec<String> = Vec::new();
            for prefix in &out {
                for letter in key.chars() {
                    next.push(format!("{}{}", prefix, letter));
                }
            }
            out = next;
        }
        out
    }
}
"""

RUST["g-word-search"] = r"""
impl Solution {
    pub fn word_search(board: Vec<Vec<String>>, word: &str) -> bool {
        if word.is_empty() {
            return true;
        }
        if board.is_empty() || board[0].is_empty() {
            return false;
        }
        let rows = board.len();
        let columns = board[0].len();
        let mut letters: Vec<Vec<char>> =
            board.iter().map(|row| row.iter().flat_map(|c| c.chars()).collect()).collect();
        let target: Vec<char> = word.chars().collect();

        // A nested `fn`, not a closure: it recurses, and a closure that calls
        // itself has to name its own type. The step table is passed in rather
        // than captured, because a `fn` item cannot see the enclosing scope.
        fn search(letters: &mut Vec<Vec<char>>, rows: isize, columns: isize,
                  target: &Vec<char>, steps: &[(isize, isize)],
                  row: isize, column: isize, index: usize) -> bool {
            if letters[row as usize][column as usize] != target[index] {
                return false;
            }
            if index == target.len() - 1 {
                return true;
            }
            // A blank is how a cell is marked as used. It is put back on the
            // way out, including out of a branch that succeeded.
            let saved = letters[row as usize][column as usize];
            letters[row as usize][column as usize] = '\0';
            let mut found = false;
            for (row_step, column_step) in steps {
                let next_row = row + *row_step;
                let next_column = column + *column_step;
                if next_row < 0 || next_row >= rows || next_column < 0 || next_column >= columns {
                    continue;
                }
                if letters[next_row as usize][next_column as usize] == '\0' {
                    continue;
                }
                if search(letters, rows, columns, target, steps,
                          next_row, next_column, index + 1) {
                    found = true;
                    break;
                }
            }
            letters[row as usize][column as usize] = saved;
            found
        }

        let steps: [(isize, isize); 4] = [(1, 0), (-1, 0), (0, 1), (0, -1)];
        for row in 0..rows {
            for column in 0..columns {
                if search(&mut letters, rows as isize, columns as isize, &target, &steps,
                          row as isize, column as isize, 0) {
                    return true;
                }
            }
        }
        false
    }
}
"""


# --- Grind 75, wave 6 -------------------------------------------------------
# The end of the list. Three positions are skipped rather than rewritten --
# LRU Cache, Serialize and Deserialize Binary Tree, and Find Median from Data
# Stream all keep state between calls, and a harness that runs one function
# once has nowhere to put it.
#
# Two of these need owned collections rather than borrows, because the search
# mutates what it walks: Min Window Substring counts what it has seen, and Word
# Ladder marks words as visited. `&str` for a string argument still works
# there, since the word list arrives owned.

RUST["g-find-anagrams"] = r"""
impl Solution {
    pub fn find_anagrams(str: &str, pattern: &str) -> Vec<i64> {
        let mut out: Vec<i64> = Vec::new();
        if pattern.is_empty() || pattern.len() > str.len() {
            return out;
        }
        // 26 counters. The window count and the pattern count are equal
        // exactly when the window is an anagram of the pattern.
        let mut need = [0i64; 26];
        let mut window = [0i64; 26];
        for byte in pattern.bytes() {
            need[(byte - b'a') as usize] += 1;
        }
        for byte in str.as_bytes()[..pattern.len()].iter() {
            window[(byte - b'a') as usize] += 1;
        }
        if window == need {
            out.push(0);
        }
        let bytes = str.as_bytes();
        for end in pattern.len()..str.len() {
            window[(bytes[end] - b'a') as usize] += 1;
            window[(bytes[end - pattern.len()] - b'a') as usize] -= 1;
            if window == need {
                out.push((end - pattern.len() + 1) as i64);
            }
        }
        out
    }
}
"""

RUST["g-min-height-trees"] = r"""
impl Solution {
    pub fn min_height_trees(n: i64, edges: Vec<Vec<i64>>) -> Vec<i64> {
        if n <= 0 {
            return Vec::new();
        }
        if n == 1 {
            return vec![0];
        }
        let count = n as usize;
        let mut adjacency: Vec<Vec<usize>> = vec![Vec::new(); count];
        for edge in &edges {
            adjacency[edge[0] as usize].push(edge[1] as usize);
            adjacency[edge[1] as usize].push(edge[0] as usize);
        }
        let mut degree: Vec<i32> = adjacency.iter().map(|row| row.len() as i32).collect();
        let mut leaves: std::collections::VecDeque<usize> = std::collections::VecDeque::new();
        for node in 0..count {
            if degree[node] == 1 {
                leaves.push_back(node);
            }
        }
        let mut remaining = n;
        while remaining > 2 {
            // The level size is read before the round is peeled. A node that
            // drops to one degree during this round belongs to the next one.
            let level = leaves.len();
            remaining -= level as i64;
            for _ in 0..level {
                let leaf = leaves.pop_front().unwrap();
                for neighbour in &adjacency[leaf] {
                    degree[*neighbour] -= 1;
                    if degree[*neighbour] == 1 {
                        leaves.push_back(*neighbour);
                    }
                }
            }
        }
        let mut out: Vec<i64> = leaves.into_iter().map(|node| node as i64).collect();
        out.sort_unstable();
        out
    }
}
"""

RUST["g-task-scheduler"] = r"""
impl Solution {
    pub fn task_scheduler(tasks: Vec<String>) -> i64 {
        if tasks.is_empty() {
            return 0;
        }
        let mut counts: std::collections::HashMap<&str, i64> = std::collections::HashMap::new();
        for task in &tasks {
            *counts.entry(task.as_str()).or_insert(0) += 1;
        }
        let mut most = 0i64;
        let mut kinds = 0i64;
        for count in counts.values() {
            if *count > most {
                most = *count;
                kinds = 1;
            } else if *count == most {
                kinds += 1;
            }
        }
        // The most common task's runs sit `most - 1` rounds of `kinds` slots
        // apart, plus a final round to place the last run of each.
        let forced = (most - 1) * (kinds + 1) + kinds;
        // Never shorter than just running the tasks.
        tasks.len().max(forced as usize) as i64
    }
}
"""

RUST["g-kth-smallest"] = r"""
impl Solution {
    pub fn kth_smallest(root: Vec<Option<i64>>, k: i64) -> i64 {
        if k < 1 {
            return -1;
        }
        // The stack holds the left spine. When it runs out the top is the next
        // value in in-order, and the walk steps into that node's right subtree.
        let mut stack: Vec<usize> = Vec::new();
        let mut node: usize = 0;
        let mut remaining = k;
        loop {
            while node < root.len() && root[node].is_some() {
                stack.push(node);
                node = 2 * node + 1;
            }
            let top = match stack.pop() {
                Some(top) => top,
                None => return -1,
            };
            remaining -= 1;
            if remaining == 0 {
                return root[top].unwrap();
            }
            node = 2 * top + 2;
        }
    }
}
"""

RUST["g-min-window-substring"] = r"""
impl Solution {
    pub fn min_window_substring(str: &str, target: &str) -> String {
        if target.is_empty() || target.len() > str.len() {
            return String::new();
        }
        let mut need: std::collections::HashMap<char, usize> = std::collections::HashMap::new();
        for letter in target.chars() {
            *need.entry(letter).or_insert(0) += 1;
        }
        // missing counts the distinct characters still short of their target
        // count. The window is valid exactly when it reaches zero.
        let mut missing = need.len();
        let mut have: std::collections::HashMap<char, usize> = std::collections::HashMap::new();
        let letters: Vec<char> = str.chars().collect();
        let mut best: Option<(usize, usize)> = None;
        let mut left = 0usize;
        for right in 0..letters.len() {
            let letter = letters[right];
            let count = have.entry(letter).or_insert(0);
            *count += 1;
            if *count == *need.get(&letter).unwrap_or(&0) {
                missing -= 1;
            }
            while missing == 0 {
                let length = right - left + 1;
                if best.is_none() || length < best.unwrap().1 - best.unwrap().0 + 1 {
                    best = Some((left, right));
                }
                let leaving = letters[left];
                let entry = have.entry(leaving).or_insert(0);
                if *entry > 0 {
                    *entry -= 1;
                }
                // Only a count dropping *below* its target invalidates.
                if *have.get(&leaving).unwrap_or(&0) < *need.get(&leaving).unwrap_or(&0) {
                    missing += 1;
                }
                left += 1;
            }
        }
        match best {
            Some((start, end)) => letters[start..=end].iter().collect(),
            None => String::new(),
        }
    }
}
"""

RUST["g-ladder-length"] = r"""
impl Solution {
    pub fn ladder_length(begin: &str, end: &str, words: Vec<String>) -> i64 {
        if begin == end {
            return 1;
        }
        let allowed: std::collections::HashSet<&str> =
            words.iter().map(|w| w.as_str()).collect();
        // Every word on the ladder has to be in the list, the end one too.
        if !allowed.contains(end) {
            return 0;
        }
        let letters: Vec<char> = "abcdefghijklmnopqrstuvwxyz".chars().collect();
        let mut frontier: std::collections::HashSet<String> = std::collections::HashSet::new();
        frontier.insert(begin.to_string());
        let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();
        seen.insert(begin.to_string());
        let mut steps = 1i64;
        while !frontier.is_empty() {
            steps += 1;
            let mut next: std::collections::HashSet<String> = std::collections::HashSet::new();
            for word in &frontier {
                let chars: Vec<char> = word.chars().collect();
                for index in 0..chars.len() {
                    for letter in &letters {
                        if *letter == chars[index] {
                            continue;
                        }
                        // Generated rather than looked up: a fixed amount of
                        // work per word instead of a comparison against all.
                        let mut candidate: String = chars[..index].iter().collect();
                        candidate.push(*letter);
                        candidate.extend(&chars[index + 1..]);
                        if candidate == end {
                            return steps;
                        }
                        if allowed.contains(candidate.as_str()) && !seen.contains(&candidate) {
                            seen.insert(candidate.clone());
                            next.insert(candidate);
                        }
                    }
                }
            }
            frontier = next;
        }
        0
    }
}
"""

RUST["g-basic-calculator"] = r"""
impl Solution {
    pub fn calculate(str: &str) -> i64 {
        // i64, so a run of digits cannot overflow before the end.
        let mut total: i64 = 0;
        let mut sign: i64 = 1;
        let mut number: i64 = 0;
        let mut have_digit = false;
        let mut stack: Vec<(i64, i64)> = Vec::new();
        for character in str.chars() {
            if character.is_ascii_digit() {
                number = number * 10 + (character as i64 - '0' as i64);
                have_digit = true;
            } else if character == '+' || character == '-' {
                if have_digit {
                    total += sign * number;
                }
                number = 0;
                have_digit = false;
                // A minus with no number in front of it just sets the sign.
                sign = if character == '+' { 1 } else { -1 };
            } else if character == '(' {
                // Save what is outside the group; the group starts from zero.
                stack.push((total, sign));
                total = 0;
                sign = 1;
            } else if character == ')' {
                if have_digit {
                    total += sign * number;
                }
                number = 0;
                have_digit = false;
                let (outer_total, outer_sign) = stack.pop().unwrap();
                total = outer_total + outer_sign * total;
                sign = 1;
            }
        }
        if have_digit {
            total += sign * number;
        }
        total
    }
}
"""

RUST["g-max-profit-jobs"] = r"""
impl Solution {
    pub fn max_profit_in_job_scheduling(start_time: Vec<i64>, end_time: Vec<i64>,
                                       profit: Vec<i64>) -> i64 {
        let mut jobs: Vec<(i64, i64, i64)> = Vec::new();
        for i in 0..start_time.len() {
            jobs.push((start_time[i], end_time[i], profit[i]));
        }
        jobs.sort_unstable();
        // best[i] is the most profit from the first i jobs in end-time order.
        let mut best = vec![0i64; jobs.len() + 1];
        for i in 0..jobs.len() {
            let mut earlier = 0usize;
            for j in 0..jobs.len() {
                if jobs[j].0 > jobs[i].0 {
                    break;
                }
                // <= not <: a job may start the moment the previous one ends.
                if jobs[j].1 <= jobs[i].0 {
                    earlier = earlier.max(j + 1);
                }
            }
            best[i + 1] = best[i].max(best[earlier] + jobs[i].2);
        }
        best[jobs.len()]
    }
}
"""

RUST["g-merge-k-sorted"] = r"""
impl Solution {
    pub fn merge_k_sorted(lists: Vec<Vec<i64>>) -> Vec<i64> {
        // A heap of the current head of each row. The row index travels with
        // the value so two equal values from different rows still order.
        let mut heap: std::collections::BinaryHeap<std::cmp::Reverse<(i64, usize, usize)>> =
            std::collections::BinaryHeap::new();
        for (index, row) in lists.iter().enumerate() {
            if let Some(first) = row.first() {
                heap.push(std::cmp::Reverse((*first, index, 0usize)));
            }
        }
        let mut out: Vec<i64> = Vec::new();
        while let Some(std::cmp::Reverse((value, index, position))) = heap.pop() {
            out.push(value);
            let next = position + 1;
            if next < lists[index].len() {
                heap.push(std::cmp::Reverse((lists[index][next], index, next)));
            }
        }
        out
    }
}
"""

RUST["g-largest-rectangle"] = r"""
impl Solution {
    pub fn largest_rectangle(heights: Vec<i64>) -> i64 {
        let mut best = 0i64;
        // Indices whose heights are in increasing order. A shorter bar arriving
        // pops every taller one, which is how each bar learns how far it
        // reaches.
        let mut stack: Vec<usize> = Vec::new();
        for index in 0..=heights.len() {
            // A bar of zero past the end finishes off whatever is left.
            let current = if index < heights.len() { heights[index] } else { 0 };
            while let Some(&top) = stack.last() {
                if heights[top] < current {
                    break;
                }
                stack.pop();
                let height = heights[top];
                let left = stack.last().map(|&i| i as i64).unwrap_or(-1);
                // Width runs from just past the new top to this index.
                best = best.max(height * (index as i64 - left - 1));
            }
            stack.push(index);
        }
        best
    }
}
"""


def attach(questions):
    """Fill in the Rust solution for every question in `questions`.

    Both builders call this on the merged catalogue, which is the only place
    that knows the full set of ids. A question with no entry here raises
    rather than shipping with four languages and a hole in the fifth.
    """
    for question in questions:
        source = RUST.get(question["id"])
        if source is None:
            raise SystemExit(f"no Rust solution for {question['id']!r}")
        question.setdefault("solution", {})["rust"] = source.strip() + "\n"
    return questions
