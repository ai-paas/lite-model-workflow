from sqlalchemy import JSON, String
from sqlalchemy.orm import MappedColumn, mapped_column

from app.core.db.models.base import IDwithTimestamp
from app.schemas.services.optimizer_info import OptimizerInfo as OptimizerInfoSchema


class OptimizerInfo(IDwithTimestamp):
    __tablename__ = "optimizer_info"

    optimizer_name: MappedColumn[str] = mapped_column(String, nullable=False)
    accelerator: MappedColumn[str] = mapped_column(String, nullable=False)
    argument: MappedColumn[dict] = mapped_column(JSON, nullable=False)
    optimizer_type: MappedColumn[str] = mapped_column(String, nullable=True)

    def to_schema(self) -> OptimizerInfoSchema:
        return OptimizerInfoSchema(
            id=self.id,
            optimizer_name=self.optimizer_name,
            accelerator=self.accelerator,
            argument=self.argument,
            optimizer_type=self.optimizer_type,
        )

    @classmethod
    def from_schema(cls, optimizer_info_schema: OptimizerInfoSchema) -> "OptimizerInfo":
        return cls(
            optimizer_name=optimizer_info_schema.optimizer_name,
            accelerator=optimizer_info_schema.accelerator,
            argument=optimizer_info_schema.argument,
            optimizer_type=optimizer_info_schema.optimizer_type,
        )
