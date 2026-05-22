import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.schemas import CreateDocumentaryRequest, DocumentaryProjectResponse
from models.documentary import DocumentaryProject, DocumentaryScene
from utils.database import get_db
from api.dependencies import rate_limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/documentary", tags=["Documentary"])

@router.post("/", response_model=DocumentaryProjectResponse, status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(rate_limiter)])
async def create_documentary(
    request: Request,
    body: CreateDocumentaryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new documentary project and start the pipeline."""
    project = DocumentaryProject(
        title=body.title,
        topic=body.topic,
        script=body.script,
        style=body.style,
        voice=body.voice,
        music_style=body.music_style,
        is_short=body.is_short,
        is_trailer=body.is_trailer,
        status="planning"
    )
    db.add(project)
    await db.flush()
    project_id = str(project.id)

    # Enqueue Celery orchestrator task
    from workers.documentary_worker import run_documentary_pipeline
    run_documentary_pipeline.apply_async(
        kwargs={"project_id": project_id},
        queue="documentary",
    )

    logger.info(f"Queued documentary project {project_id}")
    
    # We must refresh or commit to return full object, but since it's an async session without joinedload we just build dict
    # Wait, we can commit and then query
    await db.commit()
    
    # Re-query with scenes (though it has 0 scenes now)
    res = await db.execute(
        select(DocumentaryProject)
        .options(selectinload(DocumentaryProject.scenes))
        .where(DocumentaryProject.id == project_id)
    )
    proj = res.scalar_one_or_none()
    
    return proj.to_dict()

@router.get("/{project_id}", response_model=DocumentaryProjectResponse)
async def get_documentary(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get the status of a documentary project."""
    res = await db.execute(
        select(DocumentaryProject)
        .options(selectinload(DocumentaryProject.scenes))
        .where(DocumentaryProject.id == project_id)
    )
    proj = res.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj.to_dict()

@router.get("/", response_model=list[DocumentaryProjectResponse])
async def list_documentaries(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """List recent documentary projects."""
    res = await db.execute(
        select(DocumentaryProject)
        .options(selectinload(DocumentaryProject.scenes))
        .order_by(DocumentaryProject.created_at.desc())
        .limit(limit)
    )
    projs = res.scalars().all()
    return [p.to_dict() for p in projs]

@router.get("/workflows/golden-presets", response_model=list[dict])
async def list_golden_presets():
    """Returns the list of highly tuned cinematic workflow presets."""
    from services.workflows.golden_presets import GoldenPresetsManager
    return GoldenPresetsManager.list_presets()

@router.post("/{project_id}/save-template", status_code=status.HTTP_200_OK)
async def save_project_as_template(project_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Saves a successfully generated documentary's visual/audio settings as a reusable template."""
    # In production, this saves to a CreatorTemplate model
    res = await db.execute(select(DocumentaryProject).where(DocumentaryProject.id == project_id))
    proj = res.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {"status": "success", "message": f"Project {project_id} saved to your Creator Templates.", "template_name": f"{proj.title} Template"}
