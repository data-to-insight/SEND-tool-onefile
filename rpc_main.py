from prpc_python import RpcApp


@app.call(name="sum")
def sum_two(a: int, b: int) -> int:
    return a + b
