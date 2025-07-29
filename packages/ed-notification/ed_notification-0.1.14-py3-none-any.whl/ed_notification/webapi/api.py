import uvicorn
from ed_domain.common.exceptions import ApplicationException
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from ed_notification.common.logging_helpers import get_logger
from ed_notification.webapi.common.helpers import GenericResponse
from ed_notification.webapi.controllers import (notification_controller,
                                                rabbitmq_controller)

LOG = get_logger()


class API(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._routers = [
            notification_controller.router,
            rabbitmq_controller.router,
        ]

    @property
    def app(self):
        return self

    def start(self) -> None:
        LOG.info("Starting api...")
        self._include_routers()
        self._contain_exceptions()

        uvicorn.run(self, host="0.0.0.0", port=8000)

    def stop(self) -> None:
        LOG.info("API does not need to be stopped...")

    def _include_routers(self) -> None:
        LOG.info("Including routers...")
        for router in self._routers:
            LOG.info(f"Including router: {router.prefix}")
            self.include_router(router)

    def _contain_exceptions(self) -> None:
        @self.exception_handler(ApplicationException)
        async def application_exception_handler(
            request: Request, exception: ApplicationException
        ) -> JSONResponse:
            LOG.error(
                f"ApplicationException occurred: {exception.message}",
                f"with http status code: {exception.error_code}",
                f"with errors: {exception.errors}",
            )
            return JSONResponse(
                status_code=exception.error_code,
                content=GenericResponse(
                    is_success=False,
                    message=exception.message,
                    errors=exception.errors,
                    data=None,
                ).to_dict(),
            )
