import datetime
import uvicorn

from fastapi import FastAPI
from .routes import player, court, round, session
from scramble.services.logging import configure_logging

app = FastAPI(title="Scramble API")

# Register routers
app.include_router(session.router, prefix="/session")
app.include_router(player.router, prefix="/player")
app.include_router(court.router, prefix="/court")
app.include_router(round.router, prefix="/round")


def main():
    uvicorn.run("scramble.adapters.api.main:app", reload=True)

log_file = f"logs/{datetime.datetime.now().strftime("logfile_%H_%M_%d_%m_%Y.log")}"
configure_logging(log_file, True, True)

if __name__ == "__main__":
    main()
