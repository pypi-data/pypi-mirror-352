"多条件构造器"


def splicing_conditions(model, sql, query):
    for i in query.model_dump(exclude_none=True).keys():
        if isinstance(getattr(query, i), list):
            sql = sql.where(getattr(model, i) in (getattr(query, i)))
        if isinstance(getattr(query, i), str):
            sql = sql.where(getattr(model, i) % f"%{getattr(query, i)}%")
        else:
            sql = sql.where(getattr(model, i) == getattr(query, i))
    return sql


def splicing_conditions_dict(model, sql, query: dict, useAll=False):
    try:
        for i in query.keys():
            try:
                if not query[i]:
                    continue
                if useAll and query[i] == "all":
                    continue
                if query[i] in ["true", "false"]:
                    sql = sql.where(
                        getattr(model, i) == (1 if query[i] == "true" else 0)
                    )
                elif isinstance(query[i], list):
                    sql = sql.where(getattr(model, i) in query[i])
                elif isinstance(query[i], str):
                    if query[i] == "":
                        continue
                    sql = sql.where(getattr(model, i) % f"%{query[i]}%")
                else:
                    sql = sql.where(getattr(model, i) == query[i])
            except AttributeError:
                # 如果模型没有这个属性，则跳过
                pass
    except AttributeError:
        return sql
    return sql
