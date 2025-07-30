from pathlib import Path
import json
import yaml
import toml
import cv_model as cv

DATA_FOLDER = Path(__file__).parent / "data_files"


def test_valid_resume_model():
    """Test the Resume model with valid data."""
    with open(DATA_FOLDER / "valid_resume.json", "r", encoding="utf-8") as f:
        content = f.read()

    cv.Resume.model_validate_json(content)


def test_render_json(tmp_path: Path):
    """Test the rendering of a JSON resume."""
    cv.generate(
        DATA_FOLDER / "example_resume.json", tmp_path / "json_output.pdf", "fantastic-cv"
    )
    assert (tmp_path / "json_output.pdf").exists()


def test_render_yaml(tmp_path: Path):
    """Test the rendering of a YAML resume."""
    cv.generate(
        DATA_FOLDER / "example_resume.yaml", tmp_path / "yaml_output.pdf", "fantastic-cv"
    )
    assert (tmp_path / "yaml_output.pdf").exists()


def test_render_toml(tmp_path: Path):
    """Test the rendering of a TOML resume."""
    cv.generate(
        DATA_FOLDER / "example_resume.toml", tmp_path / "toml_output.pdf", "fantastic-cv"
    )
    assert (tmp_path / "toml_output.pdf").exists()


def test_load_json():
    """Test loading a json resume."""
    loaded = cv.Resume.load(cv.get_default_resume().model_dump_json(indent=2, by_alias=True))
    assert loaded == cv.get_default_resume()


def test_load_yaml(tmp_path: Path):
    """Test loading a yaml resume."""
    path = tmp_path / "resume.yaml"
    with open(path, "w", encoding="utf-8") as f:
        model_py = cv.get_default_resume().model_dump()
        yaml.dump(model_py, f, indent=2, sort_keys=False)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    loaded = cv.Resume.load(content)
    assert loaded == cv.get_default_resume()


def test_load_toml():
    """Test loading a toml resume."""
    model_py = cv.get_default_resume().model_dump()
    toml_content = toml.dumps(model_py)
    loaded = cv.Resume.load(toml_content)
    assert loaded == cv.get_default_resume()


def test_dump_json(tmp_path: Path):
    """Test the JSON dump of the Resume model."""
    cv.dump_empty_json(tmp_path / "empty_resume.json")
    assert (tmp_path / "empty_resume.json").exists()


def test_dump_yaml(tmp_path: Path):
    """Test the YAML dump of the Resume model."""
    cv.dump_empty_yaml(tmp_path / "empty_resume.yaml")
    assert (tmp_path / "empty_resume.yaml").exists()


def test_dump_toml(tmp_path: Path):
    """Test the TOML dump of the Resume model."""
    cv.dump_empty_toml(tmp_path / "empty_resume.toml")
    assert (tmp_path / "empty_resume.toml").exists()
