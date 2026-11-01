from typing import Any
import operator
import hashlib
import sqlglot
from sqlglot import exp
from sqlalchemy import and_, or_, not_
from sqlalchemy.sql.elements import ColumnElement
from redis_fastapi.cache_backend import CacheBackend
from analytics.exceptions import AudienceError
from analytics.models import RespondentStat
from analytics.repository import RespRepository
from core.cache import RedisCache

class RespondentStatService:
    """
    Сервис для расчета аналитики по статистике респондентов.
    Отвечает за вероятно безопасный парсинг SQL-условий и расчет процентов пересечения.
    """

    ALLOWED_COLUMNS: set[str] = {"id", "date", "respondent", "sex", "age", "weight"}
    CMP: dict[type[exp.Expression], Any] = {
        exp.EQ: operator.eq,
        exp.NEQ: operator.ne,
        exp.GT: operator.gt,
        exp.GTE: operator.ge,
        exp.LT: operator.lt,
        exp.LTE: operator.le,
    }

    def __init__(
            self,
            resp_repository: RespRepository,
            cache: RedisCache,
    ):
        self.resp_repository = resp_repository
        self.cache = cache

    async def get_percent(self, aud1: str, aud2: str) -> dict[str, float]:
        """
        Вычисляет процент вхождения аудитории 2 в аудиторию 1 на основе средних весов респондентов.
        
        :param aud1: SQL-условие для первой аудитории (например, "Age BETWEEN 18 AND 35")
        :param aud2: SQL-условие для второй аудитории (например, "Sex = 2 AND Age >= 18")
        :return: Словарь с ключом 'percent' и вычисленным значением (float)
        """
        redis_key = self._get_redis_key(aud1, aud2)
        cached = await self.cache.get(redis_key)
        if cached is not None:
            return cached

        sql_1 = self.check_sql(aud1)
        sql_2 = self.check_sql(aud2)

        respondents_1 = await self.resp_repository.get_respondents(sql_1)
        respondents_2 = await self.resp_repository.get_respondents(sql_2)

        data1 = dict(respondents_1)
        data2 = dict(respondents_2)

        intersection_sum = 0
        for resp_id, weigth in data1.items():
            if resp_id in data2:
                intersection_sum += weigth

        total_weigth_aud1 = sum(data1.values())
        if total_weigth_aud1 == 0:
            percent = 0.0
        else:
            percent = float(intersection_sum / total_weigth_aud1)

        await self.cache.set(
            redis_key,
            {"percent": percent},
            ttl=300
        )
        return {"percent": percent}

    def check_sql(self, sql_text: str) -> ColumnElement:
        """
        Проверяет и преобразует строку SQL-условия в безопасное выражение SQLAlchemy.
        
        :param sql_text: Строка условия (например, "Age BETWEEN 18 AND 35")
        :raises AudienceError: Если выражение содержит запрещенные конструкции или превышает лимит длины.
        :return: Готовое выражение SQLAlchemy для передачи в WHERE.
        """
        if len(sql_text) > 400:
            raise AudienceError("Слишком длинное выражение")
        try:
            tree = sqlglot.parse_one(f"SELECT 1 WHERE {sql_text}")
        except sqlglot.ParseError as e:
            raise AudienceError(f"Некорректное выражение: {e}")
        where = tree.args.get("where")
        dangerous_keys = {"union", "join"}
        if where is None or any(tree.args.get(key) is not None for key in dangerous_keys):
            raise AudienceError("Допустимо только условие")
        return self.to_sa(where.this)

    def to_sa(self, node) -> Any:
        """
        Рекурсивно преобразует AST-дерево sqlglot в объекты SQLAlchemy.
        Использует те типы операторов, которые указаны в функции.
        
        :param node: Узел дерева sqlglot.
        :raises AudienceError: Если встречается недопустимый узел.
        :return: Объект SQLAlchemy.
        """
        if isinstance(node, exp.Paren):
            return self.to_sa(node.this)
        if isinstance(node, exp.And):
            return and_(self.to_sa(node.left), self.to_sa(node.right))
        if isinstance(node, exp.Or):
            return or_(self.to_sa(node.left), self.to_sa(node.right))
        if isinstance(node, exp.Not):
            return not_(self.to_sa(node.this))
        for cls, op in self.CMP.items():
            if isinstance(node, cls):
                return op(self.to_sa(node.left), self.to_sa(node.right))
        if isinstance(node, exp.Between):
            return self.to_sa(node.this).between(self.to_sa(node.args["low"]), self.to_sa(node.args["high"]))
        if isinstance(node, exp.In):
            if node.args.get("query"):
                raise AudienceError("Подзапросы запрещены")
            return self.to_sa(node.this).in_([self.to_sa(e) for e in node.expressions])
        if isinstance(node, exp.Column):
            name = node.name.lower()
            if node.table or name not in self.ALLOWED_COLUMNS:
                raise AudienceError(f"Колонка не разрешена: {node.sql()}")
            return getattr(RespondentStat, name)
        if isinstance(node, exp.Literal):
            if node.is_string:
                return node.this
            return float(node.this) if "." in node.this else int(node.this)
        if isinstance(node, exp.Neg):
            return -self.to_sa(node.this)
        raise AudienceError(f"Недопустимая конструкция: {node.key}")

    @staticmethod
    def _get_redis_key(aud1: str, aud2: str) -> str:
        """
        Генерирует безопасный и короткий ключ для Redis.
        Использует хэширование, чтобы избежать проблем с длинными строками или спецсимволами.
        
        :param aud1: Условие первой аудитории.
        :param aud2: Условие второй аудитории.
        :return: Строка ключа Redis.
        """
        strip_aud1 = aud1.strip().lower()
        strip_aud2 = aud2.strip().lower()
        hash_str = f"{strip_aud1}:{strip_aud2}"
        hash_digest = hashlib.md5(hash_str.encode()).hexdigest()
        return f'analytics:percent:{hash_digest}'