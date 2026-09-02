from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import HistoricalStatistic
from app.services.statistics_schemas import StatisticsSummary


class HistoricalStatisticsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, summary: StatisticsSummary) -> HistoricalStatistic:
        existing = self.session.execute(
            select(HistoricalStatistic).where(
                HistoricalStatistic.event_type == summary.event_type,
                HistoricalStatistic.symbol == summary.symbol,
                HistoricalStatistic.horizon == summary.horizon,
            )
        ).scalar_one_or_none()

        if existing is None:
            statistic = HistoricalStatistic(
                event_type=summary.event_type,
                symbol=summary.symbol,
                horizon=summary.horizon,
                sample_size=summary.sample_size,
                up_count=summary.up_count,
                down_count=summary.down_count,
                up_probability=summary.up_probability,
                down_probability=summary.down_probability,
                mean_return=summary.mean_return,
                median_return=summary.median_return,
                std_return=summary.std_return,
                p10=summary.p10,
                p25=summary.p25,
                p50=summary.p50,
                p75=summary.p75,
                p90=summary.p90,
                median_mfe=summary.median_mfe,
                median_mae=summary.median_mae,
                confidence=summary.confidence.value,
            )
            self.session.add(statistic)
            return statistic

        existing.sample_size = summary.sample_size
        existing.up_count = summary.up_count
        existing.down_count = summary.down_count
        existing.up_probability = summary.up_probability
        existing.down_probability = summary.down_probability
        existing.mean_return = summary.mean_return
        existing.median_return = summary.median_return
        existing.std_return = summary.std_return
        existing.p10 = summary.p10
        existing.p25 = summary.p25
        existing.p50 = summary.p50
        existing.p75 = summary.p75
        existing.p90 = summary.p90
        existing.median_mfe = summary.median_mfe
        existing.median_mae = summary.median_mae
        existing.confidence = summary.confidence.value
        return existing

