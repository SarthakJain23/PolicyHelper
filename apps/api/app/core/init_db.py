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
from app.schemas.role import UserRole

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    {
        "name": UserRole.SUPER_ADMIN.value,
        "description": "Full platform administration, user management, and system settings",
        "permissions": {"all": True},
    },
    {
        "name": UserRole.HR_ADMIN.value,
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
        "name": UserRole.MANAGER.value,
        "description": "Department lead with access to general and manager-level policies",
        "permissions": {
            "chat:access": True,
            "documents:read_manager": True,
        },
    },
    {
        "name": UserRole.EMPLOYEE.value,
        "description": "Standard company employee with access to general company policies",
        "permissions": {
            "chat:access": True,
            "documents:read_general": True,
        },
    },
]

DEFAULT_DEPARTMENTS = [
    {
        "code": "GENERAL",
        "name": "General / Company-Wide",
        "description": "Company-wide department for cross-functional policies",
    },
    {
        "code": "HR",
        "name": "Human Resources",
        "description": "Employee relations, benefits, compensation, and talent management",
    },
    {
        "code": "ENG",
        "name": "Engineering & Technology",
        "description": "Software development, IT infrastructure, and technical operations",
    },
    {
        "code": "FIN",
        "name": "Finance & Accounting",
        "description": "Financial planning, accounting, payroll, and expense management",
    },
    {
        "code": "SALES",
        "name": "Sales & Marketing",
        "description": "Business development, customer acquisition, and marketing operations",
    },
    {
        "code": "LEGAL",
        "name": "Legal & Compliance",
        "description": "Corporate governance, regulatory compliance, contracts, and IP protection",
    },
]

MOCK_USERS = [
    {
        "email": "hr.admin@company.internal",
        "full_name": "Sarah Jenkins",
        "department_code": "HR",
        "roles": [UserRole.HR_ADMIN.value],
        "must_change_password": False,
    },
    {
        "email": "eng.manager@company.internal",
        "full_name": "Alex Rivera",
        "department_code": "ENG",
        "roles": [UserRole.MANAGER.value],
        "must_change_password": False,
    },
    {
        "email": "sales.manager@company.internal",
        "full_name": "David Chen",
        "department_code": "SALES",
        "roles": [UserRole.MANAGER.value],
        "must_change_password": False,
    },
    {
        "email": "john.doe@company.internal",
        "full_name": "John Doe",
        "department_code": "ENG",
        "roles": [UserRole.EMPLOYEE.value],
        "must_change_password": False,
    },
    {
        "email": "jane.smith@company.internal",
        "full_name": "Jane Smith",
        "department_code": "FIN",
        "roles": [UserRole.EMPLOYEE.value],
        "must_change_password": False,
    },
    {
        "email": "alice.wong@company.internal",
        "full_name": "Alice Wong",
        "department_code": "LEGAL",
        "roles": [UserRole.EMPLOYEE.value],
        "must_change_password": False,
    },
    {
        "email": "bob.martinez@company.internal",
        "full_name": "Bob Martinez",
        "department_code": "SALES",
        "roles": [UserRole.EMPLOYEE.value],
        "must_change_password": False,
    },
    {
        "email": "carol.taylor@company.internal",
        "full_name": "Carol Taylor",
        "department_code": "HR",
        "roles": [UserRole.EMPLOYEE.value],
        "must_change_password": False,
    },
]


async def init_db_data() -> None:
    """Seed initial roles, departments, organization, and mock users."""
    async with AsyncSessionLocal() as session:
        # 1. Seed Roles
        role_map: dict[str, Role] = {}
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
                await session.flush()
                role_map[role_data["name"]] = new_role
                logger.info(f"Seeded role: {role_data['name']}")
            else:
                role_map[role_data["name"]] = existing_role

        # 2. Seed Departments
        dept_map: dict[str, Department] = {}
        for dept_data in DEFAULT_DEPARTMENTS:
            dept_stmt = select(Department).where(Department.code == dept_data["code"])
            existing_dept = (await session.execute(dept_stmt)).scalar_one_or_none()
            if not existing_dept:
                new_dept = Department(
                    name=dept_data["name"],
                    code=dept_data["code"],
                    description=dept_data["description"],
                    is_active=True,
                )
                session.add(new_dept)
                await session.flush()
                dept_map[dept_data["code"]] = new_dept
                logger.info(f"Seeded department: {dept_data['code']} - {dept_data['name']}")
            else:
                dept_map[dept_data["code"]] = existing_dept

        default_dept = dept_map.get("GENERAL")

        # 3. Seed Default Organization
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

        # 4. Seed Initial Super Admin
        admin_email = settings.FIRST_SUPERUSER_EMAIL.lower()
        admin_stmt = select(User).where(User.email == admin_email)
        existing_admin = (await session.execute(admin_stmt)).scalar_one_or_none()
        if not existing_admin:
            super_role = role_map[UserRole.SUPER_ADMIN.value]
            admin_user = User(
                email=admin_email,
                full_name=settings.FIRST_SUPERUSER_NAME,
                password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                department_id=default_dept.id if default_dept else None,
                is_active=True,
                must_change_password=False,
                roles=[super_role],
            )
            session.add(admin_user)
            logger.info(f"Seeded initial superuser: {admin_email}")
        else:
            existing_admin.password_hash = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            existing_admin.is_active = True

        # 5. Seed Mock Users
        default_password_hash = get_password_hash("Password123!")
        for mock_data in MOCK_USERS:
            user_stmt = select(User).where(User.email == mock_data["email"].lower())
            existing_user = (await session.execute(user_stmt)).scalar_one_or_none()
            if not existing_user:
                user_roles_list = [role_map[r] for r in mock_data["roles"] if r in role_map]
                target_dept = dept_map.get(mock_data["department_code"])
                mock_user = User(
                    email=mock_data["email"].lower(),
                    full_name=mock_data["full_name"],
                    password_hash=default_password_hash,
                    department_id=target_dept.id if target_dept else None,
                    is_active=True,
                    must_change_password=mock_data.get("must_change_password", False),
                    roles=user_roles_list,
                )
                session.add(mock_user)
                logger.info(f"Seeded mock user: {mock_data['email']} ({', '.join(mock_data['roles'])})")

        await session.commit()
