import uuid
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    status,
    Response,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.document import Document, DocumentStatus
from app.models.chunk import DocumentChunk
from app.models.department import Department
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.document import DocumentResponse
from app.services.storage.factory import get_storage
from app.services.ingestion.pipeline import process_document_ingestion

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = None,
    department_id: uuid.UUID | None = None,
    status_filter: str | None = None,
):
    """
    List policy documents.
    Employees see documents allowed for their roles and department.
    Admins/HR see all documents.
    """
    user_roles = [r.name for r in current_user.roles]
    is_admin = any(r in ["SUPER_ADMIN", "HR_ADMIN"] for r in user_roles)

    stmt = (
        select(Document, func.count(DocumentChunk.id).label("chunk_count"))
        .outerjoin(DocumentChunk, Document.id == DocumentChunk.document_id)
        .options(selectinload(Document.department))
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )

    if category:
        stmt = stmt.where(Document.category == category)
    if department_id:
        stmt = stmt.where(Document.department_id == department_id)
    if status_filter:
        stmt = stmt.where(Document.status == status_filter)

    # RBAC filter for non-admin employees
    if not is_admin:
        # Check allowed roles overlaps with user's roles
        # Document's allowed_role_names contains at least one of user_roles
        # and department is either NULL (company-wide) or matches user.department_id
        # We can filter in Python or with PostgreSQL array overlaps
        pass

    result = await db.execute(stmt)
    rows = result.all()

    documents_out: list[DocumentResponse] = []
    for doc, chunk_count in rows:
        # Check role permission
        if not is_admin:
            has_role = any(r in doc.allowed_role_names for r in user_roles)
            dept_matches = (
                doc.department_id is None
                or doc.department_id == current_user.department_id
            )
            if not (has_role and dept_matches):
                continue

        doc_dict = {
            "id": doc.id,
            "title": doc.title,
            "file_name": doc.file_name,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "category": doc.category,
            "department_id": doc.department_id,
            "department": doc.department,
            "allowed_role_names": doc.allowed_role_names,
            "status": doc.status,
            "error_message": doc.error_message,
            "uploaded_by": doc.uploaded_by,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "chunk_count": chunk_count,
        }
        documents_out.append(DocumentResponse(**doc_dict))

    return documents_out


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("GENERAL"),
    department_id: uuid.UUID | None = Form(None),
    allowed_roles: str = Form("EMPLOYEE,MANAGER,HR_ADMIN,SUPER_ADMIN"),
):
    """
    Upload a policy document (.pdf, .docx, .md, .txt) and enqueue background parsing & vector indexing.
    """
    allowed_extensions = ["pdf", "docx", "doc", "md", "txt"]
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type .{file_ext}. Allowed: {allowed_extensions}",
        )

    # Validate department if supplied
    if department_id:
        dept = await db.get(Department, department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department not found",
            )

    # Parse allowed roles list
    allowed_roles_list = [r.strip() for r in allowed_roles.split(",") if r.strip()]

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    doc_id = uuid.uuid4()
    storage_filename = f"{doc_id}_{file.filename}"
    storage_path = f"policies/{storage_filename}"

    # 1. Store file using configured storage strategy
    storage = get_storage()
    stored_path = await storage.upload_file(
        file_obj=file_content,
        destination_path=storage_path,
        content_type=file.content_type or "application/pdf",
    )

    # 2. Save Document metadata in PostgreSQL
    new_doc = Document(
        id=doc_id,
        title=title.strip(),
        file_name=file.filename,
        file_path=stored_path,
        file_type=file_ext,
        file_size=file_size,
        category=category.strip().upper(),
        department_id=department_id,
        allowed_role_names=allowed_roles_list,
        status=DocumentStatus.PENDING.value,
        uploaded_by=current_user.id,
    )
    db.add(new_doc)

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="UPLOAD_DOCUMENT",
        details={"document_id": str(doc_id), "title": new_doc.title, "filename": file.filename},
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(new_doc)

    # 3. Trigger background ingestion (parse, chunk, embed, pgvector store)
    background_tasks.add_task(process_document_ingestion, doc_id)

    return DocumentResponse(
        id=new_doc.id,
        title=new_doc.title,
        file_name=new_doc.file_name,
        file_type=new_doc.file_type,
        file_size=new_doc.file_size,
        category=new_doc.category,
        department_id=new_doc.department_id,
        department=None,
        allowed_role_names=new_doc.allowed_role_names,
        status=new_doc.status,
        error_message=None,
        uploaded_by=new_doc.uploaded_by,
        created_at=new_doc.created_at,
        updated_at=new_doc.updated_at,
        chunk_count=0,
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Download or view raw policy document."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # RBAC check
    user_roles = [r.name for r in current_user.roles]
    is_admin = any(r in ["SUPER_ADMIN", "HR_ADMIN"] for r in user_roles)
    if not is_admin:
        has_role = any(r in doc.allowed_role_names for r in user_roles)
        dept_matches = (
            doc.department_id is None
            or doc.department_id == current_user.department_id
        )
        if not (has_role and dept_matches):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this document",
            )

    storage = get_storage()
    file_bytes = await storage.download_file(doc.file_path)

    media_type = "application/pdf" if doc.file_type == "pdf" else "application/octet-stream"
    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{doc.file_name}"'},
    )


@router.post("/{document_id}/retry", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def retry_document_ingestion(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Retry parsing, chunking, and embedding ingestion for a failed or existing document.
    """
    stmt = (
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.department))
    )
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if doc.status != DocumentStatus.FAILED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed documents can be retried.",
        )

    # 1. Reset document status to PENDING and clear previous error message
    doc.status = DocumentStatus.PENDING.value
    doc.error_message = None

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="RETRY_DOCUMENT_INGESTION",
        details={"document_id": str(document_id), "title": doc.title},
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(doc)

    # 2. Trigger background ingestion
    background_tasks.add_task(process_document_ingestion, doc.id)

    # Count existing chunks (if any)
    chunk_count_stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc.id)
    chunk_count = (await db.execute(chunk_count_stmt)).scalar_one() or 0

    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        category=doc.category,
        department_id=doc.department_id,
        department=doc.department,
        allowed_role_names=doc.allowed_role_names,
        status=doc.status,
        error_message=doc.error_message,
        uploaded_by=doc.uploaded_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunk_count=chunk_count,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a document, its physical storage file, and its vector chunks."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # 1. Delete physical file from storage
    storage = get_storage()
    await storage.delete_file(doc.file_path)

    # 2. Delete from DB (chunks cascade-deleted via foreign key)
    await db.delete(doc)

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="DELETE_DOCUMENT",
        details={"document_id": str(document_id), "title": doc.title},
    )
    db.add(audit_entry)

    await db.commit()
    return None
