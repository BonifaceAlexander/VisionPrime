import re, time, json, os

def slugify_filename(s: str):
    s = s or 'image'
    s = s.lower()
    s = re.sub(r'[^a-z0-9-_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

def log_event(event_type, payload):
    log_dir = os.getenv('IMAGE_STUDIO_LOG_DIR', '/tmp')
    os.makedirs(log_dir, exist_ok=True)
    fn = os.path.join(log_dir, 'image_studio_events.log')
    entry = {'ts': time.time(), 'event': event_type, 'payload': payload}
    try:
        with open(fn, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception:
        pass
