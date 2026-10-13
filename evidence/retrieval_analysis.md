### Review of actual hybrid results

All three methods achieve expected-source hit@4 on 3/3 queries, so this metric does not show a hybrid improvement.

- **Residency requirement:** semantic and BM25 both rank `howard_housing.txt@0` first, which contains the requirement and exemption. Semantic then includes two off-campus discussion chunks; BM25 returns four official housing chunks. Hybrid retains three official chunks and one freshman discussion. For this official-policy question, BM25's source precision is better; hybrid reduces the semantic drift but adds an unnecessary student result. All retrieve the key answer.
- **Shuttle frequency:** all three methods return the same four transportation chunks in the same order. They are tied here. The first passage explicitly distinguishes 20–30 minutes from West Campus's approximately 45 minutes.
- **CHS versus Drew:** semantic ranks `student_freshman_dorms.txt@0` first, which directly contrasts Drew recommendations with the newer CHS amenities and dining proximity. BM25 ranks it third, and hybrid second, behind a broader residence-recommendations passage. Semantic is better at putting the direct comparison first in this small example; hybrid does not beat it. The charges result at rank four is less relevant to student experiences.

Hybrid remains the requested application default so its behavior is demonstrable. These results do not justify a claim that hybrid is always superior. A larger held-out question set and passage-level relevance judgments would be needed to tune candidate counts or fusion weights.

### Review of actual chunking results

The 800/150 strategy makes 26 chunks; 400/75 makes 46. Both achieve hit@4 on 3/3 queries. For the policy question, 400/75 ranks `howard_housing.txt@325` first, focusing more narrowly on the residency clause; the larger first chunk includes background application fees too. For the shuttle question, 400/75 starts at offset 325, near the arrival intervals, while 800/150 starts with broader service context. Smaller chunks are more focused for these two factual questions.

For the dorm comparison, 800/150 retrieves `student_freshman_dorms.txt@0` in second place, retaining both Drew disagreement and CHS amenities in one passage. In 400/75, the same file's offset-0 passage is third and ends before the CHS amenities discussion; the top four do not include that file's later CHS passage. Thus 800/150 provides better comparative answer coverage for this query even though source hit@4 cannot detect the difference. The planned 800/150 baseline remains appropriate for this mixed corpus; these results do not show an across-the-board advantage.

### Review of metadata filtering

The official-only and student-only result lists contain only the requested type; the experiment asserts this. Filtering changes the evidence available to generation rather than merely changing a display label. Official-only housing questions can avoid anecdotal assignment claims, while student-only dorm comparisons can focus on experiences. A restrictive filter can also remove the only answer-bearing source, so it is not a universal quality improvement.
