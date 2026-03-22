import pytest
import yaml
import tempfile
import os
from src.tools.rules_tool import validate_rules

@pytest.fixture
def yaml_with_rules_key():
    content = """
    rules:
      patient_id:
        - must_be_unique: true
      age:
        - range: [0, 120]
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
    tmp.write(content.encode("utf-8"))
    tmp.close()
    yield tmp.name
    os.remove(tmp.name)

@pytest.fixture
def yaml_root_rules():
    content = """
    patient_id:
      - must_be_unique: true
    age:
      - range: [0, 120]
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
    tmp.write(content.encode("utf-8"))
    tmp.close()
    yield tmp.name
    os.remove(tmp.name)

def test_validate_rules_with_rules_key(yaml_with_rules_key):
    llm_analysis = {"recommendations": ["Cap age at 100"]}
    merged = validate_rules(llm_analysis, rules_file=yaml_with_rules_key)

    assert "baseline_rules" in merged
    assert "llm_recommendations" in merged
    assert "patient_id" in merged["baseline_rules"]
    assert merged["llm_recommendations"] == ["Cap age at 100"]

def test_validate_rules_with_root_rules(yaml_root_rules):
    llm_analysis = {"recommendations": ["Normalize date format"]}
    merged = validate_rules(llm_analysis, rules_file=yaml_root_rules)

    assert "baseline_rules" in merged
    assert "llm_recommendations" in merged
    assert "age" in merged["baseline_rules"]
    assert merged["llm_recommendations"] == ["Normalize date format"]