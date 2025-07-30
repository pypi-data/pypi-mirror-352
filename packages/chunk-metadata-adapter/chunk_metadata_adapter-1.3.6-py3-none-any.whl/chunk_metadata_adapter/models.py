"""
Models for chunk metadata representation using Pydantic.
"""
from enum import Enum
from typing import List, Dict, Optional, Union, Any, Pattern
import re
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, validator, field_validator
import abc


# UUID4 регулярное выражение для валидации
UUID4_PATTERN: Pattern = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE
)

# ISO 8601 с таймзоной
ISO8601_PATTERN: Pattern = re.compile(
    r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$'
)


class ChunkType(str, Enum):
    """Types of semantic chunks"""
    DOC_BLOCK = "DocBlock"
    CODE_BLOCK = "CodeBlock"
    MESSAGE = "Message"
    DRAFT = "Draft"
    TASK = "Task"
    SUBTASK = "Subtask"
    TZ = "TZ"
    COMMENT = "Comment"
    LOG = "Log"
    METRIC = "Metric"


class ChunkRole(str, Enum):
    """Roles in the system"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    REVIEWER = "reviewer"
    DEVELOPER = "developer"


class ChunkStatus(str, Enum):
    """
    Status of a chunk processing.
    
    Represents the lifecycle stages of data in the system:
    1. Initial ingestion of raw data (RAW)
    2. Data cleaning/pre-processing (CLEANED)
    3. Verification against rules and standards (VERIFIED)
    4. Validation with cross-references and context (VALIDATED)
    5. Reliable data ready for usage (RELIABLE)
    
    Also includes operational statuses for tracking processing state.
    """
    # Начальный статус для новых данных
    NEW = "new"
    
    # Статусы жизненного цикла данных
    RAW = "raw"                    # Сырые данные, как они поступили в систему
    CLEANED = "cleaned"            # Данные прошли очистку от ошибок и шума
    VERIFIED = "verified"          # Данные проверены на соответствие правилам и стандартам
    VALIDATED = "validated"        # Данные прошли валидацию с учетом контекста и перекрестных ссылок
    RELIABLE = "reliable"          # Надежные данные, готовые к использованию
    
    # Операционные статусы
    INDEXED = "indexed"            # Данные проиндексированы
    OBSOLETE = "obsolete"          # Данные устарели
    REJECTED = "rejected"          # Данные отклонены из-за критических проблем
    IN_PROGRESS = "in_progress"    # Данные в процессе обработки
    
    # Дополнительные статусы для управления жизненным циклом
    NEEDS_REVIEW = "needs_review"  # Требуется ручная проверка
    ARCHIVED = "archived"          # Данные архивированы

    # Case-insensitive parsing support
    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive mapping from string to enum member."""
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        # Fallthrough to default behaviour
        return super()._missing_(value)


class FeedbackMetrics(BaseModel):
    """Feedback metrics for a chunk"""
    accepted: int = Field(default=0, description="How many times the chunk was accepted")
    rejected: int = Field(default=0, description="How many times the chunk was rejected")
    modifications: int = Field(default=0, description="Number of modifications made after generation")


class ChunkMetrics(BaseModel):
    """Metrics related to chunk quality and usage"""
    quality_score: Optional[float] = Field(default=None, ge=0, le=1, description="Quality score between 0 and 1")
    coverage: Optional[float] = Field(default=None, ge=0, le=1, description="Coverage score between 0 and 1")
    cohesion: Optional[float] = Field(default=None, ge=0, le=1, description="Cohesion score between 0 and 1")
    boundary_prev: Optional[float] = Field(default=None, ge=0, le=1, description="Boundary similarity with previous chunk")
    boundary_next: Optional[float] = Field(default=None, ge=0, le=1, description="Boundary similarity with next chunk")
    matches: Optional[int] = Field(default=None, ge=0, description="How many times matched in retrieval")
    used_in_generation: bool = Field(default=False, description="Whether used in generation")
    used_as_input: bool = Field(default=False, description="Whether used as input")
    used_as_context: bool = Field(default=False, description="Whether used as context")
    feedback: FeedbackMetrics = Field(default_factory=FeedbackMetrics, description="Feedback metrics")


class BaseChunkMetadata(BaseModel, abc.ABC):
    """
    Abstract base class for chunk metadata.
    """
    @abc.abstractmethod
    def validate_and_fill(data: dict):
        """Validate and fill defaults for input dict."""
        pass


class SemanticChunk(BaseChunkMetadata):
    """
    Main model representing a universal semantic chunk with metadata.
    Strict field validation for all fields.

    Пример использования валидации и автозаполнения:
    >>> data = {"type": "DocBlock", "text": "Hello", "language": "en", "sha256": "a"*64, "start": 0, "end": 5, "uuid": "...valid uuid..."}
    >>> obj, err = SemanticChunk.validate_and_fill(data)
    >>> if obj:
    ...     print(obj.text)
    ... else:
    ...     print(f"Ошибка: {err['error']}")
    ...     print(f"Поля: {err['fields']}")
    """
    uuid: str = Field(..., min_length=36, max_length=36, description="Unique identifier (UUIDv4) for this chunk.")
    type: ChunkType = Field(..., description="Type of chunk content.")
    role: Optional[ChunkRole] = Field(default=None, description="Role of the content creator.")
    project: Optional[str] = Field(default=None, min_length=1, max_length=128, description="Project identifier.")
    task_id: Optional[str] = Field(default=None, min_length=1, max_length=128, description="Task identifier.")
    subtask_id: Optional[str] = Field(default=None, min_length=1, max_length=128, description="Subtask identifier.")
    unit_id: Optional[str] = Field(default=None, min_length=1, max_length=128, description="Processing unit identifier.")

    body: Optional[str] = Field(default=None, min_length=1, max_length=10000, description="Raw content of the chunk.")
    text: str = Field(..., min_length=1, max_length=10000, description="Cleaned/normalized content of the chunk.")
    summary: Optional[str] = Field(default=None, min_length=1, max_length=512, description="Brief summary of the chunk's content.")
    language: str = Field(..., min_length=2, max_length=32, description="Content language or format.")

    block_id: Optional[str] = Field(default=None, min_length=36, max_length=36, description="UUIDv4 of the source block.")
    block_type: Optional[str] = Field(default=None, min_length=1, max_length=64, description="Type of the source block.")
    block_index: Optional[int] = Field(default=None, ge=0, description="Index of the block in the source document.")
    block_meta: Optional[dict] = Field(default=None, description="Additional metadata about the block.")

    source_id: Optional[str] = Field(default=None, min_length=36, max_length=36, description="UUIDv4 identifier of the source document.")
    source_path: Optional[str] = Field(default=None, min_length=1, max_length=512, description="Path to the source file or document.")
    source_lines: Optional[List[int]] = Field(default=None, min_length=2, max_length=2, description="Line numbers in the source file that this chunk covers.")
    ordinal: Optional[int] = Field(default=None, ge=0, description="Order of the chunk within the source or block.")

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp (ISO8601 with timezone).")
    status: ChunkStatus = Field(default=ChunkStatus.NEW, description="Processing status of the chunk.")
    chunking_version: Optional[str] = Field(default="1.0", min_length=1, max_length=32, description="Version of the chunking algorithm or pipeline.")

    sha256: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-fA-F]{64}$", description="SHA256 hash of the chunk's text content.")
    embedding: Optional[Any] = Field(default=None, description="Vector embedding of the chunk's content.")

    links: List[str] = Field(default_factory=list, min_length=0, max_length=32, description="References to other chunks in the format 'relation:uuid'.")
    tags: List[str] = Field(default_factory=list, min_length=0, max_length=32, description="Categorical tags for the chunk.")

    metrics: ChunkMetrics = Field(default_factory=ChunkMetrics, description="Quality and usage metrics for the chunk.")

    start: int = Field(..., ge=0, description="Start offset of the chunk in the source text.")
    end: int = Field(..., ge=0, description="End offset of the chunk in the source text.")

    @field_validator('uuid', 'block_id', 'source_id')
    @classmethod
    def validate_uuid_fields(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v
        if not UUID4_PATTERN.match(v):
            try:
                uuid_obj = uuid.UUID(v, version=4)
                if str(uuid_obj) != v.lower():
                    raise ValueError(f"{info.field_name} UUID version or format doesn't match")
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid UUID4 format for {info.field_name}: {v}")
        return v

    @field_validator('created_at')
    @classmethod
    def validate_created_at(cls, v: str) -> str:
        if not ISO8601_PATTERN.match(v):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    raise ValueError("Missing timezone information")
                return dt.isoformat()
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid ISO8601 format with timezone: {v}")
        return v

    @field_validator('links')
    @classmethod
    def validate_links(cls, links: List[str]) -> List[str]:
        for link in links:
            parts = link.split(":", 1)
            if len(parts) != 2 or not parts[0] or not parts[1]:
                raise ValueError(f"Link must follow 'relation:uuid' format: {link}")
            if len(parts[0]) < 2:
                raise ValueError(f"Relation part in link too short: {link}")
            uuid_part = parts[1]
            if not UUID4_PATTERN.match(uuid_part):
                try:
                    uuid_obj = uuid.UUID(uuid_part, version=4)
                    if str(uuid_obj) != uuid_part.lower():
                        raise ValueError("Link UUID version or format doesn't match")
                except (ValueError, AttributeError):
                    raise ValueError(f"Invalid UUID4 format in link: {link}")
        return links

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, tags: List[str]) -> List[str]:
        for tag in tags:
            if not tag or len(tag) < 1 or len(tag) > 32:
                raise ValueError(f"Tag must be 1-32 chars, got: '{tag}'")
        return tags

    @field_validator('sha256')
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{64}", v):
            raise ValueError(f"sha256 must be a 64-character hex string, got: {v}")
        return v

    @field_validator('source_lines')
    @classmethod
    def validate_source_lines(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            if len(v) != 2:
                raise ValueError("source_lines must have exactly 2 elements [start_line, end_line]")
            if v[0] < 0 or v[1] < 0:
                raise ValueError("source_lines values must be >= 0")
        return v

    @field_validator('end')
    @classmethod
    def validate_end_ge_start(cls, v: int, values) -> int:
        start = values.data.get('start') if hasattr(values, 'data') else values.get('start')
        if start is not None and v < start:
            raise ValueError(f"end ({v}) must be >= start ({start})")
        return v

    def validate(self) -> None:
        """Explicitly run all Pydantic validation (for external/manual calls)."""
        self.__class__.model_validate(self)

    @staticmethod
    def validate_and_fill(data: dict) -> tuple[Optional["SemanticChunk"], Optional[dict]]:
        """
        Validate and fill defaults for input dict. Returns (object, None) if valid, (None, error_dict) if not.
        error_dict: {'error': str, 'fields': {field: [errors]}}
        """
        from pydantic import ValidationError
        try:
            obj = SemanticChunk(**data)
            return obj, None
        except ValidationError as e:
            field_errors = {}
            for err in e.errors():
                loc = err.get('loc')
                if loc:
                    field = loc[0]
                    field_errors.setdefault(field, []).append(err.get('msg'))
            return None, {'error': str(e), 'fields': field_errors}
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    def validate_metadata(self) -> None:
        """Validate structured metadata (list tags, etc)."""
        if self.chunk_format != "structured":
            raise ValueError(f"Invalid chunk_format for SemanticChunk: {self.chunk_format}")
        # Проверка, что tags — список строк
        if not isinstance(self.tags, list):
            raise ValueError("tags must be a list for structured metadata")
        for tag in self.tags:
            if not isinstance(tag, str):
                raise ValueError(f"Each tag must be a string, got: {type(tag)}")
        self.validate()  # pydantic validation


class FlatSemanticChunk(BaseChunkMetadata):
    """
    Flat representation of the semantic chunk with all fields in a flat structure.
    Strict field validation for all fields.

    Пример использования:
    >>> data = {"type": "DocBlock", "text": "Hello", "language": "en", "sha256": "a"*64, "start": 0, "end": 5, "uuid": "...valid uuid...", "created_at": "..."}
    >>> obj, err = FlatSemanticChunk.validate_and_fill(data)
    >>> if obj:
    ...     print(obj.text)
    ... else:
    ...     print(f"Ошибка: {err['error']}")
    ...     print(f"Поля: {err['fields']}")
    """
    uuid: str = Field(..., min_length=36, max_length=36)
    source_id: Optional[str] = Field(default=None, min_length=36, max_length=36)
    project: Optional[str] = Field(default=None, min_length=1, max_length=128)
    task_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    subtask_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    unit_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    type: str = Field(..., min_length=3, max_length=32)
    role: Optional[str] = Field(default=None, min_length=2, max_length=32)
    language: str = Field(..., min_length=2, max_length=32)
    body: Optional[str] = Field(default=None, min_length=1, max_length=10000)
    text: str = Field(..., min_length=1, max_length=10000)
    summary: Optional[str] = Field(default=None, min_length=1, max_length=512)
    ordinal: Optional[int] = Field(default=None, ge=0)
    sha256: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-fA-F]{64}$")
    created_at: str = Field(...)
    status: str = Field(default=ChunkStatus.NEW.value, min_length=2, max_length=32)
    source_path: Optional[str] = Field(default=None, min_length=1, max_length=512)
    source_lines_start: Optional[int] = Field(default=None, ge=0)
    source_lines_end: Optional[int] = Field(default=None, ge=0)
    tags: Optional[str] = Field(default=None, max_length=1024)
    link_related: Optional[str] = Field(default=None, min_length=36, max_length=36)
    link_parent: Optional[str] = Field(default=None, min_length=36, max_length=36)
    quality_score: Optional[float] = Field(default=None, ge=0, le=1)
    coverage: Optional[float] = Field(default=None, ge=0, le=1)
    cohesion: Optional[float] = Field(default=None, ge=0, le=1)
    boundary_prev: Optional[float] = Field(default=None, ge=0, le=1)
    boundary_next: Optional[float] = Field(default=None, ge=0, le=1)
    used_in_generation: bool = False
    feedback_accepted: int = Field(default=0, ge=0)
    feedback_rejected: int = Field(default=0, ge=0)
    start: Optional[int] = Field(default=None, ge=0)
    end: Optional[int] = Field(default=None, ge=0)

    @field_validator('uuid', 'source_id', 'link_related', 'link_parent')
    @classmethod
    def validate_uuid_fields(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v
        if not UUID4_PATTERN.match(v):
            try:
                uuid_obj = uuid.UUID(v, version=4)
                if str(uuid_obj) != v.lower():
                    raise ValueError(f"{info.field_name} UUID version or format doesn't match")
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid UUID4 format for {info.field_name}: {v}")
        return v

    @field_validator('created_at')
    @classmethod
    def validate_created_at(cls, v: str) -> str:
        if not ISO8601_PATTERN.match(v):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    raise ValueError("Missing timezone information")
                return dt.isoformat()
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid ISO8601 format with timezone: {v}")
        return v

    @field_validator('sha256')
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{64}", v):
            raise ValueError(f"sha256 must be a 64-character hex string, got: {v}")
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        tags = [tag.strip() for tag in v.split(",") if tag.strip()]
        for tag in tags:
            if not tag or len(tag) < 1 or len(tag) > 32:
                raise ValueError(f"Each tag must be 1-32 chars, got: '{tag}'")
        return v

    @field_validator('end')
    @classmethod
    def validate_end_ge_start(cls, v: Optional[int], values) -> Optional[int]:
        start = values.data.get('start') if hasattr(values, 'data') else values.get('start')
        if v is not None and start is not None and v < start:
            raise ValueError(f"end ({v}) must be >= start ({start})")
        return v

    def validate(self) -> None:
        """Explicitly run all Pydantic validation (for external/manual calls)."""
        self.__class__.model_validate(self)

    @staticmethod
    def validate_and_fill(data: dict) -> tuple[Optional["FlatSemanticChunk"], Optional[dict]]:
        """
        Validate and fill defaults for input dict. Returns (object, None) if valid, (None, error_dict) if not.
        error_dict: {'error': str, 'fields': {field: [errors]}}
        """
        from pydantic import ValidationError
        try:
            obj = FlatSemanticChunk(**data)
            return obj, None
        except ValidationError as e:
            field_errors = {}
            for err in e.errors():
                loc = err.get('loc')
                if loc:
                    field = loc[0]
                    field_errors.setdefault(field, []).append(err.get('msg'))
            return None, {'error': str(e), 'fields': field_errors}
        except Exception as e:
            return None, {'error': str(e), 'fields': {}}

    def validate_metadata(self) -> None:
        """Validate flat metadata (tags as comma-separated string, etc)."""
        if self.chunk_format != "flat":
            raise ValueError(f"Invalid chunk_format for FlatSemanticChunk: {self.chunk_format}")
        # Проверка, что tags — строка или None
        if self.tags is not None and not isinstance(self.tags, str):
            raise ValueError("tags must be a string for flat metadata")
        self.validate()  # pydantic validation

    @classmethod
    def from_semantic_chunk(cls, chunk: SemanticChunk) -> 'FlatSemanticChunk':
        """Convert a full SemanticChunk to flat representation"""
        source_lines_start = None
        source_lines_end = None
        if chunk.source_lines and len(chunk.source_lines) >= 2:
            source_lines_start = chunk.source_lines[0]
            source_lines_end = chunk.source_lines[1]
            
        # Extract link references
        link_parent = None
        link_related = None
        for link in chunk.links:
            if link.startswith("parent:"):
                link_parent = link.split(":", 1)[1]
            elif link.startswith("related:"):
                link_related = link.split(":", 1)[1]
                
        return cls(
            uuid=chunk.uuid,
            source_id=chunk.source_id,
            project=chunk.project,
            task_id=chunk.task_id,
            subtask_id=chunk.subtask_id,
            unit_id=chunk.unit_id,
            type=chunk.type.value,
            role=chunk.role.value if chunk.role else None,
            language=chunk.language,
            body=getattr(chunk, 'body', None),
            text=chunk.text,
            summary=chunk.summary,
            ordinal=chunk.ordinal,
            sha256=chunk.sha256,
            created_at=chunk.created_at,
            status=chunk.status.value,
            source_path=chunk.source_path,
            source_lines_start=source_lines_start,
            source_lines_end=source_lines_end,
            tags=",".join(chunk.tags) if chunk.tags else None,
            link_related=link_related,
            link_parent=link_parent,
            quality_score=chunk.metrics.quality_score,
            coverage=chunk.metrics.coverage,
            cohesion=getattr(chunk.metrics, "cohesion", None),
            boundary_prev=getattr(chunk.metrics, "boundary_prev", None),
            boundary_next=getattr(chunk.metrics, "boundary_next", None),
            used_in_generation=chunk.metrics.used_in_generation,
            feedback_accepted=chunk.metrics.feedback.accepted,
            feedback_rejected=chunk.metrics.feedback.rejected,
            start=chunk.start,
            end=chunk.end
        )
        
    def to_semantic_chunk(self) -> SemanticChunk:
        """Convert flat representation to full SemanticChunk"""
        # Prepare links
        links = []
        if self.link_parent:
            links.append(f"parent:{self.link_parent}")
        if self.link_related:
            links.append(f"related:{self.link_related}")
            
        # Prepare tags
        tags = self.tags.split(",") if self.tags else []
        
        # Prepare source lines
        source_lines = None
        if self.source_lines_start is not None and self.source_lines_end is not None:
            source_lines = [self.source_lines_start, self.source_lines_end]
            
        # Prepare metrics
        metrics = ChunkMetrics(
            quality_score=self.quality_score,
            coverage=self.coverage,
            cohesion=self.cohesion,
            boundary_prev=self.boundary_prev,
            boundary_next=self.boundary_next,
            used_in_generation=self.used_in_generation,
            feedback=FeedbackMetrics(
                accepted=self.feedback_accepted,
                rejected=self.feedback_rejected
            )
        )
        
        return SemanticChunk(
            uuid=self.uuid,
            type=self.type,
            role=self.role,
            project=self.project,
            task_id=self.task_id,
            subtask_id=self.subtask_id,
            unit_id=self.unit_id,
            body=getattr(self, 'body', None),
            text=self.text,
            summary=self.summary,
            language=self.language,
            source_id=self.source_id,
            source_path=self.source_path,
            source_lines=source_lines,
            ordinal=self.ordinal,
            created_at=self.created_at,
            status=self.status,
            sha256=self.sha256,
            links=links,
            tags=tags,
            metrics=metrics,
            start=self.start,
            end=self.end
        ) 