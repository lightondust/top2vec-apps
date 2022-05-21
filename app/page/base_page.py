from abc import ABC, abstractmethod
from app_data import AppData
from app_url import AppURL


class BasePage(ABC):
    def __init__(self, app_data: AppData, app_url: AppURL):
        self.app_data = app_data
        self.app_url = app_url

    @abstractmethod
    def run(self):
        pass

