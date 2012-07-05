import gdata.client
import random
import time

def run(gdataClientFunction, *args, **kwargs):
  """Runs the given gdata client function with exponential backoff

  Args:
    gdataClientFunction: gdata.* function

  Returns:
    Whatever the function returns
  """

  numberOfRetries = 9
  for n in range(0, numberOfRetries):
    try:
      response = gdataClientFunction(*args, **kwargs)
      return response

    except gdata.client.RequestError, error:
      computedTime = (2 ** n) + (random.randint(0, 1000) / 1000)
      time.sleep(max(error.headers.get('Retry-After'), computedTime))

    except:
      time.sleep((2 ** n) + (random.randint(0, 1000) / 1000))

  return None
