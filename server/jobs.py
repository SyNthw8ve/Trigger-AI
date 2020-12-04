from server.trigger_worker import get_driver


def on_compute_user_matches(user_id: str):
    driver = get_driver()
    driver.compute_user_matches(user_id)


def on_compute_user_score(user_id: str, opening_id: str):
    driver = get_driver()
    driver.compute_user_score(user_id, opening_id)


def on_update_user_matches(user_id: str):
    driver = get_driver()
    driver.update_user_matches(user_id)


def on_insert_opening_to_cluster(opening_id: str):
    driver = get_driver()
    driver.insert_opening_to_cluster(opening_id)


def on_update_opening(opening_id: str):
    driver = get_driver()
    driver.update_opening(opening_id)


def on_remove_opening_from_cluster(opening_id: str):
    driver = get_driver()
    driver.remove_opening_from_cluster(opening_id)
