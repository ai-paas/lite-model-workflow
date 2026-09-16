from sqlalchemy import func, select

from app.core.db.models.model_task import ModelTask
from app.core.db.session import SessionLocal
from app.core.db.connect import SessionDepends
from app.schemas.requests.task import ReqModelTaskPageForm, PatchTaskForm, ReqModelTaskForm
from app.schemas.services.model_task import ModelTaskDetailSchema, ModelTaskSchema
from app.utils.uuid import str_to_uuid4


class ModelTaskRepository:
    def __init__(self, db: SessionLocal):
        self.db = db

    def __apply_sort_and_paginate(self, statement: select, form: ReqModelTaskPageForm) -> select:
        """
        정렬 및 페이지네이션 적용
        - 기본 정렬 조건: 생성일시 내림차순
        """
        statement = statement.order_by(ModelTask.created_at.desc())
        statement = statement.offset(form.offset).limit(form.limit)
        return statement

    def __apply_filter(self, statement: select, form: ReqModelTaskForm) -> select:
        """
        필터 적용
        - 모델 이름 필터
        - 최적화 방식 필터
        - 작업 상태 필터
        """
        statement = statement.where(ModelTask.model_name.ilike(f"%{form.model_name_query}%")) \
            if form.model_name_query else statement
        statement = statement.where(ModelTask.task_type.ilike(f"%{form.optimizer_name_query}%")) \
            if form.optimizer_name_query else statement
        if form.task_status:
            # 문자열을 불린으로 변환 ("true", "True", "1" -> True, 그 외 -> False)
            task_status_bool = form.task_status.lower() in ("true", "1", "yes")
            statement = statement.where(ModelTask.progress_status == task_status_bool)
        return statement

    def create_model_task(self, model_task: ModelTask):
        """
        Create model task

        - 모델 저장 요청시 생성

        Args:
            model_task: ModelTask
        Returns:
            ModelTask
        """
        self.db.add(model_task)
        self.db.commit()
        self.db.refresh(model_task)
        return model_task

    def insert_model_task(self, model_task_schema: ModelTaskSchema) -> ModelTaskSchema:
        """
        Create model task

        - 모델 저장 요청시 생성
        - schema를 받아서 sqlalchemy 모델로 변환 후 저장

        Args:
            model_task_schema: ModelTaskSchema
        Returns:
            ModelTaskSchema
        """
        model_task = ModelTask.from_schema(model_task_schema)
        self.db.add(model_task)
        self.db.commit()
        self.db.refresh(model_task)
        return model_task.to_schema()

    def get_task_by_uuid(self, task_uuid: str) -> ModelTaskDetailSchema:
        """
        task uuid로 조회

        Args:
            task_uuid: str
        Returns:
            ModelTaskDetailSchema | None
        """
        uuid = str_to_uuid4(task_uuid)
        statement = select(ModelTask).where(ModelTask.task_uuid == uuid).limit(1)
        result = self.db.execute(statement).scalar_one_or_none()
        return result.to_detail_schema() if result else None

    def get_tasks(self, form: ReqModelTaskForm) -> list[ModelTaskSchema]:
        """
        최적화/경량화 작업 요청 기록
        """
        statement = select(ModelTask)
        statement = self.__apply_filter(statement, form)
        result = self.db.execute(statement).scalars().all()

        return [model_task.to_schema() for model_task in result]

    def get_tasks_paginated(self, form: ReqModelTaskPageForm) -> list[ModelTaskSchema]:
        """
        최적화/경량화 작업 요청 기록
        """
        statement = select(ModelTask)
        statement = self.__apply_filter(statement, form)
        statement = self.__apply_sort_and_paginate(statement, form)
        result = self.db.execute(statement).scalars().all()
        return [model_task.to_schema() for model_task in result]

    def get_tasks_count(self, form: ReqModelTaskForm) -> int:
        """
        최적화/경량화 작업 요청 기록 개수 조회
        """
        statement = select(func.count(ModelTask.pk))
        statement = self.__apply_filter(statement, form)
        return self.db.execute(statement).scalar_one_or_none()

    def patch_task_status(self, task_uuid: str, patch_task_form: PatchTaskForm) -> ModelTaskSchema:
        """
        최적화/경량화 작업 요청 상태 수정
        """
        uuid = str_to_uuid4(task_uuid)
        statement = select(ModelTask).where(ModelTask.task_uuid == uuid).limit(1)
        result = self.db.execute(statement).scalar_one_or_none()
        if result:
            result.progress_status = patch_task_form.progress_status
            result.model_path_output = patch_task_form.path_output_model
            self.db.commit()
            self.db.refresh(result)
        return result.to_schema() if result else None


def get_model_task_repository(db: SessionLocal = SessionDepends):
    return ModelTaskRepository(db)
