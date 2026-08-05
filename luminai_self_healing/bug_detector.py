"""Bug Detection Service for LuminAI."""

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class BugSeverity(Enum):
    """Severity levels for bugs."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BugType(Enum):
    """Types of bugs."""

    API_ERROR = "api_error"
    TIMEOUT_ERROR = "timeout_error"
    CONNECTION_ERROR = "connection_error"
    SYNTAX_ERROR = "syntax_error"
    CONFIG_ERROR = "config_error"
    RUNTIME_ERROR = "runtime_error"
    TEST_FAILURE = "test_failure"
    UNKNOWN = "unknown"


@dataclass
class BugReport:
    """Report containing bug information."""

    bug_id: str
    bug_type: BugType
    severity: BugSeverity
    message: str
    file_path: str | None
    line_number: int | None
    stack_trace: str | None
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bug_id": self.bug_id,
            "bug_type": self.bug_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "stack_trace": self.stack_trace,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class BugDetector:
    """Service untuk mendeteksi bug dari berbagai sumber."""

    def __init__(self):
        self.logger = self._setup_logger()
        self._error_patterns = self._compile_error_patterns()

    def _setup_logger(self):
        """Setup basic logger."""
        import structlog
        return structlog.get_logger()

    def _compile_error_patterns(self) -> dict[str, re.Pattern]:
        """Compile regex patterns for error detection."""
        patterns = {
            "api_error": r"(?i)api.*error|perplexity.*error",
            "timeout": r"(?i)timeout|time.*out",
            "connection": r"(?i)connection.*error|connection.*refused",
            "syntax": r"SyntaxError: (.+)",
            "import": r"ImportError: (.+)",
            "type": r"TypeError: (.+)",
            "value": r"ValueError: (.+)",
        }
        return {k: re.compile(v) for k, v in patterns.items()}

    def detect_from_logs(self, log_path: str | Path) -> list[BugReport]:
        """Deteksi bug dari file log."""
        bugs: list[BugReport] = []

        try:
            content = Path(log_path).read_text()
            bugs = self._parse_log_content(content, "log_file")
        except Exception as e:
            self.logger.error(f"Failed to read log file: {e}")

        return bugs

    def detect_from_test_output(self, output: str) -> list[BugReport]:
        """Deteksi bug dari output test."""
        bugs: list[BugReport] = []

        for pattern_name, pattern in self._error_patterns.items():
            for match in pattern.finditer(output):
                bug_type = self._pattern_to_bug_type(pattern_name)
                bugs.append(
                    BugReport(
                        bug_id=self._generate_bug_id(),
                        bug_type=bug_type,
                        severity=self._estimate_severity(bug_type),
                        message=match.group(0),
                        file_path=self._extract_file_path(output),
                        line_number=self._extract_line_from_error(output),
                        stack_trace=None,
                        source="test_output",
                    )
                )

        return bugs

    def _parse_log_content(self, content: str, source: str) -> list[BugReport]:
        """Parse log content untuk mencari error patterns."""
        bugs: list[BugReport] = []

        for pattern_name, pattern in self._error_patterns.items():
            for match in pattern.finditer(content):
                bug_type = self._pattern_to_bug_type(pattern_name)
                bugs.append(
                    BugReport(
                        bug_id=self._generate_bug_id(),
                        bug_type=bug_type,
                        severity=self._estimate_severity(bug_type),
                        message=match.group(0),
                        file_path=None,
                        line_number=None,
                        stack_trace=None,
                        source=source,
                    )
                )

        return bugs

    def _pattern_to_bug_type(self, pattern_name: str) -> BugType:
        """Map pattern name to BugType."""
        mapping = {
            "api_error": BugType.API_ERROR,
            "timeout": BugType.TIMEOUT_ERROR,
            "connection": BugType.CONNECTION_ERROR,
            "syntax": BugType.SYNTAX_ERROR,
            "import": BugType.SYNTAX_ERROR,
            "type": BugType.RUNTIME_ERROR,
            "value": BugType.RUNTIME_ERROR,
        }
        return mapping.get(pattern_name, BugType.UNKNOWN)

    def _estimate_severity(self, bug_type: BugType) -> BugSeverity:
        """Estimate severity based on bug type."""
        severity_map = {
            BugType.API_ERROR: BugSeverity.HIGH,
            BugType.TIMEOUT_ERROR: BugSeverity.MEDIUM,
            BugType.CONNECTION_ERROR: BugSeverity.HIGH,
            BugType.SYNTAX_ERROR: BugSeverity.HIGH,
            BugType.CONFIG_ERROR: BugSeverity.MEDIUM,
            BugType.RUNTIME_ERROR: BugSeverity.MEDIUM,
            BugType.TEST_FAILURE: BugSeverity.MEDIUM,
            BugType.UNKNOWN: BugSeverity.MEDIUM,
        }
        return severity_map.get(bug_type, BugSeverity.MEDIUM)

    def _generate_bug_id(self) -> str:
        """Generate unique bug ID."""
        import uuid
        return f"BUG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

    def _extract_file_path(self, text: str) -> str | None:
        """Extract file path from text."""
        patterns = [r'File "([^"]+)"', r"File '([^']+)'", r'([/\w]+\.py)']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _extract_line_from_error(self, text: str) -> int | None:
        """Extract line number from error message."""
        match = re.search(r"line (\d+)", text)
        return int(match.group(1)) if match else None

    def run_static_analysis(self, file_path: str | Path) -> list[BugReport]:
        """Run static analysis pada file."""
        bugs: list[BugReport] = []

        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                bug = BugReport(
                    bug_id=self._generate_bug_id(),
                    bug_type=BugType.SYNTAX_ERROR,
                    severity=BugSeverity.HIGH,
                    message=result.stderr or "Compilation failed",
                    file_path=str(file_path),
                    line_number=self._extract_line_from_error(result.stderr),
                    stack_trace=result.stderr,
                    source="static_analysis",
                )
                bugs.append(bug)

        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")

        return bugs
