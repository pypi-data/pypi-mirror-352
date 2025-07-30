from decimal import Decimal

from django.db import models

from wbportfolio.import_export.handlers.dividend import DividendImportHandler

from .transactions import ShareMixin, Transaction


class DividendTransaction(Transaction, ShareMixin, models.Model):
    import_export_handler_class = DividendImportHandler
    retrocession = models.FloatField(default=1)

    def save(self, *args, **kwargs):
        super().save(*args, factor=Decimal(self.retrocession), **kwargs)
