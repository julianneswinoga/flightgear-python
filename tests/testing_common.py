import os
from pathlib import Path


supported_fdm_versions = [
    None,  # Auto-version
    24,
    25,
]
supported_ctrls_versions = [
    None,  # Auto-version
    27,
]
supported_gui_versions = [
    None,  # Auto-version
    8,
]


project_dir = os.path.abspath(os.path.dirname(__file__))


def fill_xml_template(template_relative_path: str, **kwargs) -> str:
    template_full_path = Path(project_dir, template_relative_path).resolve()
    with open(template_full_path, 'r') as xml_fp:
        xml_template_str = xml_fp.read()
    xml_filled = xml_template_str.format(**kwargs)
    return xml_filled


def m_to_ft(val_m: float) -> float:
    return val_m * 3.28084
