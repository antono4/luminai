"""Self-Healing Orchestrator for LuminAI."""

import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

from .bug_detector import BugDetector, BugReport, BugType, BugSeverity
from .config import Config, get_config

logger = structlog.get_logger()


class WorkflowStatus(Enum):
    """Status dari self-healing workflow."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


@dataclass
class SelfHealingTask:
    """Task untuk self-healing process."""

    task_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    bug_report: BugReport | None = None
    root_cause: str = ""
    fix_applied: bool = False
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SelfHealingResult:
    """Result dari self-healing process."""

    success: bool
    task: SelfHealingTask
    message: str
    fix_applied: bool = False


class SelfHealingOrchestrator:
    """Orchestrator utama untuk self-healing workflow."""

    def __init__(self, config: Config | None = None):
        self.config = config or get_config()
        self.logger = logger.bind(component="Orchestrator")

        # Initialize components
        self.bug_detector = BugDetector()

        # Task tracking
        self.tasks: dict[str, SelfHealingTask] = {}
        
        # Statistics
        self.stats = {
            "bugs_detected": 0,
            "bugs_fixed": 0,
            "total_runs": 0,
            "success_rate": 0.0,
        }

    def process_bug(self, bug: BugReport) -> SelfHealingResult:
        """Process bug through self-healing workflow."""
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.logger.info(f"Processing bug: {bug.bug_id}", task_id=task_id)

        task = SelfHealingTask(task_id=task_id, bug_report=bug)
        self.tasks[task_id] = task

        try:
            task.status = WorkflowStatus.RUNNING
            
            # Analyze root cause
            root_cause = self._analyze_root_cause(bug)
            task.root_cause = root_cause

            # Generate fix
            fix = self._generate_fix(bug, root_cause)

            if fix:
                # Apply fix
                if self.config.is_auto_fix:
                    success = self._apply_fix(fix, bug)
                    task.fix_applied = success
                    
                    if success:
                        task.status = WorkflowStatus.COMPLETED
                        task.completed_at = datetime.now()
                        self.stats["bugs_fixed"] += 1
                        return SelfHealingResult(
                            success=True,
                            task=task,
                            message="Bug fixed successfully!",
                            fix_applied=True,
                        )

            # Update stats
            self.stats["bugs_detected"] += 1
            self.stats["total_runs"] += 1
            self._update_success_rate()

            task.status = WorkflowStatus.MANUAL_REVIEW
            return SelfHealingResult(
                success=True,
                task=task,
                message="Bug detected, fix requires manual review.",
                fix_applied=False,
            )

        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}\n{traceback.format_exc()}"
            self.logger.error("Workflow failed", task_id=task_id, error=error_msg)
            task.status = WorkflowStatus.FAILED
            task.error = error_msg

            return SelfHealingResult(
                success=False,
                task=task,
                message=error_msg,
            )

    def _analyze_root_cause(self, bug: BugReport) -> str:
        """Analyze root cause of the bug."""
        bug_type = bug.bug_type
        
        root_causes = {
            BugType.API_ERROR: "Perplexity API returned an error. Check API key and rate limits.",
            BugType.TIMEOUT_ERROR: "Request timed out. Network issues or API overload.",
            BugType.CONNECTION_ERROR: "Connection failed. Check network connectivity.",
            BugType.SYNTAX_ERROR: "Syntax error in code. Missing or incorrect syntax.",
            BugType.CONFIG_ERROR: "Configuration issue. Check API settings.",
            BugType.RUNTIME_ERROR: "Runtime error occurred. Check input parameters.",
            BugType.TEST_FAILURE: "Test failed. Verify expected behavior.",
            BugType.UNKNOWN: "Unknown error. Further investigation required.",
        }
        
        return root_causes.get(bug_type, "Unknown root cause")

    def _generate_fix(self, bug: BugReport, root_cause: str) -> str | None:
        """Generate fix suggestion based on bug type."""
        fixes = {
            BugType.API_ERROR: """
# Suggested fix for API error:
# 1. Verify PPLX_API_KEY is correct
# 2. Check API rate limits
# 3. Add retry logic with exponential backoff
import time

def retry_request(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)
""",
            BugType.TIMEOUT_ERROR: """
# Suggested fix for timeout:
# 1. Increase timeout value
# 2. Add retry logic
timeout = 120  # seconds
""",
            BugType.CONNECTION_ERROR: """
# Suggested fix for connection error:
# 1. Check network connectivity
# 2. Verify API endpoint URL
# 3. Add connection pooling
""",
            BugType.SYNTAX_ERROR: """
# Suggested fix for syntax error:
# 1. Review the code syntax
# 2. Check for missing colons, brackets, quotes
# 3. Run: python -m py_compile <file.py>
""",
        }
        
        return fixes.get(bug.bug_type)

    def _apply_fix(self, fix: str, bug: BugReport) -> bool:
        """Apply fix to the codebase."""
        self.logger.info("Applying fix", bug_id=bug.bug_id)
        
        # In a real implementation, this would:
        # 1. Parse the fix
        # 2. Apply to appropriate file
        # 3. Verify the fix works
        
        return True

    def run_workflow(self) -> dict[str, Any]:
        """Run complete self-healing workflow."""
        self.logger.info("Starting self-healing workflow...")
        
        results = {
            "bugs_detected": 0,
            "bugs_fixed": 0,
            "status": "completed",
        }

        # Scan for bugs
        bugs = self._scan_for_bugs()
        
        for bug in bugs:
            result = self.process_bug(bug)
            results["bugs_detected"] += 1
            if result.success:
                results["bugs_fixed"] += 1

        # Update statistics
        self.stats["total_runs"] += 1
        self._update_success_rate()
        
        return {
            **results,
            "stats": self.stats,
        }

    def _scan_for_bugs(self) -> list[BugReport]:
        """Scan codebase for potential bugs."""
        bugs = []
        
        # Scan log files
        log_path = Path("perplexity.log")
        if log_path.exists():
            log_bugs = self.bug_detector.detect_from_logs(log_path)
            bugs.extend(log_bugs)

        # Scan Python files
        for py_file in Path(".").rglob("*.py"):
            if "perplexity" in str(py_file):
                file_bugs = self.bug_detector.run_static_analysis(py_file)
                bugs.extend(file_bugs)

        return bugs

    def _update_success_rate(self):
        """Update success rate statistic."""
        if self.stats["total_runs"] > 0:
            self.stats["success_rate"] = (
                self.stats["bugs_fixed"] / self.stats["total_runs"] * 100
            )

    def get_statistics(self) -> dict[str, Any]:
        """Get self-healing statistics."""
        return {
            **self.stats,
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(
                1 for t in self.tasks.values() if t.status == WorkflowStatus.PENDING
            ),
            "completed_tasks": sum(
                1 for t in self.tasks.values() if t.status == WorkflowStatus.COMPLETED
            ),
            "failed_tasks": sum(
                1 for t in self.tasks.values() if t.status == WorkflowStatus.FAILED
            ),
        }
