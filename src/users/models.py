from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from billing.models import CounterAgent, Billing


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class StaffUser(AbstractBaseUser, PermissionsMixin):
    """
    Model for staff users who do data selects
    """

    email = models.EmailField(max_length=250, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    USERNAME_FIELD = 'email'

    objects = UserManager()

    @property
    def is_admin(self):
        return self.is_superuser

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.email


class ClientUser(models.Model):
    """
    Model for clients users who does payments
    """

    billing = models.ForeignKey(Billing, verbose_name=_('Биллинг'), on_delete=models.CASCADE)
    billing_userid = models.CharField(verbose_name=_('Идентификатор пользователя в системе биллинга'), max_length=250)

    class Meta:
        verbose_name = _('Плательщик')
        verbose_name_plural = _('Плательщики')
        unique_together = ('billing', 'billing_userid')

    def __str__(self):
        return _("({}) Пользователь#{}").format(self.billing, self.billing_userid)
