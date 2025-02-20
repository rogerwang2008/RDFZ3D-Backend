import datetime
from . import models, common, schemas

reported_queue: list[int] = []
reported_data: dict[int, models.GameServerStatus] = {}


def check_server_not_stopped(game_server_id: int, delete_if_not: bool = True) -> bool:
    """
    Check whether a server is reporting its status regularly and is not stopped.
    If not (and ``delete_if_not``), deletes the server from ``reported_data``.
    Does not affect ``reported_queue``!
    :param game_server_id:
    :param delete_if_not:
    :return:
    """
    if game_server_id not in reported_data:
        return False
    if reported_data[game_server_id].last_updated is None:
        result = False
    elif datetime.datetime.now() - reported_data[game_server_id].last_updated < datetime.timedelta(seconds=15):
        result = reported_data[game_server_id].state != common.GameServerStateEnum.STOPPED
    else:
        result = False
    if not result and delete_if_not:
        del reported_data[game_server_id]
    return result


def get_server_status(game_server_id: int) -> models.GameServerStatus:
    """
    Get the status of a server.
    :param game_server_id:
    :return:
    """
    if not check_server_not_stopped(game_server_id):
        return models.GameServerStatus(state=common.GameServerStateEnum.STOPPED, last_updated=None)
    return reported_data[game_server_id]


def report_server_status(game_server_id: int, status: schemas.GameServerReport) -> None:
    """
    Report the status of a server.
    :param game_server_id:
    :param status:
    :return:
    """
    reported_data[game_server_id] = models.GameServerStatus.model_validate(status, from_attributes=True)
    # idx = reported_queue.index(game_server_id)
    # if idx != -1:
    #     reported_queue.pop(idx)
    try:
        reported_queue.remove(game_server_id)
    except ValueError:
        pass
    reported_queue.append(game_server_id)


def cleanup_reported_data() -> None:
    """
    Cleanup the reported data.
    :return:
    """
    while reported_queue and check_server_not_stopped(reported_queue[0]):
        reported_queue.pop(0)
