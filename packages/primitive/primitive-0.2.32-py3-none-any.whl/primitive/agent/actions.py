import sys
from time import sleep

from loguru import logger

from primitive.__about__ import __version__
from primitive.agent.runner import Runner
from primitive.agent.uploader import Uploader
from primitive.db.models import JobRun
from primitive.db.sqlite import wait_for_db
from primitive.utils.actions import BaseAction


class Agent(BaseAction):
    def execute(
        self,
    ):
        logger.remove()
        logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            backtrace=True,
            diagnose=True,
            level="DEBUG" if self.primitive.DEBUG else "INFO",
        )
        logger.info("primitive agent")
        logger.info(f"Version: {__version__}")

        # Wait for monitor to make database
        wait_for_db()

        # Create uploader
        uploader = Uploader(primitive=self.primitive)

        try:
            while True:
                logger.debug("Scanning for files to upload...")
                uploader.scan()

                db_job_run = JobRun.objects.first()

                if not db_job_run:
                    sleep_amount = 5
                    logger.debug(
                        f"No pending job runs... [sleeping {sleep_amount} seconds]"
                    )
                    sleep(sleep_amount)
                    continue

                api_job_run_data = self.primitive.jobs.get_job_run(
                    id=db_job_run.job_run_id,
                )

                if not api_job_run_data or not api_job_run_data.data:
                    logger.error(
                        f"Job Run {db_job_run.job_run_id} not found in API, deleting from DB"
                    )
                    JobRun.objects.filter_by(job_run_id=db_job_run.job_run_id).delete()
                    continue

                api_job_run = api_job_run_data.data["jobRun"]

                logger.debug("Found pending Job Run")
                logger.debug(f"Job Run ID: {api_job_run.get('id')}")
                logger.debug(f"Job Name: {api_job_run.get('name')}")

                runner = Runner(
                    primitive=self.primitive,
                    job_run=api_job_run,
                    # max_log_size=500 * 1024,
                )

                try:
                    runner.setup()
                except Exception as exception:
                    logger.exception(
                        f"Exception while initializing runner: {exception}"
                    )
                    self.primitive.jobs.job_run_update(
                        id=api_job_run.get("id"),
                        status="request_completed",
                        conclusion="failure",
                    )
                    JobRun.objects.filter_by(job_run_id=api_job_run.get("id")).delete()
                    continue

                try:
                    runner.execute()
                except Exception as exception:
                    logger.exception(f"Exception while executing job: {exception}")
                    self.primitive.jobs.job_run_update(
                        id=api_job_run.get("id"),
                        status="request_completed",
                        conclusion="failure",
                    )
                finally:
                    runner.cleanup()

                    # NOTE: also run scan here to force upload of artifacts
                    # This should probably eventually be another daemon?
                    uploader.scan()

                sleep(5)
        except KeyboardInterrupt:
            logger.info("[agent] Stopping primitive agent...")
