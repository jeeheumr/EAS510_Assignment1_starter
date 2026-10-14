# EAS 510 - Assignment 1: Digital Forensics Apprentice

A rule-based expert system that matches modified images back to their originals.

This is the **starter repository** for Project 1. Two repositories matter:

| Repository | Role |
|------------|------|
| `delveccj/EAS510_Assignment1_starter` (this repo) | Your **code** lives here. You will fork it, work in your fork, and push your final submission here. |
| `delveccj/EAS510_Assignment1` | The **dataset** (read-only). Clone it for the images; never commit it to your fork. |

## Setup on your Codio box

```bash
# 1. Fork this repo on GitHub, then in your box:
git clone https://github.com/YOUR-USERNAME/EAS510_Assignment1_starter.git
cd EAS510_Assignment1_starter

# 2. Clone the read-only dataset as a sibling folder (images live there):
cd ~/workspace
git clone https://github.com/delveccj/EAS510_Assignment1.git

# 3. Install dependencies:
cd ~/workspace/EAS510_Assignment1_starter
python3 -m pip install -r requirements.txt

# 4. Point this box at YOUR fork (run once):
./setup_git.sh
```

## Repository layout

```
forensics_detective.py   SimpleDetector: register targets + find_best_match
rules.py                 Rule functions (Rule 1: Metadata, Rule 2: Histogram, Rule 3: Template)
test_system.py           Runs the detector over the data folders and writes results_*.txt
scripts/check_output_format.py   Validates a results file against the required format
setup_git.sh, submit.sh  One-time setup + commit/push helper ("backup button")
```

## The task in one paragraph

Implement three interpretable rules (metadata, color histogram, template matching)
that combine into a 0-100 confidence score. Run your system on `modified_images/`
and `random/` and save the full output as `results_v1.txt`. In Phase 2, run on
`hard/`, diagnose a systematic failure, add a **Rule 4**, and save
`results_v1_hard.txt` and `results_v2.txt`. Full instructions are in the Codio guide
and in the assignment PDF in UBLearns.

## Running

```bash
# Phase 1 (easy + random) -> results_v1.txt
python3 test_system.py --modified --random --output results_v1.txt

# Phase 1 on hard cases -> results_v1_hard.txt
python3 test_system.py --hard --output results_v1_hard.txt

# Phase 2 (everything) -> results_v2.txt
python3 test_system.py --modified --hard --random --output results_v2.txt

# Validate any results file against the required format:
python3 scripts/check_output_format.py results_v1.txt
```

The data folders are resolved from a sibling clone of `EAS510_Assignment1`.
If your data is elsewhere, pass `--data-dir /path/to/EAS510_Assignment1`.

## Output format (do not alter)

```
Processing: modified_image_01.jpg
Rule 1 (Metadata): FIRED - Size ratio 0.85 -> 20/30 points
Rule 2 (Histogram): FIRED - Correlation 0.92 -> 25/30 points
Rule 3 (Template): FIRED - Match score 0.76 -> 30/40 points
Final Score: 75/100 -> MATCH to original_03.jpg
```

## Observed weakness in V1: what failed and why

After running v1 on the hard images, noticed that many images involving cropping and resizing were rejected
Rule 3 use template matching at single scale.
It might occur the problem because resizing changes the size of image features even when the image come from same original
original and suspect contain same visual content, one of resized versions might produce higher template matching score

## Design decision for V2: what Rule 4 is and why you chose it

Add Rule 4 using multi-scale template matching instead of replacing Rule 3.

Rule 4 resize suspect image at different scales (0.5, 0.6, 0.7, 0.8, 0.9 and 1.0) and use highest template matching score.

Rule 1 (metadata) = 25
Rule 2 (histogram) = 25
Rule 3 (template matching) = 40
Rule 4 (multi-scale matching) = 10
100

## Effect of the change: accuracy before/after on easy vs hard

V1 hard-image test, the system matched 29 images and rejected 31 out of 60 images.
After Rule 4, tested v2 on 135 images including easy modified images, hard modfied images and unrelated random images. It matched 62 images and rejected 73 images.
Observed that rule 4 produce high similarity score for some cropped and resized images but the additional 10 points were not always enough to change final classification.

## Trade-offs: what new costs or risks did Rule 4 introduce
Multi-scale template matching requires more computation because the system tests six different image scales instead of one.
Visually similar but unrelated images can still produce high similarity score causing false postivies. 
Also has difficulty with rotations and heavily cropped images.


## Threshold experiments 

Test three thresholds: 0.40, 0.70, 0.85

0.4: allow more potential matches when comparing images at different scales.
observed that random_08.jpg an unrelated image was incorrectly matched to original_09

0.85: reduce false positives. successfully rejected random_08.jpg but it also caused two valid modified images to become false negatives

0.70: compare result 0.4 and 0.7 across 135 images, found 28 images had different score but none had different final classification

selected 0.70: provide stricter similarity requirement without reducing number of correctly classified images

experiment showed that changing threshold alone cannot completely solve false positives or improve recognition of heavily cropped images.


## AI assistance
Used ChatGPT to help compare the results of three threshold experiments (0.40, 0.70, 0.85).
ChatGPT helped me created python scripts to identify difference in final scores and classification between the experiments.

When comparing thresholds of 0.40 and 0.85 found that increasing threshold correctly rejected random_08.jpg 
but also caused two valid modfied images (original_02 v6 and original_05 v3) to be rejected.

comparing threshold 0.40 and 0.70. out of 135 images, 28 had different final scores but none had different final classification.

It helped me to understand the trade-off between false positives and false negatives.
reviewed the results and decide to use 0.70 because it maintain the same classification as 0.4 while requiring high similarity score for Rule 4.


## Backup doctrine

Your Codio box can be reset at any time. **Your fork on GitHub is the only safe
copy.** After every milestone run `./submit.sh "describe what you did"`. A box
restart never touches GitHub.

## License

Apache 2.0. See `LICENSE`.
