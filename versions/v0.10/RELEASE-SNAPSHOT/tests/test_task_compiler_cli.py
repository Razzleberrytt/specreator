import json
from pathlib import Path
from spec_creator.cli import main

ROOT=Path(__file__).resolve().parents[1]
CASES=[json.loads(x) for x in (ROOT/'fixtures/task-compiler/v0.08/corpus.jsonl').read_text().splitlines() if x.strip()]

def test_task_compiler_cli(tmp_path, capsys):
    c=next(c for c in CASES if c['expected']['status']=='compiled')
    p=tmp_path/'project.json'; p.write_text(json.dumps(c['project']))
    assert main(['task-compile',str(p),'--json'])==0
    out=json.loads(capsys.readouterr().out)
    assert out==c['expected']

def test_task_compiler_cli_nonzero_for_blocker(tmp_path, capsys):
    c=next(c for c in CASES if c['category']=='owner_blocker')
    p=tmp_path/'project.json'; p.write_text(json.dumps(c['project']))
    assert main(['task-compile',str(p),'--json'])==1
    out=json.loads(capsys.readouterr().out)
    assert out['status']=='blocked'

def test_task_graph_validate_cli(tmp_path, capsys):
    c=next(c for c in CASES if c['expected']['status']=='compiled')
    p=tmp_path/'graph.json'; p.write_text(json.dumps(c['expected']))
    assert main(['task-graph-validate',str(p),'--json'])==0
    assert json.loads(capsys.readouterr().out)['ok'] is True

def test_task_compiler_evaluator_cli(capsys):
    assert main(['evaluate-task-compiler-corpus',str(ROOT),'--json'])==0
    out=json.loads(capsys.readouterr().out)
    assert out['metrics']['accepted_task_graph_exact_match_rate']==1.0
