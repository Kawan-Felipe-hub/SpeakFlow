from __future__ import annotations

"""
SM-2 (Spaced Repetition) — implementação em Python puro.

Este módulo encapsula o algoritmo SM-2 de forma reutilizável e determinística.

Regras (SM-2):
- quality < 3: reinicia repetitions e interval para 0/1
- easiness_factor mínimo: 1.3
- Fórmula EF: EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
- interval: 1 → 6 → EF * interval anterior

Exemplo de uso (integrado com o model FlashCard do Django):

    from datetime import timezone
    from django.utils import timezone
    from core.models import FlashCard, ReviewLog
    from core.srs import sm2, ReviewResult

    def review(card: FlashCard, quality: int) -> ReviewResult:
        result = sm2(
            easiness_factor=card.easiness_factor,
            interval=card.interval_days,
            repetitions=card.repetitions,
            quality=quality,
        )
        card.easiness_factor = result.easiness_factor
        card.interval_days = result.interval_days
        card.repetitions = result.repetitions
        # Use o timezone-aware datetime do Django para persistir:
        card.next_review_at = timezone.now().replace(microsecond=0) + timezone.timedelta(days=result.interval_days)
        card.save(update_fields=["easiness_factor", "interval_days", "repetitions", "next_review_at", "updated_at"])

        ReviewLog.objects.create(
            flashcard=card,
            reviewed_at=timezone.now(),
            quality_score=quality,
            new_interval=result.interval_days,
        )
        return result
"""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True, slots=True)
class ReviewResult:
    interval_days: int
    easiness_factor: float
    repetitions: int
    next_review_date: date


def sm2(*, easiness_factor: float, interval: int, repetitions: int, quality: int, today: date | None = None) -> ReviewResult:
    """
    Executa uma revisão SM-2 e retorna o novo estado.

    Args:
        easiness_factor: Fator de facilidade atual (EF).
        interval: Intervalo atual em dias.
        repetitions: Quantidade de repetições bem-sucedidas acumuladas.
        quality: Qualidade do recall (0 a 5).
        today: Data base para cálculo do next_review_date (útil para testes). Default: date.today().

    Returns:
        ReviewResult com interval_days, easiness_factor, repetitions e next_review_date.

    Raises:
        ValueError: se quality não estiver entre 0 e 5, ou se interval/repetitions negativos.
    """
    if quality < 0 or quality > 5:
        raise ValueError("quality must be between 0 and 5")
    if interval < 0:
        raise ValueError("interval must be >= 0")
    if repetitions < 0:
        raise ValueError("repetitions must be >= 0")

    base_date = today or date.today()
    ef = float(easiness_factor)
    rep = int(repetitions)
    current_interval = int(interval)

    if quality < 3:
        rep = 0
        next_interval = 1
    else:
        if rep == 0:
            next_interval = 1
        elif rep == 1:
            next_interval = 6
        else:
            next_interval = int(round(current_interval * ef))
            if next_interval < 1:
                next_interval = 1
        rep += 1

    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ef < 1.3:
        ef = 1.3

    next_date = base_date + timedelta(days=next_interval)
    return ReviewResult(
        interval_days=next_interval,
        easiness_factor=float(ef),
        repetitions=rep,
        next_review_date=next_date,
    )

