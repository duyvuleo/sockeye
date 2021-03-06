# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#     http://aws.amazon.com/apache2.0/
# 
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import pytest
import sockeye.bleu

EPSILON = 1e-8

test_cases = [(["this is a test", "another test"], ["ref1", "ref2"], 0.003799178428257963),
              (["this is a test"], ["this is a test"], 1.0),
              (["this is a fest"], ["this is a test"], 0.223606797749979)]

test_case_offset = [("am I am a character sequence", "I am a symbol string sequence a a", 0.1555722182, 0)]

# statistic structure:
# - common counts
# - total counts
# - hyp_count
# - ref_count

test_case_statistics = [("am I am a character sequence", "I am a symbol string sequence a a",
                        sockeye.bleu.Statistics([4, 2, 1, 0], [6, 5, 4, 3]))]

test_case_scoring = [((sockeye.bleu.Statistics([9, 7, 5, 3], [10, 8, 6, 4]), 11, 11), 0.8375922397)]

# testing that right score is returned for null statistics and different offsets
# format: stat, offset, expected score
test_case_degenerate_stats = [((sockeye.bleu.Statistics([0, 0, 0, 0], [4, 4, 2, 1]), 0, 1), 0.0, 0.0),
                              ((sockeye.bleu.Statistics([0, 0, 0, 0], [10, 11, 12, 0]), 14, 10), 0.0, 0.0),
                              ((sockeye.bleu.Statistics([0, 0, 0, 0], [0, 0, 0, 0]), 0, 0), 0.0, 0.0),
                              ((sockeye.bleu.Statistics([6, 5, 4, 0], [6, 5, 4, 3]), 6, 6), 0.0, 0.0),
                              ((sockeye.bleu.Statistics([0, 0, 0, 0], [0, 0, 0, 0]), 0, 0), 0.1, 0.0),
                              ((sockeye.bleu.Statistics([0, 0, 0, 0], [0, 0, 0, 0]), 1, 5), 0.01, 0.0)]


@pytest.mark.parametrize("hypotheses, references, expected_bleu", test_cases)
def test_bleu(hypotheses, references, expected_bleu):
    bleu = sockeye.bleu.corpus_bleu(hypotheses, references)
    assert abs(bleu - expected_bleu) < EPSILON


@pytest.mark.parametrize("hypothesis, reference, expected_stat", test_case_statistics)
def test_statistics(hypothesis, reference, expected_stat):
    stat = sockeye.bleu.bleu_counts(hypothesis, reference)[0]
    assert stat == expected_stat


@pytest.mark.parametrize("statistics, expected_score", test_case_scoring)
def test_scoring(statistics, expected_score):
    score = sockeye.bleu.bleu_from_counts(statistics);
    assert abs(score - expected_score) < EPSILON


@pytest.mark.parametrize("hypothesis, reference, expected_with_offset, expected_without_offset",
                         test_case_offset)
def test_offset(hypothesis, reference, expected_with_offset, expected_without_offset):
    score_without_offset = sockeye.bleu.bleu_from_counts(sockeye.bleu.bleu_counts(hypothesis, reference),
                                                         offset = 0.0)
    print(sockeye.bleu.bleu_counts(hypothesis, reference))
    assert abs(expected_without_offset - score_without_offset) < EPSILON

    score_with_offset = sockeye.bleu.bleu_from_counts(sockeye.bleu.bleu_counts(hypothesis, reference),
                                                      offset = 0.1)
    assert abs(expected_with_offset - score_with_offset) < EPSILON


@pytest.mark.parametrize("statistics, offset, expected_score", test_case_degenerate_stats)
def test_degenerate_statistics(statistics, offset, expected_score):
    score = sockeye.bleu.bleu_from_counts(statistics, offset = offset)
    assert score == expected_score
