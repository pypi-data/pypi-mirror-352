"""VectorVein API data model definitions"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class VApp:
    """VApp information"""

    app_id: str
    title: str
    description: str
    info: Dict[str, Any]
    images: List[str]


@dataclass
class AccessKey:
    """Access key information"""

    access_key: str
    access_key_type: str  # O: one-time, M: multiple, L: long-term
    use_count: int
    max_use_count: Optional[int]
    max_credits: Optional[int]
    used_credits: int
    v_app: Optional[VApp]
    v_apps: List[VApp]
    records: List[Any]
    status: str  # AC: valid, IN: invalid, EX: expired, US: used
    access_scope: str  # S: single application, M: multiple applications
    description: str
    create_time: str
    expire_time: str
    last_use_time: Optional[str]


@dataclass
class WorkflowInputField:
    """Workflow input field"""

    node_id: str
    field_name: str
    value: Any


@dataclass
class WorkflowOutput:
    """Workflow output result"""

    type: str
    title: str
    value: Any


@dataclass
class WorkflowRunResult:
    """Workflow run result"""

    rid: str
    status: int
    msg: str
    data: List[WorkflowOutput]


@dataclass
class AccessKeyListResponse:
    """Access key list response"""

    access_keys: List[AccessKey]
    total: int
    page_size: int
    page: int
