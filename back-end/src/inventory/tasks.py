import random
import time
import uuid

from src.celery_app import celery_app


@celery_app.task(
    bind=True,
    max_retries=5,
    name="inventory.run_inventory_event",
)
def run_inventory_event(
    self,
    event_type: str,
):
    """Asynchronous processing of inventory events."""
    current_retry = self.request.retries
    task_id = self.request.id

    print(
        f"[Celery][run_inventory_event] "
        f"TASK_ID={task_id} EVENT_TYPE={event_type} "
    )
    # 50% chance of failure -> simulation
    if random.random() < 0.5:
        # Exponential backoff with 1, 2, 4... seconds between retries
        countdown = 2**current_retry if current_retry > 0 else 1
        raise self.retry(
            exc=RuntimeError("Falha simulada no processamento de inventário."),
            countdown=countdown,
        )

    sleep_seconds = random.randint(1, 5)  # simulates throttling
    print(
        f"[Celery][run_inventory_event] task_id={task_id} "
        f"sleeping_for={sleep_seconds}s"
    )
    time.sleep(sleep_seconds)

    print(
        f"[Celery][run_inventory_event] task_id={task_id} "
        f"SUCCESS retry={current_retry} sleep_seconds={sleep_seconds}"
    )
