from abc import ABC, abstractmethod

class BasePublisher(ABC):
    @abstractmethod
    def publish(self, article_data: dict, featured_image_path: str) -> bool:
        pass
