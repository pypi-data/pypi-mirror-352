#!/usr/bin/env python
import os, sys, logging, argparse, threading, queue, time, signal, itertools, collections
from google.cloud import storage
from google.api_core.exceptions import NotFound

# ── CONFIG ────────────────────────────────────────────────────
class BackupConfig:
    def __init__(self, args=None):
        parser = argparse.ArgumentParser(description="Backup uploader config")
        parser.add_argument("--bucket", help="GCS bucket name")
        parser.add_argument("--chunk-size", type=int, help="Chunk size in bytes")
        parser.add_argument("--num-workers", type=int, help="Number of upload workers")
        parser.add_argument("--queue-max", type=int, help="Max upload queue size")
        parser.add_argument("--progress-every", type=int, help="Progress reporting interval")
        parser.add_argument("--max-retries", type=int, help="Max retries per chunk")
        parser.add_argument("--compose-factor", type=int, help="Max parts to compose at once")
        parser.add_argument("final_object", help="Target object name in GCS")

        parsed = parser.parse_args(args)

        self.FINAL_OBJECT = parsed.final_object
        self.BUCKET_NAME = parsed.bucket or os.getenv("BUCKET_NAME", "analog-backups")
        self.CHUNK_SIZE = parsed.chunk_size or int(os.getenv("CHUNK_SIZE", 1024 * 1024 * 250))
        self.NUM_WORKERS = parsed.num_workers or int(os.getenv("NUM_WORKERS", 10))
        self.QUEUE_MAX = parsed.queue_max or int(os.getenv("QUEUE_MAX", 5))
        self.PROGRESS_EVERY = parsed.progress_every or int(os.getenv("PROGRESS_EVERY", 15))
        self.MAX_RETRIES = parsed.max_retries or int(os.getenv("MAX_RETRIES", 5))
        self.COMPOSE_FACTOR = parsed.compose_factor or int(os.getenv("COMPOSE_FACTOR", 32))

# Parse configuration
config = BackupConfig()
FINAL_OBJECT = config.FINAL_OBJECT
BUCKET_NAME = config.BUCKET_NAME
CHUNK_SIZE = config.CHUNK_SIZE
NUM_WORKERS = config.NUM_WORKERS
QUEUE_MAX = config.QUEUE_MAX
PROGRESS_EVERY = config.PROGRESS_EVERY
MAX_RETRIES = config.MAX_RETRIES
COMPOSE_FACTOR = config.COMPOSE_FACTOR

# ── Globals ───────────────────────────────────────────────────
q                   = queue.Queue(maxsize=QUEUE_MAX)
q_merge             = queue.Queue(maxsize=QUEUE_MAX)
bytes_uploaded      = 0
lock_record         = threading.Lock()
lock_bytes_uploaded = threading.Lock()
stop_event          = threading.Event()
failed_event        = threading.Event()
retries             = collections.defaultdict(int)
parts_by_level      = collections.defaultdict(list)

client              = storage.Client()
bucket              = client.bucket(BUCKET_NAME)

# ── Logging ──────────────────────────────────────────────

class LoggerManager:
    def __init__(self, name="MultiThreadLogger", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(level)  # Match the logger's level
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s'
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger

# -- handling

def record_upload(level, idx):
    if level not in parts_by_level:
        parts_by_level[level] = []
    parts_by_level[level].append(idx)

def merge_levels():
    merged_levels = []
    parts_by_level_copy = dict(parts_by_level)
    for level, parts in parts_by_level_copy.items():
        if len(parts_by_level_copy[level]) == 0:
            continue
        parts_by_level[level].sort()
        blobs = [bucket.blob(f"{FINAL_OBJECT}.L{level}.part{num}") for num in parts_by_level[level]]
        res_blob_name = f"{FINAL_OBJECT}.L{level}.merged"
        if len(blobs) > 1:
            destionation = bucket.blob(res_blob_name)
            destionation.compose(blobs)
            bucket.delete_blobs(blobs)
        elif len(blobs) == 1:
            bucket.rename_blob(blobs[0], res_blob_name)
        logger.debug(f"Merged {level} with {len(blobs)} parts to {FINAL_OBJECT}")
        parts_by_level.pop(level)
        merged_levels.append(res_blob_name)
    return merged_levels


def delete_parts():
    merged_levels = []
    parts_by_level_copy = dict(parts_by_level)
    for level, parts in parts_by_level_copy.items():
        if len(parts_by_level_copy[level]) == 0:
            continue
        blobs = [bucket.blob(f"{FINAL_OBJECT}.L{level}.part{num}") for num in parts_by_level[level]]
        for blob in blobs:
            try:
                bucket.delete_blobs(blobs)
            except NotFound as e:
                continue
        logger.error(f"All uploaded blobs were deleted")

# -- ComposeThread

class ComposeThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=False)
        self.logger = logger

    def run(self):
        while not stop_event.is_set():
            try:
                item = q_merge.get(timeout=1)
                if item != None:
                    self.logger.debug(f"[{self.name}] Accepted job {item}")
            except queue.Empty:
                self.logger.debug(f"[{self.name}] - queue empty")
                continue
            if item is None:
                self.logger.debug(f"[{self.name}] Exiting")
                break
            self.merge_parts(level=0)
            q_merge.task_done()

    def merge_parts(self, level):
        global parts_by_level
        if level not in parts_by_level or len(parts_by_level[level]) < COMPOSE_FACTOR:
            return
        self.logger.debug(f"[{self.name}] - level {level} - {len(parts_by_level[level])} parts")
        parts_by_level[level].sort()
        nums = parts_by_level[level]
        for num in nums:
            if num % COMPOSE_FACTOR == 0:
                if all( (num + i) in nums for i in range(COMPOSE_FACTOR) ):
                    group = [num + i for i in range(COMPOSE_FACTOR)]
                    blobs = [bucket.blob(f"{FINAL_OBJECT}.L{level}.part{num}") for num in group]
                    destionation_blob_name = f"{FINAL_OBJECT}.L{level + 1}.part{num // COMPOSE_FACTOR}"
                    destination = bucket.blob(destionation_blob_name)
                    self.logger.debug(f"[{self.name}] Composing {destionation_blob_name} from {[f'{FINAL_OBJECT}.L{level}.part{num}' for num in group]}")
                    destination.compose(
                        blobs
                    )
                    with lock_record:
                        record_upload(level + 1, num // COMPOSE_FACTOR)
                    for idx in group:
                        parts_by_level[level].remove(idx)
                    bucket.delete_blobs(blobs)
        self.merge_parts(level + 1)


# ── Worker ───────────────────────────────────────────────────
class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=False)
        self.idx = -1
        self.logger = logger

    def run(self):
        while not stop_event.is_set():
            try:
                item = q.get(timeout=1)
                if item != None:
                    self.logger.debug(f"Accepted job {item[0]}")
            except queue.Empty:
                self.logger.debug("queue empty")
                continue
            if item is None:
                self.logger.debug(f"[{self.name}] Exiting")
                break
            self.idx, data = item
            part_name = self.generate_part_name(0, self.idx)
            try:
                self.logger.debug(f"Uploading: {part_name}")
                bucket.blob(part_name).upload_from_string(data)
                self.logger.debug(f"Uploaded: {part_name}")
                with lock_bytes_uploaded:
                    global bytes_uploaded
                    bytes_uploaded += len(data)
                with lock_record:
                    record_upload(0, self.idx)
                q_merge.put(self.idx)
            except Exception as e:
                self.logger.error(f"Exception {self.name} {item[0]} - {e.__class__.__name__}: {e}")
                retries[self.idx] += 1
                self.logger.error(f"Retry idx: {self.idx} attemp: {retries[self.idx]}")
                if retries[self.idx] >= MAX_RETRIES:
                    failed_event.set(); stop_event.set()
                else:
                    q.put(item); time.sleep(1);
            finally:
                q.task_done()
        logger.debug("Worker finished proccessing queue - exiting")

    @staticmethod
    def generate_part_name(level, idx):
        return f"{FINAL_OBJECT}.L{level}.part{idx}"



# ── Progress reporter ────────────────────────────────────────
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def reporter():
    while not stop_event.is_set():
        time.sleep(PROGRESS_EVERY)
        with lock_bytes_uploaded:
            res = sizeof_fmt(bytes_uploaded)
            logger.info(f"Uploaded {res}")

# ── Graceful abort ───────────────────────────────────────────
def abort(sig, frm):
    logger.error(f"Received abort sig: {sig} frm: {frm}")
    stop_event.set()
    time.sleep(5)
    logger.error(f"Deleting parts...")
    delete_parts()
    logger.error(f"Uploaded parts deleted.")
    exit(1)

# ── Main logic ──────────────────────────────────────────────

def run_main_logic():
    # ── Launch threads ───────────────────────────────────────────
    threads=[Worker() for _ in range(NUM_WORKERS)]
    logger.debug(threads)
    for t in threads: t.start()
    logger.debug("Threads started …")
    # ── Reporter thread ────────────────────────────────────────
    reporter_thr = threading.Thread(target=reporter, daemon=True)
    reporter_thr.start()
    # ── Compose thread ───────────────────────────────────────────
    compose_thr = ComposeThread()
    compose_thr.start()

    # ── Feed stdin into queue ───────────────────────────────────
    for idx in itertools.count():
        chunk = sys.stdin.buffer.read(CHUNK_SIZE)
        if not chunk or stop_event.is_set():
            logger.error("Stop event is set, exiting!")
            break
        logger.debug(f"sending to queue - idx: {idx}")
        q.put((idx, chunk))

    # ── Finish / cleanup ─────────────────────────────────────────
    logger.debug("Waiting for all items to be processed …")
    q.join()
    logger.debug("Stopping threads …")
    for _ in threads: q.put(None)
    for t in threads: t.join()
    logger.debug("Waiting for compose thread …")
    q_merge.put(None)
    compose_thr.join()
    logger.debug("Threads stopped …")

    # fold remaining hierarchy to single object
    logger.debug(parts_by_level)
    merged = merge_levels()
    logger.debug(merged)
    # rename top object to FINAL_OBJECT if needed
    if len(merged) > 1:
        blobs = [ bucket.blob(m) for m in merged ]
        destionation = bucket.blob(FINAL_OBJECT)
        destionation.compose(blobs[::-1])
        bucket.delete_blobs(blobs)
        logger.debug(f"Composed {FINAL_OBJECT} from {', '.join(merged)}")
    elif len(merged) == 1:
        blob = bucket.blob(merged[0])
        bucket.rename_blob(blob, FINAL_OBJECT)
        logger.debug(f"Renamed {merged[0]} to {FINAL_OBJECT}")

if __name__ == "__main__":

    signal.signal(signal.SIGINT, abort)
    signal.signal(signal.SIGTERM, abort)

    log_level = getattr(logging, "DEBUG")
    logger = LoggerManager(level=log_level).get_logger()

    logger.debug(f"CHUNK_SIZE: {CHUNK_SIZE}")
    logger.debug(f"FINAL_OBJECT: {FINAL_OBJECT}")
    logger.debug(f"BUCKET_NAME: {BUCKET_NAME}")
    logger.debug(f"NUM_WORKERS: {NUM_WORKERS}")
    logger.debug(f"QUEUE_MAX: {QUEUE_MAX}")
    logger.debug(f"PROGRESS_EVERY: {PROGRESS_EVERY}")
    logger.debug(f"MAX_RETRIES: {MAX_RETRIES}")
    logger.debug(f"COMPOSE_FACTOR: {COMPOSE_FACTOR}")
    # ── Check bucket ───────────────────────────────────────────
    try:
        bucket.reload()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

    print(f"Uploading to gs://{BUCKET_NAME}/{FINAL_OBJECT} …")
    run_main_logic()
    print(f"Upload complete: gs://{BUCKET_NAME}/{FINAL_OBJECT}")
