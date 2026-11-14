"""Roadmap API: Generates, retrieves, and tracks progress on adaptive learning pathways.
Integrates with multi-agent recommendation engine.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import (
    get_db, User, Skill, CareerRole, UserCareerGoal,
    LearningRoadmap, RoadmapItem, RoleSkillRequirement, UserSkill
)
from ..schemas import (
    LearningRoadmapResponse, RoadmapItemResponse, RoadmapItemStatusUpdate
)
from .deps import get_current_user
from .agent_runner import execute_learner_agent_cycle

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmap"])


@router.get("", response_model=LearningRoadmapResponse)
def get_user_roadmap(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the learner's active learning roadmap and stage completion progress."""
    roadmap = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.user_id == user.id, LearningRoadmap.is_active == True)
        .order_by(desc(LearningRoadmap.id))
        .first()
    )

    if not roadmap:
        # Check active career goal to auto-generate if missing
        active_goal = (
            db.query(UserCareerGoal)
            .filter(UserCareerGoal.user_id == user.id, UserCareerGoal.active == True)
            .first()
        )
        if not active_goal:
            # Fallback to first role
            role = db.query(CareerRole).first()
            if not role:
                raise HTTPException(status_code=404, detail="No career roles available.")
            role_id = role.id
        else:
            role_id = active_goal.role_id

        # Auto-create initial roadmap
        role = db.query(CareerRole).filter_by(id=role_id).first()
        roadmap = LearningRoadmap(
            user_id=user.id,
            role_id=role_id,
            title=f"{role.title} Personalized Roadmap",
            is_active=True
        )
        db.add(roadmap)
        db.flush()

        # Generate stages for skills in this role
        reqs = db.query(RoleSkillRequirement).filter_by(role_id=role_id).all()
        for idx, req in enumerate(reqs, start=1):
            skill = db.query(Skill).filter_by(id=req.skill_id).first()
            sk_name = skill.name if skill else f"Skill {req.skill_id}"
            db.add(RoadmapItem(
                roadmap_id=roadmap.id,
                skill_id=req.skill_id,
                stage_order=idx,
                stage_title=f"Phase {idx}: {sk_name} Mastery",
                difficulty=1 if req.R_s < 60 else (2 if req.R_s < 80 else 3),
                est_hours=round(req.R_s * 0.25, 1),
                status="in_progress" if idx == 1 else "not_started",
                prerequisites="" if idx == 1 else f"Phase {idx - 1}"
            ))
        db.commit()
        db.refresh(roadmap)

    # Compute progress percentage
    items = db.query(RoadmapItem).filter_by(roadmap_id=roadmap.id).order_by(RoadmapItem.stage_order).all()
    total_count = len(items)
    completed_count = sum(1 for item in items if item.status == "completed")
    progress_pct = round((completed_count / total_count * 100.0) if total_count > 0 else 0.0, 1)

    # Build response items
    response_items = []
    for item in items:
        sk = db.query(Skill).filter_by(id=item.skill_id).first()
        response_items.append(RoadmapItemResponse(
            id=item.id,
            roadmap_id=item.roadmap_id,
            skill_id=item.skill_id,
            skill_name=sk.name if sk else "Unknown",
            stage_order=item.stage_order,
            stage_title=item.stage_title,
            difficulty=item.difficulty,
            est_hours=item.est_hours,
            status=item.status,
            prerequisites=item.prerequisites,
            started_at=item.started_at,
            completed_at=item.completed_at
        ))

    role = db.query(CareerRole).filter_by(id=roadmap.role_id).first()
    return LearningRoadmapResponse(
        id=roadmap.id,
        user_id=roadmap.user_id,
        role_id=roadmap.role_id,
        role_title=role.title if role else "Career Role",
        title=roadmap.title,
        generated_at=roadmap.generated_at,
        is_active=roadmap.is_active,
        progress_percentage=progress_pct,
        items=response_items
    )


@router.post("/generate", response_model=LearningRoadmapResponse)
def generate_adaptive_roadmap(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerates or adapts the learning roadmap based on active career goal and current skill gaps."""
    active_goal = (
        db.query(UserCareerGoal)
        .filter(UserCareerGoal.user_id == user.id, UserCareerGoal.active == True)
        .first()
    )
    if not active_goal:
        role = db.query(CareerRole).first()
        if not role:
            raise HTTPException(status_code=404, detail="No career role configured.")
        role_id = role.id
    else:
        role_id = active_goal.role_id

    role = db.query(CareerRole).filter_by(id=role_id).first()

    # Deactivate existing active roadmaps
    db.query(LearningRoadmap).filter_by(user_id=user.id, is_active=True).update({"is_active": False})

    # Run agent cycle to get latest skill gaps
    final_state = execute_learner_agent_cycle(
        user_id=user.id,
        event="goal_change",
        db=db,
        event_payload={"role_id": role_id}
    )

    new_roadmap = LearningRoadmap(
        user_id=user.id,
        role_id=role_id,
        title=f"Adaptive {role.title} Pathway",
        is_active=True
    )
    db.add(new_roadmap)
    db.flush()

    # Rank skills by priority score / gap
    reqs = db.query(RoleSkillRequirement).filter_by(role_id=role_id).all()
    user_skills_map = {us.skill_id: us.P_s for us in db.query(UserSkill).filter_by(user_id=user.id).all()}

    # Calculate gap G_s = max(0, R_s - P_s)
    ranked_reqs = []
    for r in reqs:
        p_s = user_skills_map.get(r.skill_id, 0.0)
        gap = max(0.0, r.R_s - p_s)
        ranked_reqs.append((r, gap))

    # Sort largest gap first (highest learning need)
    ranked_reqs.sort(key=lambda x: x[1], reverse=True)

    for idx, (req, gap) in enumerate(ranked_reqs, start=1):
        skill = db.query(Skill).filter_by(id=req.skill_id).first()
        sk_name = skill.name if skill else f"Skill {req.skill_id}"
        st_title = f"Phase {idx}: {sk_name} Proficiency"
        status_val = "completed" if gap <= 0.0 else ("in_progress" if idx == 1 else "not_started")

        db.add(RoadmapItem(
            roadmap_id=new_roadmap.id,
            skill_id=req.skill_id,
            stage_order=idx,
            stage_title=st_title,
            difficulty=1 if gap < 30 else (2 if gap < 60 else 3),
            est_hours=round(max(10.0, gap * 0.4), 1),
            status=status_val,
            prerequisites="" if idx == 1 else f"Phase {idx - 1}"
        ))

    db.commit()
    db.refresh(new_roadmap)
    return get_user_roadmap(user=user, db=db)


@router.put("/items/{item_id}/status", response_model=RoadmapItemResponse)
def update_roadmap_item_status(
    item_id: int,
    payload: RoadmapItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update roadmap stage status (not_started, in_progress, completed)."""
    item = db.query(RoadmapItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap item not found")

    roadmap = db.query(LearningRoadmap).filter_by(id=item.roadmap_id, user_id=user.id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    valid_statuses = ["not_started", "in_progress", "completed"]
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    now = datetime.now(timezone.utc)
    item.status = payload.status
    if payload.status == "in_progress" and not item.started_at:
        item.started_at = now
    elif payload.status == "completed":
        if not item.started_at:
            item.started_at = now
        item.completed_at = now

    db.commit()
    db.refresh(item)

    # If completed, trigger agent cycle
    if payload.status == "completed":
        execute_learner_agent_cycle(
            user_id=user.id,
            event="resource_completed",
            db=db,
            event_payload={"skill_id": item.skill_id}
        )

    sk = db.query(Skill).filter_by(id=item.skill_id).first()
    return RoadmapItemResponse(
        id=item.id,
        roadmap_id=item.roadmap_id,
        skill_id=item.skill_id,
        skill_name=sk.name if sk else "Unknown",
        stage_order=item.stage_order,
        stage_title=item.stage_title,
        difficulty=item.difficulty,
        est_hours=item.est_hours,
        status=item.status,
        prerequisites=item.prerequisites,
        started_at=item.started_at,
        completed_at=item.completed_at
    )

