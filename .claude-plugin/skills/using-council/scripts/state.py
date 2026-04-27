"""STATE.json schema + load/write helpers for council resumability."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path

VALID_PHASES = {
    "phase-0-intake",
    "phase-1-research",
    "phase-2-synthesis",
    "phase-3-critique",
    "phase-4-final-design",
    "phase-4b-signoff",
    "phase-5-plan-handoff",
    "phase-6-execution",
    "phase-6-final-review",
    "complete",
    "abandoned",
}


class MissingStateError(FileNotFoundError):
    pass


@dataclass
class MemberRecord:
    role: str
    type: str
    artifact: str
    done: bool

    def __post_init__(self):
        if self.type != "core" and self.type != "invented" and not self.type.startswith("library:"):
            raise ValueError(f"invalid member type: {self.type!r}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MemberRecord":
        return cls(role=d["role"], type=d["type"], artifact=d["artifact"], done=bool(d["done"]))


@dataclass
class CouncilState:
    slug: str
    phase: str
    members: list[MemberRecord]
    draft_design_written: bool
    verdict_committed: bool
    phase_4b_triggered: bool
    started_at: str
    last_updated_at: str
    research_truncated: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.phase not in VALID_PHASES:
            raise ValueError(f"invalid phase: {self.phase!r}; valid: {sorted(VALID_PHASES)}")

    def mark_done(self, role: str) -> None:
        for m in self.members:
            if m.role == role:
                m.done = True
                return
        raise KeyError(f"unknown member role: {role!r}")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["members"] = [m.to_dict() if isinstance(m, MemberRecord) else m for m in self.members]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CouncilState":
        return cls(
            slug=d["slug"],
            phase=d["phase"],
            members=[MemberRecord.from_dict(m) for m in d["members"]],
            draft_design_written=bool(d["draft_design_written"]),
            verdict_committed=bool(d["verdict_committed"]),
            phase_4b_triggered=bool(d["phase_4b_triggered"]),
            started_at=d["started_at"],
            last_updated_at=d["last_updated_at"],
            research_truncated=list(d.get("research_truncated", [])),
        )


def load_state(path: Path) -> CouncilState:
    if not path.is_file():
        raise MissingStateError(str(path))
    with path.open() as f:
        d = json.load(f)
    return CouncilState.from_dict(d)


def write_state(path: Path, state: CouncilState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(state.to_dict(), f, indent=2, sort_keys=False)
        f.write("\n")
