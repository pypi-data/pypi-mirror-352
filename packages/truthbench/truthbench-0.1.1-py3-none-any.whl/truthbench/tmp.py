from typing import List, Dict, Any

import truthbench
from truthbench import Reader


class FReader(Reader):

    def samples(self) -> List[Dict[str, Any]]:
        return [{
            "question": "Who did the United States win its independence from ?",
            "ground_truth": "Independence Day is a federal holiday in the United States celebrating the adoption of the Declaration of Independence on July 4, 1776. On this day, the Continental Congress announced that the thirteen American colonies considered themselves a new nation and were no longer under British rule."
        },
        ]


if __name__ == "__main__":
    p = truthbench.truth_pipeline()

    c, _ = p.run(FReader())

    pass
