"""Classes for queue."""

import logging
from copy import copy
from dataclasses import dataclass
from typing import List

from cyberfusion.QueueSupport.database import (
    Queue as QueueModel,
    QueueItem,
    make_database_session,
    QueueItemOutcome,
    QueueProcess,
)
from cyberfusion.QueueSupport.exceptions import QueueFulfillFailed
from cyberfusion.QueueSupport.interfaces import OutcomeInterface
from cyberfusion.QueueSupport.items import _Item

logger = logging.getLogger(__name__)


@dataclass
class QueueItemMapping:
    """Queue item mapping."""

    item: _Item
    database_object: QueueItem


class Queue:
    """Represents queue."""

    def __init__(self) -> None:
        """Set attributes."""
        self.item_mappings: List[QueueItemMapping] = []

        self._database_session = make_database_session()

        object_ = QueueModel()

        self._database_session.add(object_)
        self._database_session.commit()

        self.queue_database_object = object_

    def add(self, item: _Item, *, run_duplicate_last: bool = True) -> None:
        """Add item to queue."""
        deduplicated = False

        existing_item_index = next(
            (
                index
                for index, item_mapping in enumerate(self.item_mappings)
                if item_mapping.item == item
            ),
            None,
        )

        if existing_item_index is not None:
            if run_duplicate_last:
                self.item_mappings[
                    existing_item_index
                ].database_object.deduplicated = True

                self._database_session.commit()
            else:
                deduplicated = True

        item_dict = copy(item.__dict__)

        del item_dict["_reference"]
        del item_dict["_hide_outcomes"]

        object_ = QueueItem(
            queue=self.queue_database_object,
            type=item.__class__.__name__,
            reference=item.reference,
            hide_outcomes=item.hide_outcomes,
            deduplicated=deduplicated,
            attributes=item_dict,
        )

        self._database_session.add(object_)
        self._database_session.commit()

        self.item_mappings.append(QueueItemMapping(item, object_))

    def process(self, preview: bool) -> List[OutcomeInterface]:
        """Process items."""
        logger.debug("Processing items")

        process_object = QueueProcess(
            queue_id=self.queue_database_object.id,
            preview=preview,
        )

        self._database_session.add(process_object)
        self._database_session.commit()

        outcomes = []

        for item_mapping in [
            item_mapping
            for item_mapping in self.item_mappings
            if not item_mapping.database_object.deduplicated
        ]:
            logger.debug(
                "Processing item with id '%s'", item_mapping.database_object.id
            )

            if preview:
                if not item_mapping.item.hide_outcomes:
                    outcomes.extend(item_mapping.item.outcomes)
            else:
                try:
                    logger.debug(
                        "Fulfilling item with id '%s'", item_mapping.database_object.id
                    )

                    fulfill_outcomes = item_mapping.item.fulfill()

                    if not item_mapping.item.hide_outcomes:
                        outcomes.extend(fulfill_outcomes)

                    logger.debug(
                        "Fulfilled item with id '%s'", item_mapping.database_object.id
                    )
                except QueueFulfillFailed:
                    raise
                except Exception as e:
                    raise QueueFulfillFailed(
                        item_mapping.item,
                    ) from e

            for outcome in outcomes:
                outcome_object = QueueItemOutcome(
                    queue_item=item_mapping.database_object,
                    queue_process=process_object,
                    type=outcome.__class__.__name__,
                    attributes=outcome.__dict__,
                )

                self._database_session.add(outcome_object)
                self._database_session.commit()

            logger.debug("Processed item with id '%s'", item_mapping.database_object.id)

        logger.debug("Processed items")

        return outcomes
