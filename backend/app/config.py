from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    finnhub_api_key: str = ""
    newsapi_key: str = ""
    sec_user_agent: str = "AGE-AI-Trading research@example.com"

    database_url: str = "sqlite:///./data.db"
    watchlist: str = "AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,SPY,QQQ"

    news_fetch_minutes: int = 15
    price_fetch_minutes: int = 10
    hotspot_analysis_minutes: int = 60

    cors_origins: str = "http://localhost:3000"

    @property
    def watchlist_tickers(self) -> list[str]:
        return [t.strip().upper() for t in self.watchlist.split(",") if t.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
