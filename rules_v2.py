"""EAS 510 - Project 1 - Phase 2: the V2 rule set.

Rules 1-3 are kept exactly as in `rules.py`. Your job is to ADD Rule 4 that
targets the systematic weakness you diagnosed from results_v1_hard.txt.

<rules.py>
Rule 1: metadata file size + image dimensions
Rule 2: histogram
Rule 3: template matching 
SimpleDetector sum 3 of the point above 50 match and below 50 rejected

Constraint: the rules' `out_of` weights must still sum to 100 so the Final
Score stays on a /100 scale (the format validator enforces "Final Score:
<s>/100" equals the sum of the block's rule scores).

Example split that keeps the original spirit: Rules 1-3 -> 25/25/40 and
Rule 4 -> 10 (or trim the losers more aggressively).

<rules_v2.py>
Rule 1 = 25
Rule 2 = 25
Rule 3 = 40
Rule 4 = 10
100

"""
 
import cv2
import rules

#: Import the original rules and append your new one.
RULES = ("rule1_metadata_v2", "rule2_histogram_v2", "rule3_template", "rule4_multiscale",)

# V1 failed on cropped/resized images because Rule 3 only performs template matching at one scale.
# Rule 4 tries several scales and keep the best template match

def rule1_metadata_v2(target, input_path):
  out = rules.rule1_metadata(target, input_path)
  out = out.copy()

  out["out_of"] = 25

  if out["fired"]:
    out["score"] = int(round(25*out["metric"]))
  else:
    out["score"] = 0
  return out


def rule2_histogram_v2(target, input_path):
  out = rules.rule2_histogram(target, input_path)
  out = out.copy()

  out["out_of"] = 25

  if out["fired"]:
    out["score"] = int(round(25*out["metric"]))
  else:
    out["score"] = 0
  return out

def rule4_multiscale(target, input_path):
    """TODO: replace with your Phase 2 rule that fixes the V1 weakness.

    Starter returns a no-op so the pipeline still runs before you implement it.
    Parity with rules.py rule dict: rule/name/fired/score/out_of/note/metric.

    multi-scale template matching:
    improve matching for image that were cropped or resized

    v1's single-scale template matching often failed when the suspect image had been resized.
    I wanted to check whether trying different scale could recover similarity.

    """

    out = {
        "rule": 4,
        "name": "Multi-scale",
        "fired": False,
        "score": 0,
        "out_of": 10,
        "note": "match score 0.00",
        "metric": 0.0,
    }

    try:
      # use grayscale image to comapre; image pattern without depending on color information
      src_g = rules._gray(target["path"])
      nd_g = rules._gray(input_path)
      if src_g is None or nd_g is None:
        return out

      # example: scale 0.8 
      # scale = 0.8 

      # v1 only check original image scale
      # decide to try several smaller scales to involve cropping followed by resizing
      scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

      # keep strongest evidence found across
      # all tested scale instead of relying on single result
      best_metric = 0.0
      best_scale = 1.0
      
      for scale in scales:

        # resize suspect image while keep aspect ratio
        new_w = int(nd_g.shape[1] * scale)
        new_h = int(nd_g.shape[0] * scale)
        
        if new_w < 2 or new_h < 2:
          continue
        
        resized = cv2.resize(nd_g, (new_w, new_h))

        # matchTemplate require template to fit inside image being searched
        if (resized.shape[0] > src_g.shape[0] or resized.shape[1] > src_g.shape[1]):
          continue
      
        # compare resized suspect againt the original
        # higher normalized correlation suggest the image share similar visual patterns
        res = cv2.matchTemplate(src_g, resized, cv2.TM_CCOEFF_NORMED)
        metric = float(res.max())

        # save best result across all test scales
        if metric > best_metric:
          best_metric = metric
          best_scale = scale

      # initial threshold to test
      # value need to be evaluated against both hard image and unrelated random images
      # random_08.jpg incorrectly accepted with 53/100

      # threshold = 0.40

      # random_08 image produce multi-metric of 0.82 contributing false positive
      # testing stricter threshold to reduce accidental match
      # reject 45/100

      # threshold = 0.85

      # Used ChatGPT to help write comparison script for the results generated with thresholds 0.40 and 0.85
      # script identified three changed classification
      # - two valid modified images became false negatives.
      # - one related random image was correctly rejected.
      # used these results to understand the trade-off between false positives and false negatives

      # one more test with threshold 0.7
      threshold = 0.7

      out["metric"] = best_metric
      out["note"] = f"match score {best_metric:.2f}"

      # chose relatively small weight
      # new rule should support existing evidence rather than make final decision by itself
      if best_metric >= threshold:
        out["fired"] = True
        out["score"] = int(round(10 * best_metric))

      # chose hard case for debug 
      # crop + resize was one of the weakness observed in v1
      if (input_path.endswith("original_00__crop_keep60__resized__q45__v6.jpg") and target["stem"] == "original_00"):
        print("===rule 4 debug ===")
        print("original shape:", src_g.shape)
        print("suspect shape:", nd_g.shape)
        print("best scale:", best_scale)
        print("best metric:", best_metric)
        print("rule 4 score:", out["score"])
    except cv2.error as e:
      print("rule 4 opencv error:", e)

    return out