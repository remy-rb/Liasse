"""Categories, Correspondents and filing fields on Document.

Revision ID: 0005
Revises: 0004
"""

import uuid

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

# Frozen copy of the defaults at the time of this migration.
DEFAULT_CATEGORIES = [
    "Invoices",
    "Bank",
    "Payslips",
    "Taxes",
    "Health",
    "Insurance",
    "Housing",
    "Vehicle",
    "Contracts",
    "Identity",
]


def upgrade() -> None:
    for table in ("category", "correspondent"):
        op.create_table(
            table,
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("owner.id"), nullable=False, index=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.UniqueConstraint("owner_id", "name"),
        )
    op.add_column("document", sa.Column("title", sa.String(), nullable=True))
    op.add_column(
        "document", sa.Column("category_id", sa.Uuid(), sa.ForeignKey("category.id"), nullable=True)
    )
    op.add_column(
        "document",
        sa.Column("correspondent_id", sa.Uuid(), sa.ForeignKey("correspondent.id"), nullable=True),
    )
    op.add_column("document", sa.Column("document_date", sa.Date(), nullable=True))
    op.add_column("document", sa.Column("classification", sa.JSON(), nullable=True))

    # Owners created before this migration get the default Categories too.
    connection = op.get_bind()
    category = sa.table(
        "category", sa.column("id", sa.Uuid), sa.column("owner_id", sa.Uuid), sa.column("name")
    )
    for (owner_id,) in connection.execute(sa.text("SELECT id FROM owner")):
        op.bulk_insert(
            category,
            [{"id": uuid.uuid4(), "owner_id": owner_id, "name": n} for n in DEFAULT_CATEGORIES],
        )


def downgrade() -> None:
    for column in ("classification", "document_date", "correspondent_id", "category_id", "title"):
        op.drop_column("document", column)
    op.drop_table("correspondent")
    op.drop_table("category")
