from fastapi_cache import FastAPICache

def item_key_builder(
    func,
    namespace: str = "",
    request = None,
    response = None,
    args: tuple = None,
    kwargs: dict = None,
):
    course_id = kwargs.get("course_id")
    return f"courses:item:{course_id}"

async def invalidate_cache(course_id: int | None = None):
    """
        Универсальная очистка кэша курсов.
        Если передан course_id, удаляет конкретный курс.
        Всегда очищает списки (namespace).
    """
    if course_id:
        await FastAPICache.clear(key=f"courses:item:{course_id}")
    await FastAPICache.clear(namespace="courses")