"""Assessment API: Handles diagnostic quiz questions, backend grading,
Bayesian Knowledge Tracing (BKT) updates, and 5-agent LangGraph orchestration.
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import (
    get_db, User, Skill, Assessment, UserSkill,
    AssessmentQuestion, AssessmentAttempt, BKTState
)
from ..schemas import (
    AssessmentCreate, AssessmentResponse,
    QuizQuestionOption, QuizSubmitRequest, QuizQuestionResult, QuizSubmissionResponse
)
from .deps import get_current_user
from .agent_runner import execute_learner_agent_cycle

router = APIRouter(prefix="/assessment", tags=["Assessments"])


@router.get("/questions", response_model=List[QuizQuestionOption])
def get_quiz_questions(
    skill_id: Optional[int] = Query(None, description="Filter quiz questions by skill ID"),
    limit: int = Query(10, ge=1, le=50, description="Max questions to return"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve multiple-choice diagnostic questions for skills (correct answers omitted to prevent cheating)."""
    query = db.query(AssessmentQuestion)
    if skill_id is not None:
        query = query.filter(AssessmentQuestion.skill_id == skill_id)

    questions = query.limit(limit).all()
    return [
        QuizQuestionOption(
            id=q.id,
            skill_id=q.skill_id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            difficulty=q.difficulty
        )
        for q in questions
    ]


@router.post("/quiz-submit", response_model=QuizSubmissionResponse)
def submit_quiz_answers(
    payload: QuizSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submits student answers, grades each against verified answer keys on backend,
    updates UserSkill Q_s, executes 5-agent LangGraph workflow, updates BKT mastery,
    and returns comprehensive graded results with explanations.
    """
    skill = db.query(Skill).filter_by(id=payload.skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    if not payload.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers provided for submission."
        )

    # 1. Grade each question on the backend
    results: List[QuizQuestionResult] = []
    correct_count = 0
    total_questions = len(payload.answers)

    # Get prior BKT mastery
    prior_bkt = db.query(BKTState).filter_by(user_id=user.id, skill_id=payload.skill_id).first()
    p_mastery_before = prior_bkt.p_mastery if prior_bkt else 0.30

    for q_id_str, selected_opt in payload.answers.items():
        try:
            q_id = int(q_id_str)
        except ValueError:
            continue

        question = db.query(AssessmentQuestion).filter_by(id=q_id).first()
        if not question:
            continue

        selected_clean = selected_opt.strip().upper()
        is_correct = (selected_clean == question.correct_option.strip().upper())
        if is_correct:
            correct_count += 1

        score_item = 100.0 if is_correct else 0.0

        # Log individual question attempt
        attempt = AssessmentAttempt(
            user_id=user.id,
            question_id=question.id,
            selected_option=selected_clean,
            is_correct=is_correct,
            score=score_item
        )
        db.add(attempt)

        results.append(QuizQuestionResult(
            question_id=question.id,
            question_text=question.question_text,
            selected_option=selected_clean,
            correct_option=question.correct_option,
            is_correct=is_correct,
            explanation=question.explanation
        ))

    score_percentage = round((correct_count / total_questions * 100.0) if total_questions > 0 else 0.0, 1)

    # 2. Record aggregate assessment
    assessment = Assessment(
        user_id=user.id,
        skill_id=payload.skill_id,
        score=score_percentage
    )
    db.add(assessment)
    db.flush()

    # 3. Update average quiz score Q_s for this skill
    avg_score = db.query(func.avg(Assessment.score)).filter(
        Assessment.user_id == user.id,
        Assessment.skill_id == payload.skill_id
    ).scalar() or score_percentage

    u_skill = db.query(UserSkill).filter_by(user_id=user.id, skill_id=payload.skill_id).first()
    if u_skill:
        u_skill.Q_s = round(float(avg_score), 2)
    db.commit()

    # 4. Trigger LangGraph agent cycle
    event_payload = {
        "skill_id": payload.skill_id,
        "score": score_percentage
    }
    final_state = execute_learner_agent_cycle(
        user_id=user.id,
        event="new_assessment",
        db=db,
        event_payload=event_payload
    )

    bkt_data = final_state.get("bkt_states", {}).get(payload.skill_id, {})
    p_mastery_after = bkt_data.get("p_mastery", p_mastery_before)
    remediation = bkt_data.get("needs_remediation", False)

    return QuizSubmissionResponse(
        skill_id=payload.skill_id,
        skill_name=skill.name,
        total_questions=total_questions,
        correct_count=correct_count,
        score_percentage=score_percentage,
        p_mastery_before=p_mastery_before,
        p_mastery_after=p_mastery_after,
        remediation_flag=remediation,
        results=results
    )


@router.post("", response_model=AssessmentResponse)
def submit_assessment(
    payload: AssessmentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Direct assessment score submission (compatibility endpoint)."""
    skill = db.query(Skill).filter_by(id=payload.skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    # 1. Save assessment record
    assessment = Assessment(
        user_id=user.id,
        skill_id=payload.skill_id,
        score=payload.score
    )
    db.add(assessment)
    db.flush()

    # 2. Update average quiz score Q_s for this skill
    avg_score = db.query(func.avg(Assessment.score)).filter(
        Assessment.user_id == user.id,
        Assessment.skill_id == payload.skill_id
    ).scalar() or payload.score

    u_skill = db.query(UserSkill).filter_by(user_id=user.id, skill_id=payload.skill_id).first()
    if u_skill:
        u_skill.Q_s = round(float(avg_score), 2)
    db.commit()

    # 3. Trigger LangGraph agent pipeline
    event_payload = {
        "skill_id": payload.skill_id,
        "score": payload.score
    }
    final_state = execute_learner_agent_cycle(
        user_id=user.id,
        event="new_assessment",
        db=db,
        event_payload=event_payload
    )

    bkt_data = final_state.get("bkt_states", {}).get(payload.skill_id, {})
    p_mastery = bkt_data.get("p_mastery", 0.30)
    remediation = bkt_data.get("needs_remediation", False)

    return AssessmentResponse(
        id=assessment.id,
        user_id=user.id,
        skill_id=payload.skill_id,
        skill_name=skill.name,
        score=payload.score,
        taken_at=assessment.taken_at,
        p_mastery_after=p_mastery,
        remediation_flag=remediation
    )
