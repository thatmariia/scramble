import uvicorn

from fastapi import FastAPI
from .routes import player, court, round, session
from scramble.services.logging import configure_logging, get_log_file

app = FastAPI(title="Scramble API")

# Register routers
app.include_router(session.router, prefix="/session")
app.include_router(player.router, prefix="/player")
app.include_router(court.router, prefix="/court")
app.include_router(round.router, prefix="/round")


def main():
    uvicorn.run("scramble.adapters.api.main:app", reload=True)

configure_logging(get_log_file(), True, True)

if __name__ == "__main__":
    main()
