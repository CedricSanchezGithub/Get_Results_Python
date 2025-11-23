import os
import logging

def get_competition_via_url(driver):
    """
    Extrait la compétition de l'URL actuelle du navigateur Selenium.
    """
    url = driver.current_url
    parts = url.split('/')
    competition = parts[-4]
    return competition


def get_day_via_url(driver):
    """
    Extrait la journée de l'URL actuelle du navigateur Selenium.
    """
    url = driver.current_url
    parts = url.split('/')
    journee = parts[-2]
    return journee