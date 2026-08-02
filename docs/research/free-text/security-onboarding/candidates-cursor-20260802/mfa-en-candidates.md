# The Second Factor — en candidate answers

Source: `docs/research/free-text/security-onboarding/mfa-en.md`

## Candidate correct answers

1. **"better than nothing"** — why this should ACCEPT: Canonical; table says "Better than nothing; use it if it's all there is".
2. **"it still stops most attacks"** — why this should ACCEPT: Paraphrase of "it stops most attacks" / "blocks most attackers".
3. **"stops credential stuffing"** — why this should ACCEPT: Accept-list and explanation; scale attacks without targeting you.
4. **"blocks bulk phishing"** — why this should ACCEPT: Same scale-attack idea; partial but correct.
5. **"weak isn't worthless"** — why this should ACCEPT: Meaning from the explanation without accept-list words.
6. **"good enough when it's all that's offered"** — why this should ACCEPT: Casual restatement of the table's SMS row.
7. **"keeps opportunistic attackers out"** — why this should ACCEPT: Formal synonym for stopping scale/non-targeted attackers.
8. **"raises the bar for attackers"** — why this should ACCEPT: Partial restatement; should still count as why enable it. Flag: slightly vague for keyword floor.

## Candidate wrong answers

1. **"it's worthless / don't bother"** — why this should REJECT: Explicit reject; lesson says weakest ≠ worthless.
2. **"disable it"** — why this should REJECT: Reject-list idea.
3. **"because SMS can't be phished"** — why this should REJECT: False; lesson covers SIM swap and relay. Flag: confident-sounding wrong.
4. **"deny push prompts you didn't cause"** — why this should REJECT: Correct MFA-fatigue rule from this lesson, wrong answer to the SMS-why question.
5. **"passkeys are stronger"** — why this should REJECT: True but not why you still enable SMS; answers a different question.
6. **"verify through a second channel"** — why this should REJECT: Targeted-room answer; wrong here.
7. **"SMS is the strongest factor"** — why this should REJECT: Opposite of the table ranking.
8. **"because it's free"** — why this should REJECT: Off-point / nonsensical relative to the lesson.

## Quality assessment

- Question clarity: Clear; "even though weakest" primes the better-than-nothing answer.
- Lesson/question alignment: Good enough. Table SMS row and "Better than nothing" support it; explanation adds credential stuffing / bulk phishing detail.
- Accept-list coverage: Solid. May miss `opportunistic`, `raises the bar`, `if it's all there is` under keyword floor.
- Reject-list false-positive risk: Low; "worthless" / "don't bother" won't appear in a correct answer.
- Explanation consistency: Consistent and slightly richer than the lesson table.

## Suggested refinements

- Add accept: `if it's all there is`, `stops opportunistic attackers`, `weakest is not worthless`.
- No major lesson rewrite needed; optional one sentence in-lesson that SMS still stops scale attacks.
