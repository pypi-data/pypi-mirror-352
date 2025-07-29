COMPONENT_KEY = "subject_indexer"


class Tasks:
    SINGLE = "run_subject_indexer_process"
    PIPELINE = "run_subject_indexer_with_core_logic"


class Queue:
    MAIN = "subject-indexer"


class StatusKeys:
    EXTRACT_KEYWORDS = "extract_keywords"