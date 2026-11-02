# aud-metrics-api

API для расчёта метрик аудиторий. Стек: FastAPI, PostgreSQL, Redis

## Запуск

```bash
git clone https://github.com/Binlop/aud-metrics-api.git
cd aud-metrics-api
docker compose up
```

При первом запуске автоматически произойдёт следующее:

1. поднимутся PostgreSQL и Redis;
2. применятся миграции;
3. загрузятся данные в базу через отдельный сервис в docker-compose;
4. запустится API.

## Пример запроса

```
http://127.0.0.1:80/getPercent?audience1=Age%20BETWEEN%2018%20AND%2035&audience2=Sex%20%3D%202%20AND%20Age%20%3E%3D%2019
```

```bash
curl "http://127.0.0.1/getPercent?audience1=Age%20BETWEEN%2018%20AND%2035&audience2=Sex%20%3D%202%20AND%20Age%20%3E%3D%2019"
```

Параметры:

| Параметр    | Описание                                      | Пример                  |
|-------------|-----------------------------------------------|-------------------------|
| `audience1` | Условие, описывающее первую аудиторию         | `Age BETWEEN 18 AND 35` |
| `audience2` | Условие, описывающее вторую аудиторию         | `Sex = 2 AND Age >= 19` |

Запросы кэшируются в Redis (просто было интересно добавить опционально)
