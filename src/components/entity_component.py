from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity


class EntityComponent:
    owner: Optional[Entity] = None
