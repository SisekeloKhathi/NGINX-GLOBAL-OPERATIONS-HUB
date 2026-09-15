def _eval(condition, row, description):
    comp = condition.get("comparator")
    th = condition.get("threshold")
    if comp == "above":
        return row[0] > th, row[0], th
    if comp == "below":
        return row[0] < th, row[0], th
    if comp == "expression":
        cols = [d[0] for d in description]
        ctx = {col: val for col, val in zip(cols, row)}
        ctx["abs"] = abs
        result = bool(eval(condition["expression"], {"__builtins__": {}}, ctx))
        observed = next((v for v in ctx.values() if isinstance(v, (int, float))), None)
        return result, observed, None
    return False, None, None

def run_sql_trigger(trigger_config, rule, conn, state):
    with conn.cursor() as cur:
        cur.execute(trigger_config["query"])
        row = cur.fetchone()
        if row is None:
            return False, None, "no rows"
        return _eval(rule.condition, row, cur.description)
