"""Academy 비즈니스 로직 (교육 목록/상세, 퀴즈 채점, 수료, AI 보조)."""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations import ai
from app.models import User
from app.repositories import academy_repository as repo
from app.schemas.academy import (
    CompletionOut,
    CourseDetail,
    CourseSummary,
    QuizQuestionPublic,
    QuizResult,
    QuizResultItem,
    QuizSubmission,
    ReflectResponse,
)

PASS_RATIO = 0.6  # 60% 이상 맞히면 수료


def list_courses(db: Session) -> list[CourseSummary]:
    out: list[CourseSummary] = []
    for c in repo.list_courses(db):
        out.append(
            CourseSummary(
                id=c.id,
                slug=c.slug,
                title=c.title,
                emoji=c.emoji,
                summary=c.summary,
                order_no=c.order_no,
                question_count=len(c.questions),
            )
        )
    return out


def get_course_detail(db: Session, course_id: int) -> CourseDetail:
    c = repo.get_course(db, course_id)
    if c is None:
        raise HTTPException(status_code=404, detail="교육 과정을 찾을 수 없어요.")
    return CourseDetail(
        id=c.id,
        slug=c.slug,
        title=c.title,
        emoji=c.emoji,
        summary=c.summary,
        content=c.content,
        order_no=c.order_no,
        questions=[
            QuizQuestionPublic(id=q.id, question=q.question, options=q.options)
            for q in c.questions
        ],
    )


def grade_quiz(
    db: Session, course_id: int, submission: QuizSubmission, user: User
) -> QuizResult:
    """퀴즈 채점 + 수료 기록 저장."""
    c = repo.get_course(db, course_id)
    if c is None:
        raise HTTPException(status_code=404, detail="교육 과정을 찾을 수 없어요.")
    questions = c.questions
    if len(submission.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"답안 개수가 문항 수({len(questions)})와 일치하지 않아요.",
        )

    results: list[QuizResultItem] = []
    score = 0
    for q, chosen in zip(questions, submission.answers, strict=True):
        correct = chosen == q.answer_index
        if correct:
            score += 1
        results.append(
            QuizResultItem(
                question_id=q.id,
                correct=correct,
                answer_index=q.answer_index,
                explanation=q.explanation,
            )
        )

    total = len(questions)
    passed = total > 0 and (score / total) >= PASS_RATIO
    repo.upsert_completion(
        db, user_id=user.id, course_id=course_id, score=score, total=total, passed=passed
    )
    return QuizResult(
        course_id=course_id, score=score, total=total, passed=passed, results=results
    )


def my_completions(db: Session, user: User) -> list[CompletionOut]:
    out: list[CompletionOut] = []
    for comp in repo.list_completions(db, user.id):
        out.append(
            CompletionOut(
                course_id=comp.course_id,
                course_title=comp.course.title,
                emoji=comp.course.emoji,
                score=comp.score,
                total=comp.total,
                passed=comp.passed,
                completed_at=comp.completed_at,
            )
        )
    return out


def reflect(situation: str) -> ReflectResponse:
    """입양 전 자기 점검 보조(추천 아님). ai.adoption_reflection 사용."""
    data = ai.adoption_reflection(situation)
    return ReflectResponse(**data)
