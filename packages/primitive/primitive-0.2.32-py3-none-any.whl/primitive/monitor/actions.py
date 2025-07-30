import sys
from time import sleep
from typing import Optional

import psutil
from loguru import logger

from primitive.__about__ import __version__
from primitive.db.models import JobRun
from primitive.db.sqlite import init, wait_for_db
from primitive.utils.actions import BaseAction
from primitive.utils.exceptions import P_CLI_100


class Monitor(BaseAction):
    def start(self, job_run_id: Optional[str] = None):
        logger.remove()
        logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            backtrace=True,
            diagnose=True,
            level="DEBUG" if self.primitive.DEBUG else "INFO",
        )
        logger.info("primitive monitor")
        logger.info(f"Version: {__version__}")

        # TODO: tighten logic for determining if we're running in a container
        RUNNING_IN_CONTAINER = False
        if job_run_id is not None:
            logger.info("Running in container...")
            RUNNING_IN_CONTAINER = True

        # can't check if if it is a container
        if not RUNNING_IN_CONTAINER:
            try:
                # hey stupid:
                # do not set is_available to True here, it will mess up the reservation logic
                # only set is_available after we've checked that no active reservation is present
                # setting is_available of the parent also effects the children,
                # which may have active reservations as well
                self.primitive.hardware.check_in_http(is_online=True)
            except Exception as exception:
                logger.exception(f"Error checking in hardware: {exception}")
                sys.exit(1)

        # Initialize the database
        init()
        wait_for_db()

        try:
            if job_run_id is not None:
                if not JobRun.objects.filter_by(job_run_id=job_run_id).exists():
                    logger.debug(f"Job run {job_run_id} does not exist in database.")
                    logger.debug(f"Creating job run in database: {job_run_id}")
                    JobRun.objects.create(job_run_id=job_run_id, pid=None)

            active_reservation_id = None
            active_reservation_pk = None

            while True:
                # FIRST, check for jobs in the database that are running
                db_job_runs = JobRun.objects.all()
                for job_run in db_job_runs:
                    # first check if the job run completed already
                    status = self.primitive.jobs.get_job_status(job_run.job_run_id)
                    if status is None or status.data is None:
                        logger.error(
                            f"Error fetching status of <JobRun {job_run.job_run_id}>."
                        )
                        continue

                    status_value = status.data["jobRun"]["status"]
                    if status_value == "completed":
                        logger.debug(
                            f"Job run {job_run.job_run_id} is completed. Removing from database."
                        )
                        JobRun.objects.filter_by(job_run_id=job_run.job_run_id).delete()
                        continue

                    if job_run.pid is None:
                        pid_sleep_amount = 0.1
                        logger.debug(
                            f"Job run {job_run.job_run_id} has no PID. Agent has not started."
                        )
                        logger.debug(
                            f"Sleeping {pid_sleep_amount} seconds before checking again..."
                        )
                        sleep(pid_sleep_amount)
                        pid_sleep_amount += 0.1
                        continue

                    logger.debug(
                        f"Checking process PID {job_run.pid} for JobRun {job_run.job_run_id}..."
                    )

                    status = self.primitive.jobs.get_job_status(job_run.job_run_id)
                    if status is None or status.data is None:
                        logger.error(
                            f"Error fetching status of <JobRun {job_run.job_run_id}>."
                        )
                        continue

                    status_value = status.data["jobRun"]["status"]
                    conclusion_value = status.data["jobRun"]["conclusion"]

                    logger.debug(f"- Status: {status_value}")
                    logger.debug(f"- Conclusion: {conclusion_value}")

                    try:
                        parent = psutil.Process(job_run.pid)
                    except psutil.NoSuchProcess:
                        logger.debug("Process not found")
                        continue

                    children = parent.children(recursive=True)

                    if status_value == "completed" and conclusion_value == "cancelled":
                        logger.warning("Job cancelled by user")
                        for child in children:
                            logger.debug(f"Killing child process {child.pid}...")
                            child.kill()

                        logger.debug(f"Killing parent process {parent.pid}...")
                        parent.kill()

                    if status != "completed":
                        sleep(1)
                        continue

                if RUNNING_IN_CONTAINER:
                    if len(db_job_runs) == 0:
                        # if we get here and we're running in a container,
                        # it means the job run is complete and there is nothing left in the database
                        # so we can exit
                        logger.debug("Running in container, initial job complete.")
                        sys.exit(0)
                    else:
                        continue

                # Second, check for active reservations
                hardware = self.primitive.hardware.get_own_hardware_details()
                if hardware["activeReservation"]:
                    if (
                        hardware["activeReservation"]["id"] != active_reservation_id
                        or hardware["activeReservation"]["pk"] != active_reservation_pk
                    ):
                        logger.info("New reservation for this hardware.")
                        active_reservation_id = hardware["activeReservation"]["id"]
                        active_reservation_pk = hardware["activeReservation"]["pk"]
                        logger.debug("Active Reservation:")
                        logger.debug(f"Node ID: {active_reservation_id}")
                        logger.debug(f"PK: {active_reservation_pk}")

                        logger.debug("Running pre provisioning steps for reservation.")
                        self.primitive.provisioning.add_reservation_authorized_keys(
                            reservation_id=active_reservation_id
                        )

                if not active_reservation_id:
                    self.primitive.hardware.check_in_http(
                        is_available=True, is_online=True
                    )
                    logger.debug("Syncing children...")
                    self.primitive.hardware._sync_children(hardware=hardware)

                    sleep_amount = 5
                    logger.debug(
                        f"No active reservation found... [sleeping {sleep_amount} seconds]"
                    )
                    sleep(sleep_amount)
                    continue
                else:
                    if (
                        hardware["activeReservation"] is None
                        and active_reservation_id is not None
                        # and hardware["isAvailable"] NOTE: this condition was causing the CLI to get into a loop searching for job runs
                    ):
                        logger.debug("Previous Reservation is Complete:")
                        logger.debug(f"Node ID: {active_reservation_id}")
                        logger.debug(f"PK: {active_reservation_pk}")
                        logger.debug(
                            "Running cleanup provisioning steps for reservation."
                        )
                        self.primitive.provisioning.remove_reservation_authorized_keys(
                            reservation_id=active_reservation_id
                        )
                        active_reservation_id = None
                        active_reservation_pk = None

                # Third, see if the active reservation has any pending job runs
                job_runs_for_reservation = self.primitive.jobs.get_job_runs(
                    status="pending", first=1, reservation_id=active_reservation_id
                )

                if (
                    job_runs_for_reservation is None
                    or job_runs_for_reservation.data is None
                ):
                    logger.error("Error fetching job runs.")
                    sleep_amount = 5
                    logger.debug(
                        f"Error fetching job runs... [sleeping {sleep_amount} seconds]"
                    )
                    sleep(sleep_amount)
                    continue

                pending_job_runs = [
                    edge["node"]
                    for edge in job_runs_for_reservation.data["jobRuns"]["edges"]
                ]

                if not pending_job_runs:
                    self.primitive.hardware.check_in_http(
                        is_available=False, is_online=True
                    )
                    sleep_amount = 5
                    logger.debug(
                        f"Waiting for Job Runs... [sleeping {sleep_amount} seconds]"
                    )
                    sleep(sleep_amount)
                    continue

                # If we did find a pending job run, check if it exists in the database
                # and create it if it doesn't.
                # This will trigger the agent to start the job run.
                job_run = pending_job_runs[0]
                if not JobRun.objects.filter_by(job_run_id=job_run["id"]).exists():
                    JobRun.objects.create(job_run_id=job_run["id"], pid=None)
                    logger.debug(f"Creating job run in database: {job_run['id']}")

        except KeyboardInterrupt:
            logger.info("Stopping primitive monitor...")
            try:
                if not RUNNING_IN_CONTAINER:
                    self.primitive.hardware.check_in_http(
                        is_available=False, is_online=False, stopping_agent=True
                    )

            except P_CLI_100 as exception:
                logger.error("Error stopping primitive monitor.")
                logger.error(str(exception))
            sys.exit()
