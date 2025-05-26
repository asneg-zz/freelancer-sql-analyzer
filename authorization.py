from langchain_community.cache import InMemoryCache
from langchain_gigachat.chat_models import GigaChat

# Создание глобального кэша в памяти
llm_cache = InMemoryCache()

def authorization_gigachat():
    giga = GigaChat(
        credentials="Ключ к GigaChat",
        model="GigaChat-Max",
        verify_ssl_certs=False,
        cache=llm_cache   # Передаем объект кэша в конструктор класса
    )
    return giga