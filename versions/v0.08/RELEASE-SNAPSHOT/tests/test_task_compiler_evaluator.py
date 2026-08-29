from pathlib import Path
from spec_creator.task_compiler_evaluator import evaluate_v008_corpus

ROOT=Path(__file__).resolve().parents[1]

def test_frozen_task_compiler_corpus():
    r=evaluate_v008_corpus(ROOT)
    assert all(r['hash_checks'].values())
    m=r['metrics']
    assert m['accepted_task_graph_exact_match_rate']==1.0
    assert m['heldout_task_graph_exact_match_rate']==1.0
    assert m['negative_case_classification_accuracy']==1.0
    assert m['unresolved_decision_escape_count']==0
    assert m['unsafe_parallelization_count']==0
    assert m['oversized_ready_task_count']==0
    assert m['dependency_cycle_escape_count']==0
    assert m['invented_dependency_count']==0
    assert m['execution_stream_exact_match_rate']==1.0
    assert m['invalid_execution_escape_count']==0

def test_evaluator_reports_no_missing_data():
    assert evaluate_v008_corpus(ROOT)['missing_data']==[]
