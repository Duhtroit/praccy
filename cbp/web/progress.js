/* Progression: what solving a question is worth, and what the totals buy.
 *
 * The rules live here, apart from the DOM, because they are the part with an
 * opinion in it and the part most likely to be argued with. Everything is a
 * pure function of the state you pass in, so the numbers can be checked without
 * rendering anything.
 *
 * Two things this deliberately does not do. It does not decay XP, because
 * losing points for taking a day off turns a practice tool into a debt. And it
 * does not rank you against anyone, because the only comparison worth making
 * is with your own last month.
 */

const TIERS = ["easy", "medium", "hard"];

/* Points for a first-time solve. A hard question is worth about three times an
 * easy one, which is roughly how much longer it takes to get right the first
 * time. */
const TIER_POINTS = { easy: 10, medium: 25, hard: 50 };

/* Repeating a question you have already solved is worth something, but much
 * less, and a personal best is worth a little more than a repeat. */
const REPEAT_POINTS = 4;
const NEW_BEST_BONUS = 6;

/* The curve is quadratic, so early levels arrive quickly and later ones do
 * not. Level n needs 40 * n^2 points; the total for reaching level n is
 * 40 * (n-1) * n * (2n-1) / 6, which is what `levelFloor` inverts. */
const LEVEL_BASE = 40;

function pointsForSolve(tier, wasSolved, isNewBest) {
  const base = wasSolved ? REPEAT_POINTS : (TIER_POINTS[tier] || TIER_POINTS.easy);
  return base + (isNewBest ? NEW_BEST_BONUS : 0);
}

/* Total XP needed to have reached `level`. Level 1 starts at 0. */
function levelFloor(level) {
  const n = level - 1;
  return (LEVEL_BASE * n * (2 * n + 1)) / 3;
}

/* The level a given XP total lands on. Walk up rather than solving a quadratic
 * in floating point: the totals are small and the loop is not the bottleneck. */
function levelForXp(xp) {
  let level = 1;
  while (levelFloor(level + 1) <= xp) level += 1;
  return level;
}

/* How far through the current level you are, 0 to 1. */
function levelProgress(xp) {
  const level = levelForXp(xp);
  const base = levelFloor(level);
  const next = levelFloor(level + 1);
  return { level, into: xp - base, span: next - base, ratio: (xp - base) / (next - base) };
}

/* Names for the levels. Deliberately short and a bit dry; the reward is the
 * number moving, not the label. */
const LEVEL_TITLES = [
  "Starting out",
  "Getting the hang of it",
  "Comfortable",
  "Quick with the easy ones",
  "Seeing the pattern",
  "Reliable",
  "Fast and accurate",
  "Hard problems no longer scare you",
  "Sharp",
  "Genuinely strong",
  "Interview ready",
];

function levelTitle(level) {
  return LEVEL_TITLES[Math.min(level, LEVEL_TITLES.length) - 1] || LEVEL_TITLES[LEVEL_TITLES.length - 1];
}

/* Achievements -- which the interface calls trophies, because that is what
 * they look like and "trophy" is a word nobody has to decode. The model keeps
 * the older name: the ids below have been written into localStorage since the
 * first version, and a rename would cost every earned trophy to buy nothing
 * a comment cannot fix.
 *
 * Each is checked against the whole progress state, so they are order-
 * independent and cannot be double-counted. */
const ACHIEVEMENTS = [
  { id: "first-blood", name: "First one", hint: "Solve a question",
    test: (p) => p.solved >= 1 },
  { id: "ten", name: "Ten down", hint: "Solve 10 questions",
    test: (p) => p.solved >= 10 },
  { id: "fifty", name: "Fifty down", hint: "Solve 50 questions",
    test: (p) => p.solved >= 50 },
  { id: "hundred", name: "A hundred", hint: "Solve 100 questions",
    test: (p) => p.solved >= 100 },
  { id: "all-easy", name: "Easy does it", hint: "Solve every easy question",
    test: (p) => p.byTier.easy >= p.totalByTier.easy && p.totalByTier.easy > 0 },
  { id: "first-hard", name: "Bitten", hint: "Solve a hard question",
    test: (p) => p.byTier.hard >= 1 },
  { id: "ten-hard", name: "Harder", hint: "Solve 10 hard questions",
    test: (p) => p.byTier.hard >= 10 },
  { id: "all-hard", name: "The hard wall", hint: "Solve every hard question",
    test: (p) => p.byTier.hard >= p.totalByTier.hard && p.totalByTier.hard > 0 },
  { id: "sweep", name: "Sweep", hint: "Solve one question in every tier and both sources",
    test: (p) => TIERS.every((t) => p.byTier[t] >= 1) &&
                    p.bySource.Coderbyte >= 1 && p.bySource.LeetCode >= 1 },
  { id: "leetcode-only", name: "Across the pond", hint: "Solve 20 LeetCode questions",
    test: (p) => p.bySource.LeetCode >= 20 },
  { id: "coderbyte-all", name: "Coderbyte clean", hint: "Solve all 72 Coderbyte questions",
    test: (p) => p.bySource.Coderbyte >= p.totalBySource.Coderbyte && p.totalBySource.Coderbyte > 0 },
  { id: "week", name: "A week of this", hint: "Solve something on 7 different days",
    test: (p) => p.days >= 7 },
  { id: "speed", name: "Quick", hint: "Solve a question in under a minute",
    test: (p) => p.fastest > 0 && p.fastest < 60 },
  // The id is left over from an earlier idea for this one. What it tests has
  // always been the count, so the name and the hint now say that instead of
  // promising something the test does not measure.
  { id: "clean-sweep", name: "Twenty-five down", hint: "Solve 25 questions",
    test: (p) => p.solved >= 25 },

  /* The level trophies, and the reason they exist: XP used to move a number in
   * the header and nothing else, so the level was a scoreboard nobody was
   * keeping. These attach the points to something you can point at. The name
   * is the level's own title, so reaching level 6 does not hand you a badge
   * and a separate word for it. */
  { id: "level-3", name: levelTitle(3), hint: "Reach level 3",
    test: (p) => p.level >= 3 },
  { id: "level-6", name: levelTitle(6), hint: "Reach level 6",
    test: (p) => p.level >= 6 },
  { id: "level-10", name: levelTitle(10), hint: "Reach level 10",
    test: (p) => p.level >= 10 },
];

/* Everything an achievement might want to know about, derived once so the
 * tests above stay one line each. */
function progressFacts(state, questions) {
  const byTier = { easy: 0, medium: 0, hard: 0 };
  const bySource = { Coderbyte: 0, LeetCode: 0 };
  const totalByTier = { easy: 0, medium: 0, hard: 0 };
  const totalBySource = { Coderbyte: 0, LeetCode: 0 };
  let fastest = Infinity;

  for (const question of questions) {
    totalByTier[question.tier] = (totalByTier[question.tier] || 0) + 1;
    const source = question.source || "Coderbyte";
    totalBySource[source] = (totalBySource[source] || 0) + 1;
    if (!state.solved.has(question.id)) continue;
    byTier[question.tier] = (byTier[question.tier] || 0) + 1;
    bySource[source] = (bySource[source] || 0) + 1;
    const best = state.best[question.id];
    if (best > 0 && best < fastest) fastest = best;
  }

  const xp = state.xp || 0;
  return {
    solved: state.solved.size,
    xp,
    level: levelForXp(xp),
    days: (state.days || []).length,
    fastest: fastest === Infinity ? 0 : fastest,
    byTier,
    bySource,
    totalByTier,
    totalBySource,
  };
}

/* What a solve earned: points, the level change if any, and any achievement
 * that just came due. Returns the deltas so the caller can animate them and
 * persist the achievement ids. */
function rewardForSolve(state, questions, question, outcome) {
  const points = pointsForSolve(question.tier, outcome.wasSolved, outcome.isNewBest);
  const before = levelForXp(state.xp || 0);
  const facts = progressFacts(state, questions);
  const unlocked = ACHIEVEMENTS.filter(
    (a) => !state.achievements.includes(a.id) && a.test(facts)
  );

  return { points, unlocked, levelBefore: before, levelAfter: levelForXp((state.xp || 0) + points) };
}
