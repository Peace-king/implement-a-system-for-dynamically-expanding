from apscheduler.schedulers.blocking import BlockingScheduler

from ingest import update_knowledge_base


def main():
    scheduler = BlockingScheduler()

    scheduler.add_job(
        update_knowledge_base,
        trigger="interval",
        hours=24
    )

    print("Scheduler started. Updating knowledge base every 24 hours.")
    update_knowledge_base()
    scheduler.start()


if __name__ == "__main__":
    main()

