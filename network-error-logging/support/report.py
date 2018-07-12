import time
import json
import re

def retrieve_from_stash(request, key, timeout, default_value):
  t0 = time.time()
  while time.time() - t0 < timeout:
    time.sleep(0.5)
    value = request.server.stash.take(key=key)
    if value is not None:
      return value

  return default_value

def main(request, response):
  op = request.GET.first("op");
  key = request.GET.first("reportID")

  try:
    timeout = request.GET.first("timeout")
  except:
    timeout = 0.5
  timeout = float(timeout)

  if op == "retrieve_report":
    return [("Content-Type", "application/json")], retrieve_from_stash(request, key, timeout, json.dumps({'error': 'No such report.' , 'guid' : key}))

  # append new reports
  new_reports = json.loads(request.body)
  with request.server.stash.lock:
    reports = request.server.stash.take(key=key)
    if reports is None:
      reports = []
    else:
      reports = json.loads(reports)
    reports.extend(new_reports)
    request.server.stash.put(key=key, value=json.dumps(reports))

  # return acknowledgement report
  return [("Content-Type", "text/plain")], "Recorded report"
