from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

User = get_user_model()


class MediaType(models.Model):

    """Медиа носитель"""

    name = models.CharField(max_length=100, verbose_name='Название медианосителя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Медиа носитель'
        verbose_name_plural = 'Медиа носители'


class Member(models.Model):

    """Музыкант"""

    name = models.CharField(max_length=255, verbose_name='Имя музыканта')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Музыкант'
        verbose_name_plural = 'Музыканты'


class Genre(models.Model):

    """Жанр"""

    name = models.CharField(max_length=255, verbose_name='название жанра')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Artist(models.Model):
    """Исполнитель"""

    name = models.CharField(max_length=255, verbose_name='Исполнитель/Группа')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    members = models.ManyToManyField(Member, verbose_name='Участник', related_name='artist')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


class Album(models.Model):

    """Альбом исполнителя"""

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name='Исполнитель')
    name = models.CharField(max_length=255, verbose_name='Название альбома')
    media_type = models.ForeignKey(MediaType, verbose_name='Носитель', on_delete=models.CASCADE)
    song_list = models.TextField(verbose_name='Тэеклист')
    release_date = models.DateField(verbose_name='Дата релиза')
    slug = models.SlugField()
    description = models.TextField(verbose_name='Описание', default='Описание появится позже')
    stock = models.IntegerField(default=1, verbose_name='Наличие на складе')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    offer_of_the_week = models.BooleanField(default=False, verbose_name='Предложение недели')

    def __str__(self):
        return f"{self.id} | {self.artist.name} | {self.name}"

    @property
    def ct_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'


class CartProduct(models.Model):

    """Продукт для корзины"""

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина',on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая сумма')

    def __str__(self):
        return f"Продукт: {self.content_object.name} (Для корзины)"

    def save(self,*args,**kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'


class Cart(models.Model):

    """Корзина"""

    owner = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    products = models.ManyToManyField(
        CartProduct, blank=True, null=True, related_name='related_cart', verbose_name='Продукты для корзины')
    total_products = models.IntegerField(default=0,  verbose_name='Общее кол-во товаров')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):

    """Заказ пользователя"""

    STATUS_NEW = 'new'
    STATUS_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'
    STATUS_DENIED = 'denied'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ в готов'),
        (STATUS_COMPLETED, 'Заказ в получен'),
        (STATUS_DENIED, 'Заказ в отменен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey('Customer', related_name='orders',
                                 verbose_name='Покупатель', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    address = models.CharField(max_length=1024, verbose_name='Адресс', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа',
                              choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания заказа', auto_now_add=True)
    order_date = models.DateField(verbose_name='Дата получени заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Customer(models.Model):

    """Покупатель"""

    user = models.OneToOneField(User, verbose_name='пОЛЬЗОВАТЕЛЬ', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    customer_orders = models.ManyToManyField(Order, blank=True,
                                             verbose_name='заказы покупаеля', related_name='related_customer')
    wishlist = models.ManyToManyField(Album, verbose_name='Список ожидаемого', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=1024, verbose_name='Адресс', null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Notification(models.Model):

    """Уведомления"""

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Уведомление для {self.recipient.user.username} | {self.id}"

    class Meta:
        verbose_name = 'Уведомления'
        verbose_name_plural = 'Уведомления'
