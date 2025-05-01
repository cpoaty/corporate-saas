# apps/core/models/fiscal_year.py
from django.db import models
import uuid
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class FiscalYear(models.Model):
    """Exercice fiscal"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, help_text="Code unique pour l'exercice (ex: FY2023)")
    start_date = models.DateField()
    end_date = models.DateField()
    
    is_closed = models.BooleanField(default=False)
    closed_date = models.DateTimeField(null=True, blank=True)
    closed_by = models.UUIDField(null=True, blank=True)  # ID de l'utilisateur
    
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False, help_text="Empêche toute modification des transactions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Exercice fiscal"
        verbose_name_plural = "Exercices fiscaux"
        ordering = ['-start_date']
        unique_together = [['tenant_id', 'code']]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validation personnalisée pour l'exercice fiscal"""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
        
        # Vérifier que les périodes ne se chevauchent pas
        overlapping = FiscalYear.objects.filter(
            tenant_id=self.tenant_id,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )
        
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError("Cet exercice chevauche un autre exercice existant.")
    
    def create_periods(self, period_type='monthly'):
        """Crée automatiquement les périodes fiscales"""
        if period_type == 'monthly':
            # Créer 12 périodes mensuelles
            current_date = self.start_date
            month = 1
            
            while current_date <= self.end_date:
                # Calculer la fin de ce mois
                next_month = current_date.replace(day=1)
                if next_month.month == 12:
                    next_month = next_month.replace(year=next_month.year + 1, month=1)
                else:
                    next_month = next_month.replace(month=next_month.month + 1)
                
                period_end = next_month - timedelta(days=1)
                
                # Ajuster si on dépasse la fin de l'exercice
                if period_end > self.end_date:
                    period_end = self.end_date
                
                # Créer la période
                FiscalPeriod.objects.create(
                    tenant_id=self.tenant_id,
                    fiscal_year=self,
                    name=f"Mois {month}",
                    code=f"{self.code}-M{month:02d}",
                    start_date=current_date,
                    end_date=period_end,
                    number=month
                )
                
                month += 1
                current_date = next_month
                
                # Si on dépasse la fin de l'exercice, on s'arrête
                if current_date > self.end_date:
                    break
                    
        elif period_type == 'quarterly':
            # Créer 4 périodes trimestrielles
            quarters = [
                {"name": "Premier trimestre", "months": 3},
                {"name": "Deuxième trimestre", "months": 3},
                {"name": "Troisième trimestre", "months": 3},
                {"name": "Quatrième trimestre", "months": 3}
            ]
            
            current_date = self.start_date
            for i, quarter in enumerate(quarters):
                # Calculer la fin de ce trimestre
                days_in_quarter = 0
                temp_date = current_date
                for m in range(quarter["months"]):
                    month_days = (temp_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                    days_in_quarter += month_days.day
                    if temp_date.month == 12:
                        temp_date = temp_date.replace(year=temp_date.year + 1, month=1)
                    else:
                        temp_date = temp_date.replace(month=temp_date.month + 1)
                
                period_end = current_date + timedelta(days=days_in_quarter - 1)
                
                # Ajuster si on dépasse la fin de l'exercice
                if period_end > self.end_date:
                    period_end = self.end_date
                
                # Créer la période
                FiscalPeriod.objects.create(
                    tenant_id=self.tenant_id,
                    fiscal_year=self,
                    name=quarter["name"],
                    code=f"{self.code}-Q{i+1}",
                    start_date=current_date,
                    end_date=period_end,
                    number=i+1
                )
                
                current_date = period_end + timedelta(days=1)
                
                # Si on dépasse la fin de l'exercice, on s'arrête
                if current_date > self.end_date:
                    break

class FiscalPeriod(models.Model):
    """Période fiscale (mois, trimestre, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(null=True, blank=True)  # ID du tenant pour isolation
    
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    
    number = models.PositiveSmallIntegerField(help_text="Numéro de la période dans l'exercice")
    is_closed = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Période fiscale"
        verbose_name_plural = "Périodes fiscales"
        ordering = ['fiscal_year', 'number']
        unique_together = [['fiscal_year', 'number']]
    
    def __str__(self):
        return f"{self.fiscal_year.name} - {self.name}"
    
    def clean(self):
        """Validation personnalisée pour la période fiscale"""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
        
        if self.fiscal_year and self.start_date and self.end_date:
            if self.start_date < self.fiscal_year.start_date:
                raise ValidationError("La date de début doit être postérieure ou égale à celle de l'exercice fiscal.")
            
            if self.end_date > self.fiscal_year.end_date:
                raise ValidationError("La date de fin doit être antérieure ou égale à celle de l'exercice fiscal.")