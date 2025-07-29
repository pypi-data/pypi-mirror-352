from tasks.functions import redact_annotation


def processor(job):
    try:
        redact_annotation(
            annotation_pk=job.workspace["annotation_pk"],
        )
    except Exception as e:
        print(f"Failed to run redact audio job: {e}")
