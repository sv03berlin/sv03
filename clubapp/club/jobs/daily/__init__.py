from django_extensions.management.jobs import BaseJob


class KCSync(BaseJob):
    help = "KeyCloak Sync Job"

    def execute(self):
        print("Syncing KeyCloak")