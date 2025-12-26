import logging
from typing import List, Dict, Optional, Any
from src.database.db_connector import get_connection

logger = logging.getLogger(__name__)

def _to_int_or_none(value: Any) -> Optional[int]:
    if value in (None, "", "-"):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def _to_str_or_none(value: Any) -> Optional[str]:
    return str(value) if value else None

def db_writer_results(match_data_list: List[Dict], category: str):
    """Écrit les résultats des matchs dans la base de données."""
    if not match_data_list:
        return

    table_name = "matches"
    insert_sql = f"""
        INSERT INTO {table_name} 
            (pool_id, match_date, team_1_name, team_1_score, team_2_name, team_2_score, 
             match_link, competition, round)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            team_1_score = VALUES(team_1_score),
            team_2_score = VALUES(team_2_score),
            match_link = VALUES(match_link),
            round = VALUES(round),
            pool_id = VALUES(pool_id),
            match_date = VALUES(match_date)
    """

    connection = get_connection()
    if not connection:
        logger.error("Impossible d'obtenir une connexion à la BDD.")
        return

    data_to_insert = []
    for row in match_data_list:
        try:
            data_tuple = (
                category,
                _to_str_or_none(row.get('match_date')),
                _to_str_or_none(row.get('team_1_name')),
                _to_int_or_none(row.get('team_1_score')),
                _to_str_or_none(row.get('team_2_name')),
                _to_int_or_none(row.get('team_2_score')),
                _to_str_or_none(row.get('match_link')),
                _to_str_or_none(row.get('competition')),
                _to_str_or_none(row.get('journee'))
            )
            data_to_insert.append(data_tuple)
        except Exception:
            logger.error(f"Échec préparation ligne match : {row}", exc_info=True)
            continue

    if data_to_insert:
        _execute_batch(connection, insert_sql, data_to_insert, f"Matchs '{category}'")
    else:
        connection.close()


def db_writer_ranking(ranking_data: List[Dict], category: str):
    """Écrit le classement dans la base de données."""
    if not ranking_data:
        return

    table_name = "ranking"
    insert_sql = f"""
        INSERT INTO {table_name} 
            (pool_id, team_name, rank_number, points, matches_played, won, draws, lost, goal_diff)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            rank_number = VALUES(rank_number),
            points = VALUES(points),
            matches_played = VALUES(matches_played),
            won = VALUES(won),
            draws = VALUES(draws),
            lost = VALUES(lost),
            goal_diff = VALUES(goal_diff)
    """

    connection = get_connection()
    if not connection:
        return

    data_to_insert = []
    for row in ranking_data:
        try:
            data_tuple = (
                category,
                _to_str_or_none(row.get('team_name')),
                _to_int_or_none(row.get('rank')),
                _to_int_or_none(row.get('points')),
                _to_int_or_none(row.get('matches_played')),
                _to_int_or_none(row.get('won')),
                _to_int_or_none(row.get('draws')),
                _to_int_or_none(row.get('lost')),
                _to_int_or_none(row.get('goal_diff'))
            )
            data_to_insert.append(data_tuple)
        except Exception:
            logger.error(f"Échec préparation ligne classement : {row}", exc_info=True)
            continue

    if data_to_insert:
        _execute_batch(connection, insert_sql, data_to_insert, f"Classement '{category}'")
    else:
        connection.close()


def _execute_batch(connection, sql, data, context_name):
    """Fonction helper pour exécuter les batchs SQL."""
    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql, data)
        connection.commit()
    except Exception:
        logger.exception(f"❌ Erreur critique écriture BDD pour {context_name}")
        connection.rollback()
    finally:
        connection.close()