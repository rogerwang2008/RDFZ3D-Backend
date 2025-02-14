from apscheduler.schedulers.asyncio import AsyncIOScheduler


import game_server.status.crud

scheduler = AsyncIOScheduler()
scheduler.add_job(game_server.status.crud.cleanup_reported_data, "interval", seconds=600)

