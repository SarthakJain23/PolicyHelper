import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.department import Department
from app.models.user import User
from app.models.organization import Organization

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    {
        "name": "SUPER_ADMIN",
        "description": "Full platform administration, user management, and system settings",
        "permissions": {"all": True},
    },
    {
        "name": "HR_ADMIN",
        "description": "Policy document management, indexing, user invitations, and analytics",
        "permissions": {
            "documents:create": True,
            "documents:read": True,
            "documents:update": True,
            "documents:delete": True,
            "users:create": True,
            "users:read": True,
            "departments:create": True,
            "departments:read": True,
            "departments:update": True,
        },
    },
    {
        "name": "MANAGER",
        "description": "Department lead with access to general and manager-level policies",
        "permissions": {
            "chat:access": True,
            "documents:read_manager": True,
        },
    },
    {
        "name": "EMPLOYEE",
        "description": "Standard company employee with access to general company policies",
        "permissions": {
            "chat:access": True,
            "documents:read_general": True,
        },
    },
]


async def init_db_data() -> None:
    """Seed initial roles, departments, and default Super Admin user."""
    async with AsyncSessionLocal() as session:
        # 1. Seed Roles
        for role_data in DEFAULT_ROLES:
            stmt = select(Role).where(Role.name == role_data["name"])
            existing_role = (await session.execute(stmt)).scalar_one_or_none()
            if not existing_role:
                new_role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_data["permissions"],
                )
                session.add(new_role)
                logger.info(f"Seeded role: {role_data['name']}")

        # 2. Seed Default Department
        dept_stmt = select(Department).where(Department.code == "GENERAL")
        default_dept = (await session.execute(dept_stmt)).scalar_one_or_none()
        if not default_dept:
            default_dept = Department(
                name="General / Company-Wide",
                code="GENERAL",
                description="Company-wide department for cross-functional policies",
                is_active=True,
            )
            session.add(default_dept)
            logger.info("Seeded default department: GENERAL")

        await session.flush()

        # 3. Seed Initial Super Admin
        admin_stmt = select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL.lower())
        existing_admin = (await session.execute(admin_stmt)).scalar_one_or_none()
        if not existing_admin:
            super_role_stmt = select(Role).where(Role.name == "SUPER_ADMIN")
            super_role = (await session.execute(super_role_stmt)).scalar_one()

            admin_user = User(
                email=settings.FIRST_SUPERUSER_EMAIL.lower(),
                full_name=settings.FIRST_SUPERUSER_NAME,
                password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                department_id=default_dept.id,
                is_active=True,
                must_change_password=False,
                roles=[super_role],
            )
            session.add(admin_user)
            logger.info(f"Seeded initial superuser: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            # Ensure password hash is fresh for default super admin
            existing_admin.password_hash = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            existing_admin.is_active = True

        # 4. Seed Default Organization
        org_stmt = select(Organization).where(Organization.slug == "default")
        default_org = (await session.execute(org_stmt)).scalar_one_or_none()
        if not default_org:
            default_org = Organization(
                name="Default Organization",
                slug="default",
                is_active=True,
            )
            session.add(default_org)
            await session.flush()
            logger.info("Seeded default organization: Default Organization")

        await session.commit()
