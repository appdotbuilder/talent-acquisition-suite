from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


# Enums for status tracking
class UserRole(str, Enum):
    CANDIDATE = "candidate"
    DEPARTMENTAL = "departmental"
    TA_ADMIN = "ta_admin"


class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_MADE = "offer_made"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class VacancyStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class InterviewType(str, Enum):
    INITIAL_SCREENING = "initial_screening"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"
    FINAL = "final"
    AI_ASSISTED = "ai_assisted"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class NotificationType(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    BOTH = "both"


class ReportType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


# Core User Model
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.CANDIDATE)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)

    # Profile information
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)

    # Relationships
    applications: List["Application"] = Relationship(back_populates="candidate")
    manpower_requests: List["ManpowerRequest"] = Relationship(back_populates="requester")
    created_vacancies: List["Vacancy"] = Relationship(back_populates="created_by")
    interviews: List["Interview"] = Relationship(back_populates="interviewer")
    notifications: List["Notification"] = Relationship(back_populates="user")
    audit_logs: List["AuditLog"] = Relationship(back_populates="user")


# Manpower Request Model
class ManpowerRequest(SQLModel, table=True):
    __tablename__ = "manpower_requests"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    department: str = Field(max_length=100)
    justification: str = Field(max_length=1000)
    headcount: int = Field(default=1, gt=0)
    priority: str = Field(max_length=20, default="medium")  # low, medium, high, urgent

    # Required skills and experience
    required_skills: List[str] = Field(default=[], sa_column=Column(JSON))
    preferred_skills: List[str] = Field(default=[], sa_column=Column(JSON))
    minimum_experience_years: int = Field(default=0, ge=0)
    education_requirements: str = Field(default="", max_length=500)

    # Salary and benefits
    salary_min: Optional[Decimal] = Field(default=None, decimal_places=2)
    salary_max: Optional[Decimal] = Field(default=None, decimal_places=2)
    benefits: str = Field(default="", max_length=1000)

    # Status tracking
    status: str = Field(default="pending", max_length=20)
    approved_at: Optional[datetime] = Field(default=None)

    # Foreign keys
    requester_id: int = Field(foreign_key="users.id")
    approved_by_id: Optional[int] = Field(default=None, foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    requester: User = Relationship(back_populates="manpower_requests")
    vacancies: List["Vacancy"] = Relationship(back_populates="manpower_request")


# Job Vacancy Model
class Vacancy(SQLModel, table=True):
    __tablename__ = "vacancies"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    job_title: str = Field(max_length=200)
    job_description: str = Field(max_length=3000)
    department: str = Field(max_length=100)
    location: str = Field(max_length=200)
    employment_type: str = Field(max_length=50, default="full_time")  # full_time, part_time, contract, internship

    # Requirements
    required_skills: List[str] = Field(default=[], sa_column=Column(JSON))
    preferred_skills: List[str] = Field(default=[], sa_column=Column(JSON))
    minimum_experience_years: int = Field(default=0, ge=0)
    education_requirements: str = Field(default="", max_length=500)

    # Salary and benefits
    salary_min: Optional[Decimal] = Field(default=None, decimal_places=2)
    salary_max: Optional[Decimal] = Field(default=None, decimal_places=2)
    benefits: str = Field(default="", max_length=1000)

    # Status and lifecycle
    status: VacancyStatus = Field(default=VacancyStatus.DRAFT)
    is_published: bool = Field(default=False)
    published_at: Optional[datetime] = Field(default=None)
    application_deadline: Optional[datetime] = Field(default=None)
    closed_at: Optional[datetime] = Field(default=None)

    # Approval workflow
    approved_at: Optional[datetime] = Field(default=None)
    approved_by_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Foreign keys
    created_by_id: int = Field(foreign_key="users.id")
    manpower_request_id: Optional[int] = Field(default=None, foreign_key="manpower_requests.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    created_by: User = Relationship(back_populates="created_vacancies")
    manpower_request: Optional[ManpowerRequest] = Relationship(back_populates="vacancies")
    applications: List["Application"] = Relationship(back_populates="vacancy")


# Application Model
class Application(SQLModel, table=True):
    __tablename__ = "applications"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)

    # CV and application data
    cv_file_path: str = Field(max_length=500)
    cv_original_name: str = Field(max_length=255)
    cover_letter: str = Field(default="", max_length=2000)

    # AI parsing results
    parsed_cv_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    ai_match_score: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0, le=100)
    ai_match_details: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Status tracking
    status: ApplicationStatus = Field(default=ApplicationStatus.SUBMITTED)
    shortlisted_at: Optional[datetime] = Field(default=None)
    rejected_at: Optional[datetime] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)

    # Notes and feedback
    recruiter_notes: str = Field(default="", max_length=2000)

    # Foreign keys
    candidate_id: int = Field(foreign_key="users.id")
    vacancy_id: int = Field(foreign_key="vacancies.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    candidate: User = Relationship(back_populates="applications")
    vacancy: Vacancy = Relationship(back_populates="applications")
    interviews: List["Interview"] = Relationship(back_populates="application")
    offers: List["JobOffer"] = Relationship(back_populates="application")


# Interview Model
class Interview(SQLModel, table=True):
    __tablename__ = "interviews"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    interview_type: InterviewType = Field(default=InterviewType.INITIAL_SCREENING)
    status: InterviewStatus = Field(default=InterviewStatus.SCHEDULED)

    # Scheduling
    scheduled_date: datetime
    duration_minutes: int = Field(default=60, gt=0)
    location: str = Field(default="", max_length=200)  # Can be virtual meeting link
    meeting_link: Optional[str] = Field(default=None, max_length=500)

    # Interview details
    interviewer_notes: str = Field(default="", max_length=2000)
    candidate_feedback: str = Field(default="", max_length=1000)
    rating: Optional[int] = Field(default=None, ge=1, le=10)
    recommendation: Optional[str] = Field(default=None, max_length=20)  # proceed, reject, reconsider

    # AI assistance
    ai_suggested_questions: List[str] = Field(default=[], sa_column=Column(JSON))
    ai_analysis: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Foreign keys
    application_id: int = Field(foreign_key="applications.id")
    interviewer_id: int = Field(foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    application: Application = Relationship(back_populates="interviews")
    interviewer: User = Relationship(back_populates="interviews")


# Job Offer Model
class JobOffer(SQLModel, table=True):
    __tablename__ = "job_offers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)

    # Offer details
    job_title: str = Field(max_length=200)
    department: str = Field(max_length=100)
    salary_offered: Decimal = Field(decimal_places=2, gt=0)
    benefits_offered: str = Field(default="", max_length=1000)
    start_date: Optional[datetime] = Field(default=None)

    # Offer lifecycle
    offer_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: datetime
    response_date: Optional[datetime] = Field(default=None)
    status: str = Field(default="pending", max_length=20)  # pending, accepted, rejected, expired, withdrawn

    # Terms and conditions
    contract_terms: str = Field(default="", max_length=2000)
    special_conditions: str = Field(default="", max_length=1000)

    # Foreign keys
    application_id: int = Field(foreign_key="applications.id")
    offered_by_id: int = Field(foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    application: Application = Relationship(back_populates="offers")


# Notification Model
class Notification(SQLModel, table=True):
    __tablename__ = "notifications"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    notification_type: NotificationType = Field(default=NotificationType.EMAIL)

    # Delivery tracking
    sent_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)
    read_at: Optional[datetime] = Field(default=None)
    failed_at: Optional[datetime] = Field(default=None)
    failure_reason: Optional[str] = Field(default=None, max_length=500)

    # Retry logic
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)

    # Context
    related_entity_type: Optional[str] = Field(default=None, max_length=50)  # application, interview, offer, etc.
    related_entity_id: Optional[int] = Field(default=None)

    # Foreign keys
    user_id: int = Field(foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="notifications")


# Report Model
class Report(SQLModel, table=True):
    __tablename__ = "reports"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    report_type: ReportType = Field(default=ReportType.WEEKLY)

    # Report period
    period_start: datetime
    period_end: datetime

    # Report data and metrics
    report_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    kpi_metrics: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # File information
    file_path: Optional[str] = Field(default=None, max_length=500)
    file_size: Optional[int] = Field(default=None)

    # Generation and delivery
    generated_at: Optional[datetime] = Field(default=None)
    emailed_at: Optional[datetime] = Field(default=None)
    recipients: List[str] = Field(default=[], sa_column=Column(JSON))

    # Generation status
    status: str = Field(default="pending", max_length=20)  # pending, generating, completed, failed
    error_message: Optional[str] = Field(default=None, max_length=500)

    # Foreign keys
    generated_by_id: Optional[int] = Field(default=None, foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)


# Audit Log Model
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(max_length=100)
    entity_type: str = Field(max_length=50)
    entity_id: int

    # Change tracking
    old_values: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    new_values: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Context
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    additional_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Foreign keys
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="audit_logs")


# System Configuration Model
class SystemConfig(SQLModel, table=True):
    __tablename__ = "system_configs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, max_length=100)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas for API and validation


class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.CANDIDATE)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)


class UserUpdate(SQLModel, table=False):
    email: Optional[str] = Field(default=None, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class ManpowerRequestCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    department: str = Field(max_length=100)
    justification: str = Field(max_length=1000)
    headcount: int = Field(default=1, gt=0)
    priority: str = Field(max_length=20, default="medium")
    required_skills: List[str] = Field(default=[])
    preferred_skills: List[str] = Field(default=[])
    minimum_experience_years: int = Field(default=0, ge=0)
    education_requirements: str = Field(default="", max_length=500)
    salary_min: Optional[Decimal] = Field(default=None, decimal_places=2)
    salary_max: Optional[Decimal] = Field(default=None, decimal_places=2)
    benefits: str = Field(default="", max_length=1000)


class VacancyCreate(SQLModel, table=False):
    job_title: str = Field(max_length=200)
    job_description: str = Field(max_length=3000)
    department: str = Field(max_length=100)
    location: str = Field(max_length=200)
    employment_type: str = Field(max_length=50, default="full_time")
    required_skills: List[str] = Field(default=[])
    preferred_skills: List[str] = Field(default=[])
    minimum_experience_years: int = Field(default=0, ge=0)
    education_requirements: str = Field(default="", max_length=500)
    salary_min: Optional[Decimal] = Field(default=None, decimal_places=2)
    salary_max: Optional[Decimal] = Field(default=None, decimal_places=2)
    benefits: str = Field(default="", max_length=1000)
    application_deadline: Optional[datetime] = Field(default=None)
    manpower_request_id: Optional[int] = Field(default=None)


class ApplicationCreate(SQLModel, table=False):
    vacancy_id: int
    cv_file_path: str = Field(max_length=500)
    cv_original_name: str = Field(max_length=255)
    cover_letter: str = Field(default="", max_length=2000)


class InterviewCreate(SQLModel, table=False):
    application_id: int
    interview_type: InterviewType = Field(default=InterviewType.INITIAL_SCREENING)
    scheduled_date: datetime
    duration_minutes: int = Field(default=60, gt=0)
    location: str = Field(default="", max_length=200)
    meeting_link: Optional[str] = Field(default=None, max_length=500)
    interviewer_id: int


class JobOfferCreate(SQLModel, table=False):
    application_id: int
    job_title: str = Field(max_length=200)
    department: str = Field(max_length=100)
    salary_offered: Decimal = Field(decimal_places=2, gt=0)
    benefits_offered: str = Field(default="", max_length=1000)
    start_date: Optional[datetime] = Field(default=None)
    expiry_date: datetime
    contract_terms: str = Field(default="", max_length=2000)
    special_conditions: str = Field(default="", max_length=1000)


class NotificationCreate(SQLModel, table=False):
    user_id: int
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    notification_type: NotificationType = Field(default=NotificationType.EMAIL)
    related_entity_type: Optional[str] = Field(default=None, max_length=50)
    related_entity_id: Optional[int] = Field(default=None)
