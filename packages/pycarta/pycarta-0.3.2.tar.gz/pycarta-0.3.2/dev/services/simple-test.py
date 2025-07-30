import pycarta as pc
import asyncio
import logging
from pprint import pformat
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Calculation(BaseModel):
    lhs: float
    rhs: float

    def __call__(self) -> float:
        return self.lhs + self.rhs


pc.login(profile="sandbox")


myservice = pc.service(
        namespace="test", service="delme",
        groups={"Contextualize:All":"User"}
)

@myservice.get()
def foo():
    """
    Foo Summary

    Returns
    -------
    str

        Simple message.
    """
    return "Hello from 'foo'"

@myservice.get()
def add(*, lhs: float, rhs: float) -> float:
    """
    Adds two numbers together.

    Parameters
    ----------
    lhs (float) : Left operand.

    rhs (float) : Right operand.
    
    Returns
    -------
    float
    """
    logger.debug(f"Calling add(lhs={lhs} ({type(lhs)}), {rhs} ({type(rhs)}))")
    return lhs + rhs

@myservice.post()
def calc(payload: Calculation) -> float:
    f"""
    Constructs then calls a `Calculation` object from the
    contents of the request body.

    body
    ----
    {pformat(Calculation.model_json_schema())}

    Returns
    -------
    float
    """
    return payload()

def main():
    # Do something interesting locally with these codes
    print("foo:", foo())
    print("add(1, 2):", add(lhs=1, rhs=2))


if __name__ == "__main__":
    # The function is unchanged and still usable locally.
    main()
    # Connect to Carta and wait for events. Ctrl-c to stop.
    import asyncio
    print("""
          To download the docs:

          >>> pc.login(profile="sandbox"); agent = pc.get_agent()
          >>> request = agent.get("test/delme/docs")
          >>> html = agent.get("test/delme", params=request.json()).json()["response"]
          >>> with open("docs.html", "w") as ofs:
                  ofs.write(html)
          """)
    # asyncio.run(connect())
    try:
        asyncio.run(pc.service.connect())
    finally:
        myservice.cleanup(force=True)
